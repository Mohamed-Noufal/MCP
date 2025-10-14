import asyncio
import json
import os
import sys
import uuid
from textwrap import dedent
from typing import Optional
from pathlib import Path

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters
from dotenv import load_dotenv
import warnings

# Suppress runtime warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Load environment variables
load_dotenv()


class GoogleMCPConfig:
    """Configuration manager for Google MCP server"""
    
    def __init__(self):
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
    def validate(self) -> tuple[bool, str]:
        """Validate configuration"""
        if not self.credentials_path and not self.api_key:
            return False, "Either GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_API_KEY must be set"
        
        if self.credentials_path and not Path(self.credentials_path).exists():
            return False, f"Credentials file not found: {self.credentials_path}"
        
        return True, "Configuration valid"


async def create_google_mcp_connection(config: GoogleMCPConfig) -> StdioServerParameters:
    """
    Create MCP server parameters for Google Workspace
    
    Best Practice: Separate connection logic for better testability and reusability
    """
    env_vars = {}
    
    # Add credentials to environment
    if config.credentials_path:
        env_vars["GOOGLE_APPLICATION_CREDENTIALS"] = config.credentials_path
    
    if config.api_key:
        env_vars["GOOGLE_API_KEY"] = config.api_key
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-gdrive"  # Official Google Drive MCP server
        ],
        env=env_vars,
    )
    
    return server_params


async def initialize_agent(mcp_tools: MCPTools) -> Agent:
    """
    Initialize the Google Workspace agent
    
    Best Practice: Separate agent initialization for better configuration management
    """
    agent = Agent(
        name="GoogleWorkspaceAgent",
        model=Groq(id="llama-3.3-70b-versatile"),
        tools=[mcp_tools],
        description="Google Docs and Sheets assistant via MCP using Groq Llama 3.3",
        instructions=dedent("""
            You are an expert assistant for Google Workspace (Docs and Sheets).

            **Core Capabilities:**
            - Search for documents and spreadsheets in Google Drive
            - Read and summarize Google Docs content
            - Analyze and explain spreadsheet data
            - Create new documents or sheets
            - Update existing content (text, formulas, data)
            - Export documents in various formats

            **Workflow Guidelines:**
            1. When users mention a document, ALWAYS search for it first using Drive search
            2. Confirm document identity before performing operations
            3. For spreadsheets, ask about specific sheets/ranges if needed
            4. Always preview changes before applying them
            5. Provide clear confirmation of completed actions

            **Best Practices:**
            - Use descriptive names when creating new files
            - Summarize long documents rather than dumping full content
            - For spreadsheets, present data in readable tables
            - Explain formulas in plain English
            - Handle errors gracefully and suggest alternatives

            **Security:**
            - Never expose sensitive data unnecessarily
            - Confirm before making destructive changes
            - Respect file permissions
        """),
        markdown=True,
        retries=3,
        add_history_to_context=True,
        num_history_runs=5,
        show_tool_calls=True,  # Best Practice: Show tool calls for transparency
        debug_mode=False,  # Set to True for development
    )
    
    return agent


async def run_interactive_session(agent: Agent):
    """
    Run interactive CLI session
    
    Best Practice: Separate session logic for better error handling
    """
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    print(f"\n📋 Session Info:")
    print(f"   User ID: {user_id}")
    print(f"   Session ID: {session_id}\n")
    
    try:
        await agent.acli_app(
            user_id=user_id,
            session_id=session_id,
            user="You",
            emoji="📄",
            stream=True,
            markdown=True,
            exit_on=["exit", "quit", "bye", "goodbye"],
        )
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error during session: {str(e)}")
        raise


async def main():
    """Main entry point with comprehensive error handling"""
    
    print("\n" + "=" * 50)
    print("   📄 Google Docs & Sheets MCP Agent (Groq)")
    print("=" * 50 + "\n")
    
    # Initialize configuration
    config = GoogleMCPConfig()
    is_valid, message = config.validate()
    
    if not is_valid:
        print(f"❌ Configuration Error: {message}")
        print("\n💡 Setup Instructions:")
        print("   1. Create a Google Cloud project")
        print("   2. Enable Google Drive, Docs, and Sheets APIs")
        print("   3. Create OAuth 2.0 credentials or Service Account")
        print("   4. Download credentials JSON file")
        print("   5. Set environment variable:")
        print("      export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json")
        print("\n   Or use API key:")
        print("      export GOOGLE_API_KEY=your_api_key_here\n")
        sys.exit(1)
    
    print("✅ Configuration validated")
    
    # Create MCP connection
    try:
        server_params = await create_google_mcp_connection(config)
        print("🔧 MCP server parameters created")
    except Exception as e:
        print(f"❌ Failed to create server parameters: {str(e)}")
        sys.exit(1)
    
    # Connect to MCP server
    try:
        async with MCPTools(server_params=server_params) as mcp_tools:
            print("✅ Connected to Google Drive MCP server!")
            
            # List available tools
            available_tools = await mcp_tools.list_tools()
            print(f"🔧 Available tools: {len(available_tools)}")
            
            # Initialize agent
            agent = await initialize_agent(mcp_tools)
            print("🤖 Agent initialized successfully!\n")
            
            # Print usage examples
            print("💡 Example queries:")
            print("   • 'Find my project proposal document'")
            print("   • 'Create a new spreadsheet for Q1 budget'")
            print("   • 'Summarize the meeting notes from last week'")
            print("   • 'Add a new section to my report about AI trends'")
            print("   • 'Show me the data from Sales sheet, rows 1-10'")
            print("\n" + "-" * 50)
            print("Type 'exit' to quit\n")
            
            # Run interactive session
            await run_interactive_session(agent)
            
    except ConnectionError as e:
        print(f"❌ Connection Error: {str(e)}")
        print("   Make sure the MCP server package is installed:")
        print("   npm install -g @modelcontextprotocol/server-gdrive")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("\n👋 Session ended. Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Application terminated by user.")
        sys.exit(0)