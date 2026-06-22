# SciHubMCP — Autonomous Literature Review Agent

An automated literature review pipeline that uses Sci-Hub MCP + OpenCode to search, fetch, and organize academic papers.

---

## Prerequisites

- Python 3.10+
- [OpenCode](https://opencode.ai) CLI installed
- `uv` package manager (`pip install uv` or `brew install uv`)
- Git

---

## Setup

### 1. Install OpenCode

```bash
# macOS / Linux
curl -fsSL https://opencode.ai/install.sh | sh

# Or via npm
npm install -g @opencode/cli
```

### 2. Start OpenCode Web UI

```bash
opencode web
```

This opens the OpenCode web interface in your browser.

---

## Workflow (execute in OpenCode)

### Step A — Reset to initial state

In the OpenCode chat, ask the agent:

> Run `python3 clear.py` to revert the project to its initial state.

This will keep only:
- `promt1.md`
- `promt2.md`
- `literature/2507.04211v1.pdf`
- `tools/scihub_tool.py`

### Step B — Run Prompt 1 (Setup)

Ask the agent:

> Read `promt1.md` and execute it step by step.

This clones the Sci-Hub MCP server, creates a venv with `uv`, installs dependencies, configures OpenCode MCP, and creates `AGENT.md`.

### Step C — Run Prompt 2 (Refine)

Ask the agent:

> Read `promt2.md` and execute it step by step.

This initializes git, sets up the project structure (`LIT.md`, `LIST.md`, `FOUND.md`, `diary.md`, `status.md`), debugs the download tool, and rewrites `AGENT.md` with a structured workflow.

### Step D — Execute the Literature Review

Ask the agent:

> Read `AGENT.md` and complete the task step by step, committing each step to git.

The agent will:
1. Analyze the source PDF → populate `LIT.md` → commit
2. Identify 10 target articles → populate `LIST.md` → commit
3. Search Sci-Hub for each → populate `FOUND.md` → commit
4. Download found PDFs to `literature/` → commit
5. Final review → commit

---

## Project Structure (after full run)

```
SciHubMCP/
├── Sci-Hub-MCP-Server/   # Cloned MCP server (external dependency)
│   ├── .venv/            # Virtual environment (uv)
│   ├── sci_hub_server.py
│   ├── sci_hub_search.py
│   └── requirements.txt
├── literature/           # Source + downloaded PDFs
├── tools/
│   └── scihub_tool.py    # MCP client wrapper
├── LIT.md                # Source literature notes
├── LIST.md               # Target articles list
├── FOUND.md              # Sci-Hub availability tracking
├── diary.md              # Agent action log
├── status.md             # Project state tracker
├── AGENT.md              # Autonomous task contract
├── opencode.json         # MCP server config
├── promt1.md             # Setup instructions
├── promt2.md             # Refinement instructions
├── clear.py              # Reset script
└── .gitignore
```

---

## Manual Usage

```bash
# Activate venv
source Sci-Hub-MCP-Server/.venv/bin/activate

# Search by DOI
python3 tools/scihub_tool.py search-doi "10.1093/mnras/sty2628"

# Search by keyword
python3 tools/scihub_tool.py search-keyword "solar radio imaging" 5

# Download PDF
python3 tools/scihub_tool.py download "<pdf_url>" "literature/paper.pdf"
```
---

## 🚀 Advanced Assignment: Custom Skills and Tools (For the smartest)

In this assignment, we will go beyond using ready-made tools and learn how to **extend the agent's capabilities**.

An agent in OpenCode consists of two parts:
1. **Tools** — the agent's "hands". Functions that it can call (e.g., `read_file`, `shell`, or our `scihub`).
2. **Skills** — the agent's "brain and experience". These are prompt-instructions that tell the agent *how* and *in what order* to combine Tools to solve complex tasks.

Your task is to add a new **Skill** to the agent for automated literature review and write the missing **Tools** for working with PDFs.

---

### Step 1. Adding a Skill

In OpenCode, skills are usually stored as Markdown files in a special directory so that the agent can load them into its system prompt.

1. Create a `skills/` folder in the root of the project.
2. Create a file `skills/literature.md`.
3. Copy the following code into it (this is the skill description):

<details>
<summary><b>Click to expand the contents of skills/literature.md</b></summary>

```markdown
---
name: literature
description: Literature review — web_search → pdf_download → analysis → literature/review.md
triggers: literature review, scientific papers, arxiv, peer-reviewed, review
combines_with: markdown (for review.md), lean (when formalizing found theorems), python (when analyzing data from papers)
---

# Literature Review — workflow

## When to apply
The user asks:
- "Do a literature review on topic X"
- "Find papers about Y and analyze them"
- "Download a PDF and tell me what's inside"

## Algorithm
1. **Candidate search**: `web_search(query, num_results=10)`. Use qualifiers: `site:arxiv.org`, `filetype:pdf`.
2. **Clarification with the user**: Show the list and ask what to download. Don't download everything without asking!
3. **Folder preparation**: `mkdir -p literature`.
4. **PDF download**: `pdf_download(url, dest_path)`. **Important:** do not use `web_fetch` for PDFs, it breaks binary content.
5. **Deep analysis**: Use `pdf_info`, `pdf_read`, `pdf_search`. If there are >5 papers, read only the first 3 pages.
6. **Report**: Create `literature/review.md` via `text_editor`. Structure: List of papers, Connections, Terms. **Do not hallucinate citations!**
7. **Summary**: Briefly report in the chat (how many papers, path to file, main findings).

## Rules
- Do not hallucinate citations and page numbers.
- Do not invent connections between papers "based on vibes".
- Peer-reviewed filter: mark non-peer-reviewed sources as "reference only".
```
</details>

---

### Step 2. Writing a Tool for working with PDFs

If you read the skill carefully, you noticed that it relies on the `pdf_download`, `pdf_info`, `pdf_read`, and `pdf_search` tools. OpenCode's built-in tools are not enough for this (or they don't work the way we need).

**Your task:** implement these 4 functions.

#### Option A (Simple): CLI wrapper
Create a script `tools/pdf_tool.py` (similar to `scihub_tool.py`) that accepts command-line arguments:
```bash
python3 tools/pdf_tool.py download <url> <dest_path>
python3 tools/pdf_tool.py info <path>
python3 tools/pdf_tool.py read <path> <pages>
python3 tools/pdf_tool.py search <path> <query>
```
*Hint: use the `requests` library for downloading and `PyMuPDF` (fitz) or `pypdf` for parsing PDFs.*

#### Option B (Advanced): Local MCP server
Create a separate MCP server for PDFs so that the agent calls these functions natively, without `shell`.
1. Create a `pdf_mcp_server.py` file.
2. Implement 4 functions (tools) in it using the `mcp` SDK.
3. Register it in `opencode.json`.

---

### Step 3. Integration and configuration

If you chose **Option B (MCP)**, you need to update `opencode.json` by adding your new server there:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "scihub": {
      "type": "local",
      "enabled": true,
      "command": ["./Sci-Hub-MCP-Server/.venv/bin/python", "./Sci-Hub-MCP-Server/sci_hub_server.py"]
    },
    "pdf_tools": {
      "type": "local",
      "enabled": true,
      "command": ["./Sci-Hub-MCP-Server/.venv/bin/python", "./pdf_mcp_server.py"]
    }
  }
}
```
*(Don't forget to install the necessary dependencies into your `uv` environment: `uv pip install pymupdf requests`)*.

---

### Step 4. Testing the new agent

1. Restart OpenCode Web UI (`opencode web`) so it picks up the new `opencode.json` and skills.
2. Write a trigger phrase from the skill to the agent in the chat:
   > "Do a literature review on Physics-Informed Neural Networks for space weather forecasting. Find 3 recent papers on arxiv".
3. Watch as the agent:
   - Remembers the `literature` skill.
   - Finds papers via `web_search`.
   - Asks for your confirmation (or downloads immediately if you asked).
   - Calls your custom `pdf_*` tools.
   - Generates a beautiful `literature/review.md`.

**Success criteria:**
- [ ] The agent successfully calls custom PDF tools without errors.
- [ ] The agent follows the algorithm from `skills/literature.md` (doesn't start writing review.md before downloading and analyzing).
- [ ] There are no "hallucinations" (invented citations) in `review.md`, all page numbers are taken from the real text via `pdf_search`/`pdf_read`.
