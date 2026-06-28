"""
RAG Pipeline for Actian → MuleSoft XML Conversion.

Responsibilities:
1. Connect to MongoDB Atlas Vector Search
2. Retrieve similar Actian-Mule examples
3. Build the prompt
4. Generate MuleSoft XML using the configured LLM
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch

from config import (
    CHAT_MODEL,
    COLLECTION_NAME,
    DB_NAME,
    GEMINI_API_KEY,
    INDEX_NAME,
    LLM_PROVIDER,
    MONGO_URI,
    OPENAI_API_KEY,
)

# ----------------------------------------------------
# Embedding Model
# ----------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ----------------------------------------------------
# MongoDB Atlas Vector Search
# ----------------------------------------------------

vector_store = MongoDBAtlasVectorSearch.from_connection_string(
    connection_string=MONGO_URI,
    namespace=f"{DB_NAME}.{COLLECTION_NAME}",
    embedding=embeddings,
    index_name=INDEX_NAME,
)

# ----------------------------------------------------
# LLM
# ----------------------------------------------------

if LLM_PROVIDER == "openai":
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model=CHAT_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0,
    )
elif LLM_PROVIDER in {"google", "gemini"}:
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=0,
    )
else:
    raise ValueError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}. "
        "Use 'openai', 'google', or 'gemini'."
    )

# ----------------------------------------------------
# Prompt
# ----------------------------------------------------

PROMPT = ChatPromptTemplate.from_template(
    """
You are an expert MuleSoft Integration Developer with extensive experience
in migrating legacy Actian DataConnect processes into Mule 4 applications.

Your task is to convert the given Actian XML into a production-ready MuleSoft XML flow.

Use the retrieved examples only as reference.

Requirements:

• Preserve the original business logic.
• Convert database operations into db:select, db:update or db:stored-procedure.
• Convert conditions into Choice Routers.
• Convert variable assignments into Mule 4 vars.
• Convert transformation logic into DataWeave.
• Add Logger components wherever useful.
• Split into subflows whenever appropriate.
• Produce clean, readable Mule 4 XML.

Before generating the XML, explain:

1. What the Actian process does.
2. Database interactions.
3. Transformation logic.
4. Overall migration strategy.

------------------------------------------
Reference Examples
------------------------------------------

{context}

------------------------------------------
Actian XML
------------------------------------------

{query}

Generate the explanation first.

Then generate the complete MuleSoft XML.
"""
)

# ----------------------------------------------------
# Helper Functions
# ----------------------------------------------------


def retrieve_context(query: str, k: int = 5) -> str:
    """
    Retrieves similar Actian-Mule examples from MongoDB Atlas.
    """

    docs = vector_store.similarity_search(query, k=k)

    if not docs:
        return "No similar examples found."

    context = []

    for i, doc in enumerate(docs, start=1):

        context.append(
            f"""
Example {i}
Project: {doc.metadata.get("project")}

{doc.page_content}
"""
        )

    return "\n\n".join(context)


# ----------------------------------------------------
# Main RAG Function
# ----------------------------------------------------


def generate_mule_flow(actian_xml: str) -> str:
    """
    Converts Actian XML into MuleSoft XML.
    """

    context = retrieve_context(actian_xml)

    messages = PROMPT.format_messages(
        context=context,
        query=actian_xml,
    )

    response = llm.invoke(messages)

    return response.content


# ----------------------------------------------------
# Local Testing
# ----------------------------------------------------

if __name__ == "__main__":

    sample = """
<Process name="SampleProcess">
    <Step name="ReadData"/>
</Process>
"""

    result = generate_mule_flow(sample)

    print(result)
