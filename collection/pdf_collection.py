from langchain_community.document_loaders import PyPDFLoader
import asyncio

class PDFCollection:
    def __init__(self, path_file: str) -> None:
        self.path_file = path_file

    async def loader_pdf(self):
        loader = PyPDFLoader(self.path_file)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
        return pages

if __name__ == "__main__":
    pdf_col = PDFCollection("../document/data.pdf")
    pages = asyncio.run(pdf_col.loader_pdf())

    # Ghi file cho embedding
    with open("corpus.txt", "w", encoding="utf-8") as f:
        for page in pages:
            text = page.page_content.strip()
            f.write(text + "\n\n")
