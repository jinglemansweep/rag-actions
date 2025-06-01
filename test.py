from pathlib import Path
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import DirectoryLoader

PATH = Path("./test/content")
GLOB_PATTERN = "**/*.md"


loader = DirectoryLoader(
    PATH,
    glob=GLOB_PATTERN,
    loader_cls=UnstructuredMarkdownLoader,
    loader_kwargs={"mode": "elements"},
)
data = loader.load()
for doc in data:
    print("=== Document ===")
    print(doc.page_content)
    print("=== Metadata ===")
    print(doc.metadata)
