from langchain_text_splitters.character import RecursiveCharacterTextSplitter

def ingest_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    return splitter.split_documents(docs)
