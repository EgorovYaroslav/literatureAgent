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
