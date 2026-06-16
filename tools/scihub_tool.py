import sys
import json
import os
import asyncio
from contextlib import AsyncExitStack

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession


SERVER_CMD = os.path.abspath("./Sci-Hub-MCP-Server/.venv/bin/python")
SERVER_SCRIPT = os.path.abspath("./Sci-Hub-MCP-Server/sci_hub_server.py")
PROJECT_ROOT = os.path.abspath(".")


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

    async def search_by_keyword(self, keyword: str, num_results: int = 10) -> list | dict:
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


async def async_main():
    if len(sys.argv) < 2:
        print("Usage: python scihub_tool.py <command> [args]")
        print("Commands: search-doi, search-title, search-keyword, download, metadata")
        sys.exit(1)

    command = sys.argv[1]

    async with SciHubClient() as client:
        if command == "search-doi" and len(sys.argv) >= 3:
            result = await client.search_by_doi(sys.argv[2])
        elif command == "search-title" and len(sys.argv) >= 3:
            result = await client.search_by_title(sys.argv[2])
        elif command == "search-keyword" and len(sys.argv) >= 3:
            num = int(sys.argv[3]) if len(sys.argv) >= 4 else 10
            result = await client.search_by_keyword(sys.argv[2], num)
        elif command == "download" and len(sys.argv) >= 4:
            result = await client.download_pdf(sys.argv[2], sys.argv[3])
        elif command == "metadata" and len(sys.argv) >= 3:
            result = await client.get_metadata(sys.argv[2])
        else:
            print(f"Unknown command or missing arguments: {command}")
            sys.exit(1)

        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
