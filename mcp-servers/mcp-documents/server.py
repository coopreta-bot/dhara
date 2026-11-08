"""mcp-documents. Contract server for the document store. Status: OPEN."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import serve


if __name__ == "__main__":
    serve(Path(__file__).resolve().parent)
