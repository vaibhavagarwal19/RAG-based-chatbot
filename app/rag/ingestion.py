from langchain_text_splitters import RecursiveCharacterTextSplitter

def ingest_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_documents(docs)
