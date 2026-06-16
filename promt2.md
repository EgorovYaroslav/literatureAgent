# Project Update: Structured Literature Review Workflow

## Context
We are refining the literature review automation project. We need to establish a minimal, highly structured project environment, set up tracking files, and rewrite `AGENT.md` to enforce a strict, step-by-step workflow. We will use `git` for version control, and the new `AGENT.md` must strictly follow the format of an existing `AGENT_example.md` file.

## Step 1: Git Initialization & Minimal Project Structure
1. Initialize a git repository in the project root: `git init`.
2. Ensure the minimal folder structure exists: `literature/` and `tools/`.
3. Create a `.gitignore` file that ignores Python virtual environments (`.venv/`, `venv/`), `__pycache__/`, and the cloned `Sci-Hub-MCP-Server/` directory.

## Step 2: Create Tracking and Documentation Files
Create the following markdown files in the project root with minimal, structured templates:
1. **`LIT.md`**: For summarizing the source literature. (Headers: `# Source Literature Notes`, `## Core Topic`, `## Key Findings`, `## Extracted Keywords`).
2. **`LIST.md`**: For the target articles. (Headers: `# Top 10 Target Articles`, `## Article List` - create a numbered list template from 1 to 10 with placeholders for Title, Authors, Year, and DOI).
3. **`FOUND.md`**: For tracking Sci-Hub availability. (Headers: `# Sci-Hub Search Results`, `## Found Articles` - table or list format with fields for: Article Title, DOI/Link, Status [Found/Not Found], Local Filename).
4. **`diary.md`**: A running log of the agent's actions. (Header: `# Agent Diary`, with a template for Date/Time and Action).
5. **`status.md`**: Current project state. (Headers: `# Project Status`, `## Current Step`, `## Blockers`, `## Next Actions`).

## Step 3: Rewrite `AGENT.md` using `AGENT_example.md` as a Template
1. Read the existing `AGENT_example.md` file in the project root.
2. Analyze its structure, tone, formatting, and how it breaks down tasks into sequential steps.
3. Completely rewrite `AGENT.md` to **strictly mimic the structure and style** of `AGENT_example.md`.
4. The content of the new `AGENT.md` must instruct the AI agent to perform the following workflow, split into clear steps matching the example's format:
   - **Step 1**: Read source PDF in `literature/`, analyze it, and populate `LIT.md`. Update `diary.md` and `status.md`. Commit to git.
   - **Step 2**: Identify the top 10 most relevant articles based on `LIT.md` and populate `LIST.md`. Commit to git.
   - **Step 3**: Use the Sci-Hub MCP tool to search for the 10 articles in `LIST.md` and update `FOUND.md` with their availability status. Commit to git.
   - **Step 4**: Download the PDFs of all articles marked as "Found" in `FOUND.md` using the Sci-Hub tool, save them to `literature/`, update the "Local Filename" in `FOUND.md`, and commit to git.
   - **Step 5**: Final review, update `diary.md` with a summary of retrieved articles, set `status.md` to "Task Complete", and make a final git commit.

## Execution Instructions for the Agent
- Execute these steps in exact order.
- Ensure `git` is used to track the creation of files.
- **Do not invent a new format for `AGENT.md`**; you must derive the step-by-step structure directly from `AGENT_example.md`.
