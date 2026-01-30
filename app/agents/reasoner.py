from app.schemas.state import AgentState
from app.tools.llm import llm


def reasoning_agent(state: AgentState) -> dict:
    retrieved_docs = state.get("retrieved_docs", [])
    user_query = state.get("user_query")

    # Guard: no retrieved context
    if not retrieved_docs:
        return {
            "reasoning": None,
            "next_agent": "validator"
        }

    # Remove duplicate chunks while preserving order
    seen = set()
    unique_docs = []
    for doc in retrieved_docs:
        if doc not in seen:
            seen.add(doc)
            unique_docs.append(doc)

    # Limit context size (important for long documents)
    context_chunks = unique_docs[:5]
    context = "\n\n".join(context_chunks)

    prompt = f"""
SYSTEM ROLE:
You are a precise and reliable AI assistant.

STRICT RULES:
- Answer ONLY using the information in the provided document excerpts.
- If the answer is not explicitly present, respond exactly with:
  "The document does not contain enough information to answer this question."
- Do NOT use prior knowledge.
- Do NOT infer or assume information.

DOCUMENT EXCERPTS:
{context}

USER QUESTION:
{user_query}

RESPONSE GUIDELINES:
- Use clear and simple language.
- Be concise but complete.
- Do NOT reference the document or excerpts explicitly.
- Do NOT include any disclaimers or extra commentary.
"""

    try:
        response = llm.invoke(prompt)
        answer = response.content.strip()

        return {
            "reasoning": answer,
            "used_chunks": len(context_chunks),
            "next_agent": "validator"
        }

    except Exception as e:
        # Fail safely — never crash the workflow
        return {
            "reasoning": None,
            "error": str(e),
            "next_agent": "validator"
        }
