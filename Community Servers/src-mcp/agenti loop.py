import os
import json
from groq import Groq
from notion_client import Client
from dotenv import load_dotenv
load_dotenv()
# ============================================
# APPROACH 3: Agent Loop (Most Powerful)
# ============================================
# Build an agent that can make multiple tool calls

def approach_3_agent_loop():
    """
    Agent loop: Multi-step reasoning with tools
    ✅ Most powerful
    ✅ Can make multiple calls
    ✅ Complex workflows
    """
    print("\n" + "="*60)
    print("APPROACH 3: Agent Loop (Most Powerful)")
    print("="*60)
    
    notion = Client(auth=os.getenv("NOTION_API_KEY"))
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Define available tools
    def search_notion(query: str) -> dict:
        """Search Notion workspace"""
        print(f"   🔍 Searching Notion: {query}")
        results = notion.search(
            query=query,
            filter={"property": "object", "value": "page"}
        )
        return results.get("results", [])[:3]
    
    def read_page(page_id: str) -> str:
        """Read page content"""
        print(f"   📖 Reading page: {page_id}")
        blocks = notion.blocks.children.list(block_id=page_id)
        
        content = []
        for block in blocks.get("results", []):
            block_type = block["type"]
            if block_type in ["paragraph", "bulleted_list_item"]:
                rich_text = block.get(block_type, {}).get("rich_text", [])
                if rich_text:
                    content.append(rich_text[0].get("plain_text", ""))
        
        return "\n".join(content)
    
    def create_page(title: str, content: str) -> dict:
        """Create new Notion page"""
        print(f"   ✍️ Creating page: {title}")
        # Find a parent page
        pages = notion.search(filter={"property": "object", "value": "page"})
        if not pages.get("results"):
            return {"error": "No parent page found"}
        
        parent_id = pages["results"][0]["id"]
        
        new_page = notion.pages.create(
            parent={"page_id": parent_id},
            properties={
                "title": [{"text": {"content": title}}]
            },
            children=[{
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": content}}]
                }
            }]
        )
        return new_page
    
    # Tool registry
    available_tools = {
        "search_notion": search_notion,
        "read_page": read_page,
        "create_page": create_page
    }
    
    # Tool definitions for Groq
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_notion",
                "description": "Search for pages in Notion",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_page",
                "description": "Read content from a page",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page_id": {"type": "string", "description": "Page ID"}
                    },
                    "required": ["page_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_page",
                "description": "Create a new Notion page",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Page title"},
                        "content": {"type": "string", "description": "Page content"}
                    },
                    "required": ["title", "content"]
                }
            }
        }
    ]
    
    # Agent loop
    messages = [{
        "role": "user",
        "content": "Find my 'Project Roadmap' page, read it, summarize the tasks, and create a new page called 'Task Summary' with the summary."
    }]
    
    max_iterations = 5
    for iteration in range(max_iterations):
        print(f"\n🔄 Agent Iteration {iteration + 1}")
        
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1000
        )
        
        response_message = response.choices[0].message
        
        # Check if done
        if not response_message.tool_calls:
            print(f"\n✅ Agent finished!")
            print(f"Final response: {response_message.content}")
            return response_message.content
        
        # Execute tool calls
        messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Call the actual function
            function_to_call = available_tools[function_name]
            function_response = function_to_call(**function_args)
            
            # Add to messages
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response, default=str),
            })
    
    return "Max iterations reached"


# ============================================
# MAIN: Choose Your Approach
# ============================================

def main():
    print("\n" + "="*60)
    print("🚀 Groq + Notion Integration - Working Examples")
    print("="*60)
    
    # Check environment
    if not os.getenv("NOTION_API_KEY"):
        print("\n❌ NOTION_API_KEY not set!")
        print("   Set it: export NOTION_API_KEY='secret_...'")
        return
    
    if not os.getenv("GROQ_API_KEY"):
        print("\n❌ GROQ_API_KEY not set!")
        print("   Set it: export GROQ_API_KEY='gsk_...'")
        return
    
    print("\nChoose an approach:")
    print("1. Direct Integration (Simplest - Recommended)")
    print("2. Function Calling (Smart)")
    print("3. Agent Loop (Most Powerful)")
    
    choice = input("\nEnter 1, 2, or 3: ").strip()
    
    if choice == "1":
        approach_1_direct_integration()
    elif choice == "2":
        approach_2_function_calling()
    elif choice == "3":
        approach_3_agent_loop()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()