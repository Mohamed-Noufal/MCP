# MCP (Model Context Protocol) Learning Repository

This repository contains a comprehensive collection of MCP (Model Context Protocol) implementations, examples, and projects from various learning resources, primarily focused on building rich-context AI applications with Anthropic and other AI frameworks.

## 📚 Repository Structure

### Core Learning Materials

#### **Crash Course**
Complete MCP crash course covering fundamentals to advanced topics:
- Introduction and Context
- Understanding MCP
- Simple Server Setup (SSE, STDIO, Streamable HTTP)
- OpenAI Integration
- MCP vs Function Calling
- Docker Deployment
- Lifecycle Management

#### **Deep Learning Course Lessons**
Progressive lessons from the Anthropic MCP course:
- **L3**: Chatbot Example
- **L4**: Creating an MCP Server
- **L5**: Creating an MCP Client
- **L6**: Connecting MCP Chatbot to Reference Servers
- **L7**: Adding Prompt & Resource Features
- **L8**: Creating and Deploying Remote Servers

### Project Implementations

- **📝 Notion-MCP-Agent**: Integration between Notion and MCP
- **📧 mcp-notion-email**: Email integration with Notion via MCP
- **📄 Docs-sheet-mcp**: Google Sheets/Docs MCP integration
- **🌐 Community Servers**: Various MCP server implementations
- **🧪 Acadamic-Research**: Research and experimental implementations

### Additional Resources
- **Appendx**: Supporting materials, images, and documentation
- **1/**: Simple agent implementation examples

## 🚀 Getting Started

### Prerequisites

- Python 3.13 or higher
- Node.js (for JavaScript-based servers)
- Docker (optional, for containerized deployments)
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Mohamed-Noufal/MCP.git
cd N-MCP
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies for specific projects:
```bash
# For Python projects
pip install -r requirements.txt

# For Node.js projects (e.g., Notion-server-)
cd Notion-server-
npm install
```

### Environment Setup

Create a `.env` file based on `.env.example` (found in crash-course) and add your API keys:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
# Add other required keys
```

## 📖 How to Use This Repository

### For Learning
Navigate through the lessons in order (L3 → L8) to understand MCP progressively. Each lesson contains:
- Jupyter notebooks with explanations
- Python implementation files
- README documentation
- Supporting images and resources

### For Reference
Browse the `crash-course` directory for quick references on specific MCP topics and implementations.

### For Development
Use the various server implementations in `Community Servers`, `Notion-server-`, and other project directories as templates for your own MCP servers.

## 🔧 Key Technologies

- **MCP (Model Context Protocol)**: Core protocol for AI context management
- **Python**: Primary implementation language
- **OpenAI API**: LLM integration
- **Anthropic Claude**: Advanced AI model integration
- **Docker**: Containerization and deployment
- **Notion API**: Notion workspace integration
- **Google APIs**: Sheets/Docs integration

## 📂 Project Highlights

### MCP Chatbot Client
Found in L5-L7, demonstrates how to:
- Create MCP clients
- Connect to reference servers
- Implement prompt and resource features

### Research Server
Custom MCP server implementation showcasing:
- Tool definition and registration
- Resource management
- Prompt templates

### Notion Integration
Full-featured Notion MCP server with:
- Email integration
- Database operations
- Agent-based interactions

## 🤝 Contributing

This is a learning repository. Feel free to:
- Explore the code
- Try the examples
- Create your own MCP implementations
- Share improvements

## 📝 License

Please refer to individual project directories for specific licensing information.

## 🔗 Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Anthropic Documentation](https://docs.anthropic.com/)
- [Deep Learning AI Course](https://www.deeplearning.ai/)

## 📧 Contact

https://www.linkedin.com/in/mohamed-noufal-b7101a25b/
For questions or collaboration:
- GitHub: [@Mohamed-Noufal](https://github.com/Mohamed-Noufal)

---

**Note**: This repository is for educational purposes. Ensure you have proper API keys and credentials before running any examples that require external services.
