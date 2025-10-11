#!/usr/bin/env python3
"""
CORRECT WAY: Groq + Notion Integration
Three working approaches that actually work!
"""

import os
import json
from groq import Groq
from notion_client import Client

# ============================================
# APPROACH 1: Direct Integration (Simplest)
# ============================================
# Use Notion SDK + Groq SDK directly
# This is the most straightforward and reliable

def approach_1_direct_integration():
    """
    Direct integration: Use both APIs directly
    ✅ Works immediately
    ✅ Full control
    ✅ No complex setup
    """
    print("\n" + "="*60)
    print("APPROACH 1: Direct Integration (Recommended)")
    print("="*60)
    
    # Initialize clients
    notion = Client(auth=os.getenv("NOTION_API_KEY"))
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Example: Search Notion for a page
    print("\n1️⃣ Searching Notion for 'Project Roadmap'...")
    search_results = notion.search(
        query="Project Roadmap",
        filter={"property": "object", "value": "page"}
    )
    
    if not search_results.get("results"):
        print("❌ Page not found")
        return
    
    page_id = search_results["results"][0]["id"]
    print(f"✅ Found page: {page_id}")
    
    # Get page content
    print("\n2️⃣ Reading page content...")
    blocks = notion.blocks.children.list(block_id=page_id)
    
    # Extract text content
    content_parts = []
    for block in blocks.get("results", []):
        block_type = block["type"]
        if block_type in ["paragraph", "bulleted_list_item", "numbered_list_item"]:
            rich_text = block.get(block_type, {}).get("rich_text", [])
            if rich_text:
                content_parts.append(rich_text[0].get("plain_text", ""))
    
    page_content = "\n".join(content_parts)
    print(f"✅ Retrieved {len(content_parts)} blocks")
    
    # Use Groq to analyze
    print("\n3️⃣ Processing with Groq...")
    completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that analyzes Notion content."
            },
            {
                "role": "user",
                "content": f"Summarize the next three tasks from this content:\n\n{page_content}"
            }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=500
    )
    
    result = completion.choices[0].message.content
    print(f"\n✨ Groq Analysis:\n{result}")
    
    return result


# ============================================
# APPROACH 2: Function Calling (More Advanced)
# ============================================
# Use Groq's function calling to let the model decide when to use Notion

def approach_2_function_calling():
    """
    Function calling: Let Groq decide when to call Notion
    ✅ More intelligent
    ✅ Groq chooses when to use tools
    ✅ Standard Groq feature
    """
    print("\n" + "="*60)
    print("APPROACH 2: Function Calling (Smart)")
    print("="*60)
    
    notion = Client(auth=os.getenv("NOTION_API_KEY"))
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Define Notion functions for Groq
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_notion",
                "description": "Search for pages in Notion workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for Notion pages"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_notion_page",
                "description": "Read content from a Notion page",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "The ID of the Notion page"
                        }
                    },
                    "required": ["page_id"]
                }
            }
        }
    ]
    
    # Initial request
    messages = [
        {
            "role": "user",
            "content": "Find the page titled 'Project Roadmap' in my Notion and summarize the next three tasks."
        }
    ]
    
    print("\n1️⃣ Sending request to Groq...")
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # Let model decide
        max_tokens=1000
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # Process tool calls
    if tool_calls:
        print(f"\n2️⃣ Groq wants to call: {tool_calls[0].function.name}")
        
        messages.append(response_message)
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute the function
            if function_name == "search_notion":
                print(f"   Searching for: {function_args['query']}")
                result = notion.search(
                    query=function_args["query"],
                    filter={"property": "object", "value": "page"}
                )
                function_response = json.dumps(result.get("results", [])[:1])
                
            elif function_name == "read_notion_page":
                print(f"   Reading page: {function_args['page_id']}")
                blocks = notion.blocks.children.list(
                    block_id=function_args["page_id"]
                )
                function_response = json.dumps(blocks.get("results", []))
            
            # Add function response to messages
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })
        
        # Get final response
        print("\n3️⃣ Getting final analysis...")
        second_response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1000
        )
        
        result = second_response.choices[0].message.content
        print(f"\n✨ Final Result:\n{result}")
        
        return result


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