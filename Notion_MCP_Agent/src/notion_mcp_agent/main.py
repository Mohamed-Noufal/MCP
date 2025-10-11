import asyncio
import json
import os
import sys
import uuid
from textwrap import dedent
from agno.agent import Agent
from agno.models.groq import Groq  # ✅ Groq model
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


# Try importing the memory module (may not exist in 2.1.3)
try:
    from agno.memory.v2 import Memory
except ImportError:
    try:
        from agno.memory import Memory
        print("⚠️ Using legacy agno.memory module (v1).")
    except ImportError:
        Memory = None
        print("⚠️ No memory module found in agno. Continuing without memory support.")

# Load environment variables
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


async def main():
    print("\n========================================")
    print("      Notion MCP Agent (Groq)")
    print("========================================\n")

    # Get Notion Page ID
    if len(sys.argv) > 1:
        page_id = sys.argv[1]
        print(f"Using provided page ID: {page_id}")
    else:
        page_id = input("Enter your Notion page ID: ").strip()

    user_id = f"user_{uuid.uuid4().hex[:8]}"
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}\n")

    print("Connecting to Notion MCP server...\n")

    # Configure MCP connection
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@notionhq/notion-mcp-server"],
        env={
            "OPENAPI_MCP_HEADERS": json.dumps(
                {
                    "Authorization": f"Bearer {NOTION_TOKEN}",
                    "Notion-Version": "2022-06-28",
                }
            )
        },
    )

    # Connect MCP Tools
    async with MCPTools(server_params=server_params) as mcp_tools:
        print("✅ Connected to Notion MCP server!")

        # Create the agent with Groq LLM
        agent = Agent(
            name="NotionGroqAgent",
            model=Groq(id="llama-3.3-70b-versatile"),
            tools=[mcp_tools],
            description="Agent to query and modify Notion docs via MCP using Groq Llama 3.3.",
            instructions=dedent(
                f"""
                You are an expert Notion assistant that helps users interact with their Notion pages.

                IMPORTANT INSTRUCTIONS:
                1. You have direct access to Notion documents through MCP tools - make full use of them.
                2. ALWAYS use the page ID: {page_id} for all operations unless the user explicitly provides another ID.
                3. When asked to update, read, or search pages, ALWAYS use the appropriate MCP tool calls.
                4. Be proactive in suggesting actions users can take with their Notion documents.
                5. When making changes, explain what you did and confirm the changes were made.
                6. If a tool call fails, explain the issue and suggest alternatives.

                Example tasks you can help with:
                - Reading page content
                - Searching for specific information
                - Adding new content or updating existing content
                - Creating lists, tables, and other Notion blocks
                - Explaining page structure
                - Adding comments to specific blocks

                The user's current page ID is: {page_id}
                """
            ),
            markdown=True,
            retries=3,
            add_history_to_context=True,
            num_history_runs=5,
        )

        print("\n🤖 Notion MCP Agent is ready! Type 'exit' to quit.\n")

        await agent.acli_app(
            user_id=user_id,
            session_id=session_id,
            user="You",
            emoji="✨",
            stream=True,
            markdown=True,
            exit_on=["exit", "quit", "bye"],
        )


if __name__ == "__main__":
    asyncio.run(main())
