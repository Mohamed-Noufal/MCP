import os
import json
import asyncio
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleNotionAgent:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.conversation_history = []
        
    def process_message(self, user_message: str) -> str:
        """
        Simple message processing without complex MCP client setup
        For first-time learning, we'll simulate the tool calling
        """
        
        # Create a context about what tools are available
        tools_context = """
        Available Notion Tools:
        - search_pages(query): Search pages in Notion workspace
        - get_page(page_id): Get content of a specific page
        - create_page(parent_id, title, content): Create new page
        - query_database(database_id): Query a database
        """
        
        prompt = f"""
        {tools_context}
        
        User Request: {user_message}
        
        Based on the user's request, suggest which Notion tool(s) would be appropriate.
        Also provide example parameters they might use.
        
        Format your response as:
        SUGGESTED TOOLS: [tool names]
        PARAMETERS: [example parameters]
        EXPLANATION: [brief explanation]
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat_loop(self):
        """Simple interactive chat loop"""
        print("🤖 Simple Notion Agent Started!")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif not user_input:
                    continue
                
                print("Thinking...")
                response = self.process_message(user_input)
                print(f"\nAssistant: {response}\n")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    agent = SimpleNotionAgent()
    agent.chat_loop()