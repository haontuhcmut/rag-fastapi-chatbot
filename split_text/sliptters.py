from importlib.metadata import pass_none

from charset_normalizer.utils import is_separator
from langchain_text_splitters import RecursiveCharacterTextSplitter


class Splitters:
    def __init__(self, path_file: str) -> None:
        self.path_file = path_file

    def text_splitters(self):
        with open(f"{self.path_file}") as f:
            state_of_the_union = f.read()

        text_splitters = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        texts = text_splitters.create_documents([state_of_the_union])
        return texts

if __name__ == "__main__":
    splitter = Splitters("../collection/corpus.txt")
    texts = splitter.text_splitters()
    print(texts[0])
    print(texts[1])

