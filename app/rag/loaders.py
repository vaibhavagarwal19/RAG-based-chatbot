from langchain_community.document_loaders import PyPDFLoader

def load_pdf(path: str):
    loader = PyPDFLoader(path)
    docs = loader.load()

    # Add filename as metadata
    for doc in docs:
        doc.metadata["source"] = path

    return docs

