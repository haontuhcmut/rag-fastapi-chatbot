from collection.pdf_collection import PDFCollection
import asyncio

path_file = "document/data.pdf"

loader = PDFCollection(path_file)

docs = asyncio.run(loader.loader_pdf())

print(docs)

