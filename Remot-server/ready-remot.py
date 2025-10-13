import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

response = client.responses.create(
    model="llama-3.3-70b-versatile",
    input="what tools are avilable for you ",
    tools=[
        {
            "type": "mcp",
            "server_label": "Notion",
            "server_url": "https://mcp.notion.com/mcp",
            "authorization": {
            "type": "bearer",
            "token": os.environ.get("NOTION_API_KEY")
        }
        }
    ]
)


if __name__ == "__main__":
    print(response)