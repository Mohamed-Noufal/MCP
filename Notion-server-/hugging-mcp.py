import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

response = client.responses.create(
    model="openai/gpt-oss-120b",
    input="can u acces to ?",
    tools=[
        {
            "type": "mcp",
            "server_label": "Huggingface",
            "server_url": "https://huggingface.co/mcp",
        }
    ]
)


print(response)