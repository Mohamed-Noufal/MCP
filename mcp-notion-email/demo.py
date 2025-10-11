"""
Demo script for Notion + Email MCP system.
"""
import asyncio
import sys
from groq_agent import system

async def interactive_demo():
    """Run an interactive demo with the Notion + Email system."""
    try:
        # Initialize the system
        await system.initialize()
        
        print("\n" + "="*60)
        print("🚀 NOTION + EMAIL MCP SYSTEM")
        print("="*60)
        print("Available Servers:")
        print("• Notion - Read/write pages, search, databases")
        print("• Email - Send emails, read inbox, manage messages")
        print("\nExample Commands:")
        print("- 'Check my unread emails and summarize them'")
        print("- 'Create a Notion page for my meeting notes'") 
        print("- 'Send email to john@example.com about the project'")
        print("- 'Search my Notion for project documents'")
        print("\nSystem Commands:")
        print("- 'quit' to exit")
        print("- 'clear' to clear conversation")
        print("- 'tools' to list available tools")
        print("="*60)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'clear':
                    system.clear_conversation()
                    continue
                elif user_input.lower() == 'tools':
                    all_tools = await system.mcp_manager.list_all_tools()
                    print("\n🔧 Available Tools:", file=sys.stderr)
                    for server, tools in all_tools.items():
                        print(f"\n{server.upper()}:", file=sys.stderr)
                        for tool in tools:
                            print(f"  • {tool['name']}: {tool['description']}", file=sys.stderr)
                    continue
                elif not user_input:
                    continue
                
                print("🔄 Processing...", file=sys.stderr)
                response = await system.process_message(user_input)
                print(f"\n🤖 Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}", file=sys.stderr)
                
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}", file=sys.stderr)
    finally:
        await system.close()

async def quick_demo():
    """Run a quick automated demo."""
    print("🚀 Running Notion + Email demo...", file=sys.stderr)
    
    try:
        await system.initialize()
        
        # Demo 1: Check emails
        print("\n1. Checking emails...", file=sys.stderr)
        response1 = await system.process_message("Check my unread emails and give me a summary")
        print(f"📧 Email check: {response1}", file=sys.stderr)
        
        # Demo 2: Notion operations
        if system.mcp_manager.sessions.get('notion'):
            print("\n2. Testing Notion...", file=sys.stderr)
            response2 = await system.process_message("Search for pages in my Notion workspace")
            print(f"📚 Notion search: {response2}", file=sys.stderr)
        
        # Demo 3: Combined operation
        print("\n3. Testing combined operation...", file=sys.stderr)
        response3 = await system.process_message("Check for urgent emails and create a Notion page for any important ones")
        print(f"🔄 Combined operation: {response3}", file=sys.stderr)
        
        print("\n✅ Demo completed!", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}", file=sys.stderr)
    finally:
        await system.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        asyncio.run(quick_demo())
    else:
        asyncio.run(interactive_demo())