"""
MCP Manager for Notion and Email servers only.
"""
import asyncio
import subprocess
import sys
from mcp.client import create_session, stdio_client
from mcp.client.stdio import stdio_client
import os
from config import config

class MCPServerManager:
    """Manages Notion and Email MCP server connections."""
    
    def __init__(self):
        self.servers = {}
        self.sessions = {}
        
    async def start_server(self, server_name: str, server_config: dict):
        """Start an MCP server and establish connection."""
        try:
            print(f"🚀 Starting {server_name} server...", file=sys.stderr)
            
            # Prepare environment
            env = os.environ.copy()
            if 'env' in server_config:
                env.update(server_config['env'])
            
            # Create server command
            command = [server_config['command']] + server_config['args']
            
            # Start the server process
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Create stdio transport
            stdio_transport = await stdio_client(process)
            stdio, write = stdio_transport
            
            # Create session
            session = await create_session(stdio, write)
            await session.initialize()
            
            # Store the session and process
            self.servers[server_name] = process
            self.sessions[server_name] = session
            
            # List available tools
            tools_response = await session.list_tools()
            tools = [tool.name for tool in tools_response.tools]
            
            print(f"✅ {server_name} server connected successfully!", file=sys.stderr)
            print(f"   Available tools: {', '.join(tools)}", file=sys.stderr)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {server_name} server: {e}", file=sys.stderr)
            return False
    
    async def start_all_servers(self):
        """Start both Notion and Email servers."""
        tasks = []
        for server_name, server_config in config.MCP_SERVERS.items():
            # Skip servers without required environment variables
            if server_name == "notion" and not os.getenv("NOTION_API_KEY"):
                print(f"⚠️  Skipping {server_name} - NOTION_API_KEY not set", file=sys.stderr)
                continue
            if server_name == "email" and not os.getenv("EMAIL_ADDRESS"):
                print(f"⚠️  Skipping {server_name} - EMAIL_ADDRESS not set", file=sys.stderr)
                continue
                
            task = self.start_server(server_name, server_config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return all(results)
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        """Call a tool on a specific MCP server."""
        if server_name not in self.sessions:
            raise ValueError(f"Server {server_name} not connected")
        
        try:
            result = await self.sessions[server_name].call_tool(tool_name, arguments)
            return result
        except Exception as e:
            print(f"❌ Error calling {tool_name} on {server_name}: {e}", file=sys.stderr)
            raise
    
    async def list_all_tools(self):
        """List all available tools from both servers."""
        all_tools = {}
        for server_name, session in self.sessions.items():
            try:
                tools_response = await session.list_tools()
                all_tools[server_name] = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools_response.tools
                ]
            except Exception as e:
                print(f"❌ Error listing tools for {server_name}: {e}", file=sys.stderr)
                all_tools[server_name] = []
        
        return all_tools
    
    async def close_all(self):
        """Close all server connections."""
        for server_name, session in self.sessions.items():
            try:
                await session.close()
            except Exception as e:
                print(f"Error closing {server_name}: {e}", file=sys.stderr)
        
        for server_name, process in self.servers.items():
            try:
                process.terminate()
                await process.wait()
            except Exception as e:
                print(f"Error terminating {server_name}: {e}", file=sys.stderr)

# Singleton instance
mcp_manager = MCPServerManager()