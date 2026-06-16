"""
Sci-Hub MCP Client Wrapper

Usage:
    python tools/scihub_tool.py search-doi <doi>
    python tools/scihub_tool.py search-title <title>
    python tools/scihub_tool.py search-keyword <keyword> [num_results]
    python tools/scihub_tool.py download <pdf_url> <output_path>
    python tools/scihub_tool.py metadata <doi>

The tool first tries the MCP server (stdio). If it fails (Sci-Hub unreachable),
it falls back to direct HTTP access with a properly configured session that
handles DDOS-guard protected Sci-Hub domains.
"""

import sys
import json
import os
import re
import asyncio
import logging
from contextlib import AsyncExitStack

import requests
import urllib3
from bs4 import BeautifulSoup

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.WARNING)

SERVER_CMD = os.path.abspath("./Sci-Hub-MCP-Server/.venv/bin/python")
SERVER_SCRIPT = os.path.abspath("./Sci-Hub-MCP-Server/sci_hub_server.py")
PROJECT_ROOT = os.path.abspath(".")


def _make_scihub_session() -> requests.Session:
    """Create a requests Session ready for Sci-Hub (handles DDOS-guard cookies)."""
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
    session.verify = False
    session.get("https://sci-hub.ru", timeout=15)
    return session


def _direct_fetch_via_scihub(doi: str) -> dict:
    """Fetch a paper from Sci-Hub by DOI using direct HTTP."""
    result = {"doi": doi, "status": "not_found"}
    session = _make_scihub_session()
    try:
        r = session.get(f"https://sci-hub.ru/{doi}", timeout=30)
        if "отсутствует" in r.text or len(r.text) < 500:
            return result
        soup = BeautifulSoup(r.text, "html.parser")
        pdf_url = None
        iframe = soup.find("iframe")
        if iframe and iframe.get("src"):
            pdf_url = iframe["src"]
        embed = soup.find("embed")
        if embed and embed.get("src"):
            pdf_url = embed["src"]
        dl = soup.find("a", href=re.compile(r"storage/tail|download"))
        if dl:
            pdf_url = dl["href"]
        if pdf_url:
            if not pdf_url.startswith("http"):
                pdf_url = "https://sci-hub.ru" + pdf_url
            result["pdf_url"] = pdf_url
            result["status"] = "success"
            # Extract citation metadata from page meta tags
            for meta in soup.find_all("meta"):
                name = meta.get("name", "")
                content = meta.get("content", "")
                if name == "citation_title":
                    result["title"] = content
                elif name == "citation_author":
                    result.setdefault("author", content)
                elif name == "citation_date":
                    result["year"] = content[:4] if content else ""
                elif name == "citation_doi":
                    result["doi"] = content
    except Exception as e:
        result["error"] = str(e)
    return result


def _direct_search_by_title(title: str) -> dict:
    """Search by title via CrossRef, then try Sci-Hub."""
    session = _make_scihub_session()
    try:
        url = f"https://api.crossref.org/works?query.title={title}&rows=1"
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            items = r.json()["message"]["items"]
            if items:
                doi = items[0].get("DOI")
                if doi:
                    result = _direct_fetch_via_scihub(doi)
                    if result.get("title"):
                        return result
                    result["doi"] = doi
                    result["title"] = items[0].get("title", [""])[0]
                    authors = items[0].get("author", [])
                    result["author"] = ", ".join(a.get("family", "") for a in authors[:3])
                    date = items[0].get("published-print", {}).get("date-parts", [[None]])[0]
                    if not date or date[0] is None:
                        date = items[0].get("published-online", {}).get("date-parts", [[None]])[0]
                    result["year"] = str(date[0]) if date and date[0] else ""
                    return result
    except Exception as e:
        return {"title": title, "status": "error", "error": str(e)}
    return {"title": title, "status": "not_found"}


def _direct_search_by_keyword(keyword: str, num_results: int = 10) -> list:
    """Search by keyword via CrossRef."""
    papers = []
    session = _make_scihub_session()
    try:
        url = f"https://api.crossref.org/works?query={keyword}&rows={num_results}"
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            for item in r.json()["message"]["items"]:
                doi = item.get("DOI")
                if not doi:
                    continue
                result = _direct_fetch_via_scihub(doi)
                if result["status"] == "success":
                    papers.append(result)
    except Exception as e:
        return [{"error": str(e)}]
    return papers


def _direct_download_pdf(pdf_url: str, output_path: str) -> bool:
    """Download a PDF from a URL to a local file."""
    session = _make_scihub_session()
    try:
        r = session.get(pdf_url, timeout=60)
        if "pdf" in r.headers.get("Content-Type", "") and len(r.content) > 10000:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(r.content)
            return True
    except Exception:
        pass
    return False


def _direct_get_metadata(doi: str) -> dict:
    """Get metadata via CrossRef."""
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    try:
        url = f"https://api.crossref.org/works/{doi}"
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            item = r.json()["message"]
            authors = item.get("author", [])
            author_str = ", ".join(a.get("family", "") for a in authors[:3])
            title = item.get("title", [""])[0]
            date = item.get("published-print", {}).get("date-parts", [[None]])[0]
            if not date or date[0] is None:
                date = item.get("published-online", {}).get("date-parts", [[None]])[0]
            year = str(date[0]) if date and date[0] else ""
            return {
                "doi": doi,
                "title": title,
                "author": author_str,
                "year": year,
                "status": "success",
            }
    except Exception as e:
        return {"doi": doi, "status": "error", "error": str(e)}
    return {"doi": doi, "status": "not_found"}


class SciHubClient:
    def __init__(self):
        self.session: ClientSession | None = None
        self._exit_stack = AsyncExitStack()

    async def __aenter__(self):
        server_params = StdioServerParameters(
            command=SERVER_CMD,
            args=[SERVER_SCRIPT],
        )
        transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = transport
        self.session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()
        return self

    async def __aexit__(self, *args):
        await self._exit_stack.__aexit__(*args)

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        if self.session is None:
            return {"error": "Not connected to MCP server"}
        try:
            result = await self.session.call_tool(tool_name, arguments)
            return {
                "content": result.content,
                "isError": result.isError,
            }
        except Exception as e:
            return {"error": str(e)}

    async def search_by_doi(self, doi: str) -> dict:
        return await self.call_tool("search_scihub_by_doi", {"doi": doi})

    async def search_by_title(self, title: str) -> dict:
        return await self.call_tool("search_scihub_by_title", {"title": title})

    async def search_by_keyword(self, keyword: str, num_results: int = 10):
        return await self.call_tool(
            "search_scihub_by_keyword",
            {"keyword": keyword, "num_results": num_results},
        )

    async def download_pdf(self, pdf_url: str, output_path: str) -> str:
        abs_path = os.path.join(PROJECT_ROOT, output_path) if not os.path.isabs(output_path) else output_path
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        return await self.call_tool(
            "download_scihub_pdf",
            {"pdf_url": pdf_url, "output_path": abs_path},
        )

    async def get_metadata(self, doi: str) -> dict:
        return await self.call_tool("get_paper_metadata", {"doi": doi})


def _mcp_failed(raw_output: str) -> bool:
    """Check if MCP response indicates failure (Sci-Hub unreachable)."""
    return any(marker in raw_output.lower() for marker in ["not_found", "error occurred", "connection"])


async def async_main():
    if len(sys.argv) < 2:
        print("Usage: python scihub_tool.py <command> [args]")
        print("Commands: search-doi, search-title, search-keyword, download, metadata")
        sys.exit(1)

    command = sys.argv[1]

    async with SciHubClient() as client:
        if command == "search-doi" and len(sys.argv) >= 3:
            doi = sys.argv[2]
            result = await client.search_by_doi(doi)
            raw = json.dumps(result, indent=2, ensure_ascii=False, default=str)
            if _mcp_failed(raw):
                fallback = _direct_fetch_via_scihub(doi)
                print(json.dumps(fallback, indent=2, ensure_ascii=False, default=str))
            else:
                print(raw)

        elif command == "search-title" and len(sys.argv) >= 3:
            title = sys.argv[2]
            result = await client.search_by_title(title)
            raw = json.dumps(result, indent=2, ensure_ascii=False, default=str)
            if _mcp_failed(raw):
                fallback = _direct_search_by_title(title)
                print(json.dumps(fallback, indent=2, ensure_ascii=False, default=str))
            else:
                print(raw)

        elif command == "search-keyword" and len(sys.argv) >= 3:
            keyword = sys.argv[2]
            num = int(sys.argv[3]) if len(sys.argv) >= 4 else 10
            result = await client.search_by_keyword(keyword, num)
            raw = json.dumps(result, indent=2, ensure_ascii=False, default=str)
            if _mcp_failed(raw):
                fallback = _direct_search_by_keyword(keyword, num)
                print(json.dumps(fallback, indent=2, ensure_ascii=False, default=str))
            else:
                print(raw)

        elif command == "download" and len(sys.argv) >= 4:
            pdf_url = sys.argv[2]
            output_path = sys.argv[3]
            abs_path = os.path.join(PROJECT_ROOT, output_path) if not os.path.isabs(output_path) else output_path
            result = await client.download_pdf(pdf_url, output_path)
            raw = json.dumps(result, indent=2, ensure_ascii=False, default=str)
            if _mcp_failed(raw):
                success = _direct_download_pdf(pdf_url, abs_path)
                if success:
                    print(json.dumps({"status": "success", "path": abs_path}, indent=2))
                else:
                    print(json.dumps({"status": "failed", "path": abs_path}, indent=2))
            else:
                print(raw)

        elif command == "metadata" and len(sys.argv) >= 3:
            doi = sys.argv[2]
            result = await client.get_metadata(doi)
            raw = json.dumps(result, indent=2, ensure_ascii=False, default=str)
            if _mcp_failed(raw):
                fallback = _direct_get_metadata(doi)
                print(json.dumps(fallback, indent=2, ensure_ascii=False, default=str))
            else:
                print(raw)

        else:
            print(f"Unknown command or missing arguments: {command}")
            sys.exit(1)


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
