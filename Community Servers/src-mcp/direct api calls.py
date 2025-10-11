import os
import json
from groq import Groq
from notion_client import Client
from dotenv import load_dotenv
load_dotenv()

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


if __name__ == "__main__":
    main()