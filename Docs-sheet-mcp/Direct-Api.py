"""
Google Docs & Sheets Agent using Direct Google APIs
Works without deprecated MCP server
"""

import asyncio
import os
from textwrap import dedent
from typing import List, Dict, Any

from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment
load_dotenv()

# Google API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]


class GoogleWorkspaceTools:
    """Direct Google Workspace API integration"""
    
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.credentials = None
        self.drive_service = None
        self.docs_service = None
        self.sheets_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google API services"""
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=SCOPES
            )
            
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            self.docs_service = build('docs', 'v1', credentials=self.credentials)
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
            
            print("✅ Google API services initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Google services: {e}")
            raise
    
    def search_files(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for files in Google Drive"""
        try:
            results = self.drive_service.files().list(
                q=f"name contains '{query}' and trashed=false",
                spaces='drive',
                fields='files(id, name, mimeType, createdTime, modifiedTime)',
                pageSize=max_results
            ).execute()
            
            files = results.get('files', [])
            return files
        except HttpError as e:
            return [{"error": f"Search failed: {e}"}]
    
    def read_document(self, document_id: str) -> Dict[str, Any]:
        """Read a Google Doc"""
        try:
            doc = self.docs_service.documents().get(documentId=document_id).execute()
            
            # Extract text content
            content = []
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for text_run in element['paragraph'].get('elements', []):
                        if 'textRun' in text_run:
                            content.append(text_run['textRun']['content'])
            
            return {
                "title": doc.get('title'),
                "document_id": document_id,
                "content": ''.join(content),
                "revision_id": doc.get('revisionId')
            }
        except HttpError as e:
            return {"error": f"Failed to read document: {e}"}
    
    def read_spreadsheet(self, spreadsheet_id: str, range_name: str = "A1:Z100") -> Dict[str, Any]:
        """Read a Google Sheet"""
        try:
            sheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            values = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            return {
                "title": sheet.get('properties', {}).get('title'),
                "spreadsheet_id": spreadsheet_id,
                "data": values.get('values', []),
                "range": range_name
            }
        except HttpError as e:
            return {"error": f"Failed to read spreadsheet: {e}"}
    
    def list_my_files(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """List recent files"""
        try:
            results = self.drive_service.files().list(
                spaces='drive',
                fields='files(id, name, mimeType, createdTime, modifiedTime, webViewLink)',
                orderBy='modifiedTime desc',
                pageSize=max_results
            ).execute()
            
            return results.get('files', [])
        except HttpError as e:
            return [{"error": f"Failed to list files: {e}"}]


def create_tool_functions(google_tools: GoogleWorkspaceTools):
    """Create tool functions for the agent"""
    
    def search_google_drive(query: str) -> str:
        """
        Search for files in Google Drive.
        
        Args:
            query: Search query (file name or content)
        
        Returns:
            List of matching files with their IDs and types
        """
        files = google_tools.search_files(query)
        
        if not files:
            return f"No files found matching '{query}'"
        
        result = f"Found {len(files)} file(s):\n\n"
        for i, file in enumerate(files, 1):
            result += f"{i}. **{file['name']}**\n"
            result += f"   - ID: `{file['id']}`\n"
            result += f"   - Type: {file['mimeType'].split('.')[-1]}\n"
            result += f"   - Modified: {file.get('modifiedTime', 'N/A')}\n\n"
        
        return result
    
    def read_google_doc(document_id: str) -> str:
        """
        Read content from a Google Doc.
        
        Args:
            document_id: The ID of the document to read
        
        Returns:
            Document content as text
        """
        doc = google_tools.read_document(document_id)
        
        if "error" in doc:
            return f"Error: {doc['error']}"
        
        result = f"# {doc['title']}\n\n"
        result += f"Document ID: `{doc['document_id']}`\n\n"
        result += "## Content:\n\n"
        result += doc['content'][:3000]  # Limit to first 3000 chars
        
        if len(doc['content']) > 3000:
            result += f"\n\n... (truncated, total length: {len(doc['content'])} characters)"
        
        return result
    
    def read_google_sheet(spreadsheet_id: str, range_name: str = "A1:Z100") -> str:
        """
        Read data from a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: Range to read (e.g., 'A1:D10', 'Sheet1!A1:Z100')
        
        Returns:
            Spreadsheet data formatted as a table
        """
        sheet = google_tools.read_spreadsheet(spreadsheet_id, range_name)
        
        if "error" in sheet:
            return f"Error: {sheet['error']}"
        
        result = f"# {sheet['title']}\n\n"
        result += f"Spreadsheet ID: `{sheet['spreadsheet_id']}`\n"
        result += f"Range: `{sheet['range']}`\n\n"
        
        data = sheet.get('data', [])
        if not data:
            return result + "No data found in the specified range."
        
        # Format as markdown table
        result += "## Data:\n\n"
        if data:
            # Header
            result += "| " + " | ".join(str(cell) for cell in data[0]) + " |\n"
            result += "|" + "|".join(["---" for _ in data[0]]) + "|\n"
            
            # Rows (limit to first 50)
            for row in data[1:50]:
                # Pad row to match header length
                padded_row = row + [''] * (len(data[0]) - len(row))
                result += "| " + " | ".join(str(cell) for cell in padded_row) + " |\n"
            
            if len(data) > 51:
                result += f"\n... (showing 50 of {len(data)-1} rows)"
        
        return result
    
    def list_recent_files() -> str:
        """
        List your recent Google Drive files.
        
        Returns:
            List of recent files with links
        """
        files = google_tools.list_my_files()
        
        if not files:
            return "No files found or unable to access files."
        
        result = "## Your Recent Files:\n\n"
        for i, file in enumerate(files[:20], 1):
            file_type = file['mimeType'].split('.')[-1]
            result += f"{i}. **{file['name']}** ({file_type})\n"
            result += f"   - ID: `{file['id']}`\n"
            if 'webViewLink' in file:
                result += f"   - [Open in browser]({file['webViewLink']})\n"
            result += f"   - Modified: {file.get('modifiedTime', 'N/A')}\n\n"
        
        return result
    
    return [
        search_google_drive,
        read_google_doc,
        read_google_sheet,
        list_recent_files
    ]


async def main():
    """Main entry point"""
    
    print("\n" + "=" * 60)
    print("   📄 Google Docs & Sheets Agent (Direct API)")
    print("=" * 60 + "\n")
    
    # Validate environment
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set in .env")
        print("Please configure your .env file first.")
        return
    
    if not groq_key:
        print("❌ GROQ_API_KEY not set in .env")
        print("Get your key from: https://console.groq.com")
        return
    
    # Initialize Google tools
    try:
        google_tools = GoogleWorkspaceTools(creds_path)
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Create tool functions
    tools = create_tool_functions(google_tools)
    
    # Create agent
    agent = Agent(
        name="GoogleWorkspaceAgent",
        model=Groq(id="llama-3.3-70b-versatile"),
        tools=tools,
        description="Google Docs and Sheets assistant using direct API access",
        instructions=dedent("""
            You are an expert assistant for Google Workspace (Docs and Sheets).

            **Available Tools:**
            1. `search_google_drive` - Search for files by name
            2. `read_google_doc` - Read content from a Google Doc (needs document ID)
            3. `read_google_sheet` - Read data from a spreadsheet (needs spreadsheet ID)
            4. `list_recent_files` - Show user's recent files

            **Workflow:**
            1. When user mentions a file, use `search_google_drive` or `list_recent_files`
            2. Get the file ID from search results
            3. Use appropriate read function with the ID
            4. Summarize or analyze the content

            **Best Practices:**
            - Always search for files first to get their IDs
            - Confirm which file to read if multiple matches
            - Summarize long documents
            - Format spreadsheet data as tables
            - Be helpful and explain what you're doing

            **Note:** This is read-only access. You cannot modify files.
        """),
        markdown=True,
        debug_mode=False
    )
    
    print("🤖 Agent ready!\n")
    print("💡 Try these commands:")
    print("   • 'List my recent files'")
    print("   • 'Search for budget spreadsheet'")
    print("   • 'Show me my meeting notes'")
    print("\n" + "-" * 60)
    print("Type 'exit' to quit\n")
    
    # Run interactive session
    await agent.aprint_response(
        "Hello! I can help you search and read your Google Docs and Sheets. What would you like to do?",
        stream=True
    )
    
    # Interactive loop
    while True:
        try:
            user_input = input("\n📄 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            await agent.aprint_response(user_input, stream=True)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Exiting...")