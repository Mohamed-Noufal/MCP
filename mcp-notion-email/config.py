import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration for Notion and Email MCP servers."""
    
    # Groq Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama-3.3-70b-versatile"
    
    # MCP Server Configurations
    MCP_SERVERS = {
        "notion": {
            "command": "npx",
            "args": ["@modelcontextprotocol/server-notion"],
            "env": {
                "NOTION_API_KEY": os.getenv("NOTION_API_KEY")
            }
        },
        "email": {
            "command": "npx",
            "args": ["mcp-server-gmail"],
            "env": {
                "GMAIL_ADDRESS": os.getenv("EMAIL_ADDRESS"),
                "GMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD")
            }
        }
    }
    
    @classmethod
    def validate_config(cls):
        """Validate that required environment variables are set."""
        missing = []
        if not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        if not os.getenv("NOTION_API_KEY"):
            missing.append("NOTION_API_KEY")
        if not os.getenv("EMAIL_ADDRESS"):
            missing.append("EMAIL_ADDRESS")
        if not os.getenv("EMAIL_PASSWORD"):
            missing.append("EMAIL_PASSWORD")
        
        if missing:
            print(f"⚠️  Missing environment variables: {', '.join(missing)}")
            print("Some MCP servers may not work properly.")
        
        return len(missing) == 0

# Global config instance
config = Config()