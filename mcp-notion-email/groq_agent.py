"""
AI Agent using Groq LLM with Notion and Email MCP servers.
"""
import asyncio
import json
from groq import Groq
from mcp_manager import mcp_manager
from config import config
import sys

class GroqNotionEmailSystem:
    """
    Complete AI system using Groq LLM with Notion and Email MCP servers.
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=config.GROQ_API_KEY)
        self.conversation_history = []
        
    async def initialize(self):
        """Initialize the system and connect to MCP servers."""
        print("🤖 Initializing Groq Notion + Email System...", file=sys.stderr)
        
        # Validate configuration
        config.validate_config()
        
        # Start all MCP servers
        success = await mcp_manager.start_all_servers()
        if not success:
            print("⚠️  Some servers failed to start, but continuing...", file=sys.stderr)
        
        # List all available tools
        all_tools = await mcp_manager.list_all_tools()
        total_tools = sum(len(tools) for tools in all_tools.values())
        
        print(f"✅ System ready! Available tools: {total_tools} tools across {len(all_tools)} servers", file=sys.stderr)
        for server, tools in all_tools.items():
            print(f"   {server}: {len(tools)} tools", file=sys.stderr)
            
            # Print specific tools for each server
            for tool in tools:
                print(f"     • {tool['name']}: {tool['description']}", file=sys.stderr)
        
        return True
    
    def _create_tool_schemas(self, all_tools):
        """Convert MCP tools to Groq-compatible tool schemas."""
        tool_schemas = []
        
        for server_name, tools in all_tools.items():
            for tool in tools:
                tool_schemas.append({
                    "type": "function",
                    "function": {
                        "name": f"{server_name}_{tool['name']}",
                        "description": f"{tool['description']} (Server: {server_name})",
                        "parameters": tool['inputSchema']
                    }
                })
        
        return tool_schemas
    
    async def process_message(self, user_message: str) -> str:
        """
        Process user message using Groq LLM and available MCP tools.
        
        Args:
            user_message: User's input message
            
        Returns:
            AI response with tool results
        """
        try:
            # Get all available tools
            all_tools = await mcp_manager.list_all_tools()
            tool_schemas = self._create_tool_schemas(all_tools)
            
            # Add user message to conversation
            self.conversation_history.append({"role": "user", "content": user_message})
            
            print(f"🔄 Processing with {len(tool_schemas)} available tools...", file=sys.stderr)
            
            # Initial LLM call
            response = self.groq_client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=self.conversation_history,
                tools=tool_schemas,
                tool_choice="auto",
            )
            
            response_message = response.choices[0].message
            self.conversation_history.append(response_message)
            
            # Check if LLM wants to use tools
            if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                tool_results = []
                
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Parse server and tool name (format: "server_tool")
                    if "_" in tool_name:
                        server_name, actual_tool_name = tool_name.split("_", 1)
                    else:
                        # Fallback: try to find the tool in any server
                        server_name = None
                        actual_tool_name = tool_name
                        for s_name, tools in all_tools.items():
                            if any(t['name'] == tool_name for t in tools):
                                server_name = s_name
                                break
                    
                    if not server_name:
                        error_msg = f"Could not find server for tool: {tool_name}"
                        print(f"❌ {error_msg}", file=sys.stderr)
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "output": error_msg
                        })
                        continue
                    
                    print(f"🛠️  Calling {server_name}.{actual_tool_name}...", file=sys.stderr)
                    
                    try:
                        # Call the tool
                        result = await mcp_manager.call_tool(server_name, actual_tool_name, tool_args)
                        output = result.content if hasattr(result, 'content') else str(result)
                        
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "output": output
                        })
                        
                        print(f"✅ {server_name}.{actual_tool_name} completed", file=sys.stderr)
                        
                    except Exception as e:
                        error_msg = f"Error calling {server_name}.{actual_tool_name}: {str(e)}"
                        print(f"❌ {error_msg}", file=sys.stderr)
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "output": error_msg
                        })
                
                # Add tool results to conversation
                for result in tool_results:
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": result["tool_call_id"],
                        "content": result["output"]
                    })
                
                # Get final response with tool results
                final_response = self.groq_client.chat.completions.create(
                    model=config.GROQ_MODEL,
                    messages=self.conversation_history,
                )
                
                final_message = final_response.choices[0].message.content
                self.conversation_history.append({"role": "assistant", "content": final_message})
                
                return final_message
            else:
                # No tools needed
                self.conversation_history.append({"role": "assistant", "content": response_message.content})
                return response_message.content
                
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            print(f"❌ {error_msg}", file=sys.stderr)
            return error_msg
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("🗑️  Conversation cleared", file=sys.stderr)
    
    async def close(self):
        """Clean up resources."""
        await mcp_manager.close_all()
        print("👋 All MCP servers closed", file=sys.stderr)

# Global system instance
system = GroqNotionEmailSystem()