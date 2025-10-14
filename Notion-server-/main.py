import asyncio
import json
import os
import uuid
from textwrap import dedent
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_API_KEY")

async def main():
    print("\n========================================")
    print("   🌐 Notion Workspace MCP Agent (Groq)")
    print("========================================\n")

    # Prepare MCP connection
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@notionhq/notion-mcp-server"],
        env={
            "OPENAPI_MCP_HEADERS": json.dumps({
                "Authorization": f"Bearer {NOTION_TOKEN}",
                "Notion-Version": "2022-06-28",
            })
        },
    )

    async with MCPTools(server_params=server_params) as mcp_tools:
        print("✅ Connected to Notion MCP server!")

        agent = Agent(
            name="NotionWorkspaceAgent",
            model=Groq(id="llama-3.3-70b-versatile"),
            tools=[mcp_tools],
            description="Workspace-wide Notion agent via MCP using Groq Llama 3.3.",
            instructions=dedent("""
                You are an expert assistant for Notion workspaces.

                You can:
                - Search for pages, databases, or blocks
                - Read and summarize any page you find
                - Add new pages or content blocks
                - Update text or tasks in any document
                - Explain how a page is structured

                When users mention a page (e.g., 'Project Plan' or 'Meeting Notes'),
                use MCP's search tools to locate it first, then interact with it.

                Always confirm before making edits, and describe what you changed.
            """),
            markdown=True,
            retries=3,
            add_history_to_context=True,
            num_history_runs=5,
        )

        print("\n🤖 Agent is ready! Type 'exit' to quit.\n")

        await agent.acli_app(
            user_id=f"user_{uuid.uuid4().hex[:8]}",
            session_id=f"session_{uuid.uuid4().hex[:8]}",
            user="You",
            emoji="✨",
            stream=True,
            markdown=True,
            exit_on=["exit", "quit", "bye"],
        )

if __name__ == "__main__":
    asyncio.run(main())
