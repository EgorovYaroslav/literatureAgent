# Project Setup: Sci-Hub MCP Integration & Autonomous Literature Agent

## Context
We are setting up a new project to integrate the Sci-Hub MCP (Model Context Protocol) server and configure an autonomous agent workflow for literature review. Please execute the following steps sequentially to set up the environment using `uv` and `venv`, configure the tools, and define the agent's task.

## Step 1: Clone and Setup the Sci-Hub MCP Server (using uv and venv)
1. Clone the Sci-Hub MCP server repository into the project root:
   `git clone https://github.com/JackKuo666/Sci-Hub-MCP-Server.git`
2. Navigate into the cloned directory (`Sci-Hub-MCP-Server`).
3. Create a Python virtual environment using `uv`:
   `uv venv .venv`
4. Install the required dependencies using `uv pip` (ensure it targets the newly created venv):
   `uv pip install -r requirements.txt`
   *(Note: Ensure Python 3.10+ is used. It requires FastMCP, requests, bs4, and scihub).*

## Step 2: Configure OpenCode MCP & Create Tool
1. **MCP Configuration**: Create the standard configuration file for OpenCode (`opencode.json`) at the project root to register the `scihub` MCP server.
   **CRITICAL**: The `command` must point to the Python executable *inside the virtual environment* (e.g., `./Sci-Hub-MCP-Server/.venv/bin/python` on Linux/macOS or `./Sci-Hub-MCP-Server/.venv/Scripts/python.exe` on Windows) so it can find the installed dependencies. Example structure:
   ```json
      {
         "$schema": "https://opencode.ai/config.json",
         "mcp": {
            "scihub": {
               "type": "local",
               "enabled": true,
               "command": "./Sci-Hub-MCP-Server/.venv/bin/python",
               "args": ["./Sci-Hub-MCP-Server/sci_hub_server.py"]
            }
         }
      }
   ```
2. **Custom Tool Wrapper**: The project already contains a `tools/` folder with a script inside it. Read and inspect the existing `tools/scihub_tool.py` (and the underlying Sci-Hub MCP server logic if necessary). Ensure the script acts as a proper wrapper/tool definition that demonstrates how to programmatically initialize an MCP client, connect to the `scihub` server, and call its search/download functions.

## Step 3: Directory Setup
1. Create a folder named `literature/` in the project root. This will be used to store source PDFs and downloaded articles.

## Step 4: Create AGENT.md for Autonomous Task
Create an `AGENT.md` file in the project root. This file must describe the following autonomous task for the AI agent to execute in the future:

**Task Description to include in AGENT.md:**
"Your task is to perform an automated literature review based on an existing document.
1. **Read Source Material**: Locate and read the PDF file(s) currently placed in the `literature/` folder.
2. **Extract Key Information**: Analyze the text to identify the core research topic, keywords, and critical references.
3. **Find Relevant Articles**: Use the configured Sci-Hub MCP tool to search for academic papers. Based on the extracted keywords and context, identify the 5 most relevant articles related to the source material's topic.
4. **Download and Save**: Use the Sci-Hub MCP tool to download the PDFs of these 5 selected articles.
5. **Organize**: Save all 5 downloaded PDFs directly into the `literature/` folder.
6. **Report**: Generate a brief summary listing the titles, authors, and reasons why these 5 articles were selected as the most relevant."

## Execution Instructions for the Agent
- Execute these steps sequentially.
- Use `uv` for all virtual environment and package management tasks.
- Ensure all file paths in the `opencode.json` MCP configuration correctly resolve to the `.venv` python executable and the `sci_hub_server.py` script so the MCP server can start properly.
- Verify that the `tools/scihub_tool.py` script is syntactically correct.
- Ensure the `AGENT.md` is clearly formatted in Markdown so it can be easily parsed by any AI agent in the future.