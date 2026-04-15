
# 📊 Gradio MCP Finance Server
A complete **Model Context Protocol (MCP) server** for financial analysis tools,
built with Gradio. This project extends the stock price tool from `tool_use.ipynb`
into a robust, standardized service that works with any MCP-compatible client like
Claude, Cursor, and Cline.
## 📊 Quick Start
1. **Install uv** (if not already installed):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or with pip
pip install uv
```
2. **Setup virtual environment and install dependencies**:
```bash
cd <folder>
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```
3. **Run the Server**:
```bash
python gradio_mcp_finance_server.py
```
4. **Connect to Your MCP Client**:
Add this to your MCP client configuration:
```json
{
"mcpServers": {
"gradio-finance": {
"url": "http://localhost:7860/gradio_api/mcp/sse"
}
}
}
```
That's it! The tools will now be available in Claude, Cursor, or Cline.

# 🧩 How This Project Works (Simple Explanation)

## What is MCP?
**Model Context Protocol (MCP)** is a standard that lets AI models (like Claude, Cursor, or Cline) use external tools and APIs in a safe, structured way. Think of it as a universal language for AI to talk to different services.

## What is this Project?
This project is a **Finance MCP Server** built with Gradio. It provides financial tools (like stock price lookup, company info, etc.) as MCP-compatible functions. Any AI or app that understands MCP can connect and use these tools.

## How Does It Work?
1. **Server Side (this repo):**
	- Runs a Gradio app that exposes finance tools as MCP functions.
	- Waits for requests from MCP clients (like "What is the price of AAPL?").
	- Processes the request, fetches data (e.g., from Yahoo Finance), and sends back the answer.

2. **Client Side (MCP Client):**
	- Could be an AI assistant, notebook, or app (see the example notebook in this repo).
	- Sends questions/commands to the MCP server using the MCP protocol.
	- Receives structured answers and displays them to the user.

## Example Flow
1. User asks: "Compare AAPL and MSFT prices."
2. MCP client sends this to the server.
3. Server runs the right tool/function (e.g., stock comparison).
4. Server sends back the result (prices, ratios, etc.).
5. Client shows the answer to the user.

## Why is this Useful?
- **Plug-and-play:** Any AI that supports MCP can use these tools instantly.
- **Standardized:** No need to write custom code for each AI or tool.
- **Extensible:** Add more finance tools easily by updating the server.

## Main Files
- `gradio_mcp_finance_server.py`: The main server code exposing finance tools.
- `gradio_mcp_finance_client.ipynb`: Example notebook showing how to connect as a client and use the tools.
- `requirements.txt`: Python dependencies.

---
**In summary:**
This project lets any AI or app use advanced finance tools by simply connecting to your server, as of the MCP standard and Gradio's easy interface.
