"""
Builds the MongoDB Atlas Vector Store from paired
Actian XML and MuleSoft XML examples.

Run:
    python ingest.py
"""

from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain_huggingface import HuggingFaceEmbeddings


from config import (
    DATA_DIR,
    OPENAI_API_KEY,
    MONGO_URI,
    DB_NAME,
    COLLECTION_NAME,
    INDEX_NAME,
    EMBEDDING_MODEL,
)


def normalize_mongo_uri(uri):
    """
    Percent-encodes MongoDB credentials when the username or password
    contains reserved URI characters.
    """

    parsed = urlsplit(uri)

    if "@" not in parsed.netloc:
        return uri

    credentials, host = parsed.netloc.rsplit("@", 1)

    if ":" not in credentials:
        return uri

    username, password = credentials.split(":", 1)
    safe_netloc = f"{quote(username, safe='')}:{quote(password, safe='')}@{host}"

    return urlunsplit(
        (parsed.scheme, safe_netloc, parsed.path, parsed.query, parsed.fragment)
    )


def load_documents():
    """
    Reads every folder inside /data.
    Each folder should contain:
        *_Actian.xml
        *_MuleSoft.xml
    """

    documents = []
    folders = sorted([folder for folder in DATA_DIR.iterdir() if folder.is_dir()])

    splitter = RecursiveCharacterTextSplitter(
        separators=[
            "</Step>",
            "</Session>",
            "</Variable>",
            "\n\n",
            "\n",
        ],
        chunk_size=1800,
        chunk_overlap=250,
    )

    for folder in folders:

        actian_file = None
        mule_file = None

        for file in folder.iterdir():

            filename = file.name.lower()

            if "actian" in filename:
                actian_file = file

            elif "mule" in filename:
                mule_file = file

        if not actian_file or not mule_file:
            print(f"Skipping {folder.name} (missing XML pair)")
            continue

        with open(actian_file, encoding="utf-8") as f:
            actian_xml = f.read()

        with open(mule_file, encoding="utf-8") as f:
            mule_xml = f.read()

        combined = f"""
############################################################

PROJECT

{folder.name}

############################################################

ACTIAN XML

{actian_xml}

############################################################

EXPECTED MULESOFT CONVERSION

{mule_xml}

############################################################
"""

        chunks = splitter.split_text(combined)

        for i, chunk in enumerate(chunks):

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "project": folder.name,
                        "chunk": i,
                        "source": "ActianToMule",
                        "actian_file": actian_file.name,
                        "mule_file": mule_file.name,
                    },
                )
            )

    return documents, len(folders)


def main():

    print("=" * 60)
    print("Loading training examples...")
    print("=" * 60)

    docs, total_projects = load_documents()

    print(f"Loaded {len(docs)} chunks from {total_projects} projects.")

    print("\nConnecting to MongoDB Atlas...")

    client = MongoClient(normalize_mongo_uri(MONGO_URI))

    collection = client[DB_NAME][COLLECTION_NAME]

    print("Clearing existing collection...")
    collection.delete_many({})

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Creating embeddings and uploading to Atlas...")

    vector_store = MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=embeddings,
        collection=collection,
        index_name=INDEX_NAME,
    )

    print("\nDone!")
    print(f"Indexed {len(docs)} chunks into MongoDB Atlas.")


if __name__ == "__main__":
    main()


    
