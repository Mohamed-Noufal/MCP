# ============================================
# APPROACH 2: Function Calling (More Advanced)
# ============================================
# Use Groq's function calling to let the model decide when to use Notion

import os
import json
from groq import Groq
from notion_client import Client
from dotenv import load_dotenv
load_dotenv()

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


if __name__ == "__main__":
    main()