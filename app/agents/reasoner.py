from app.rag.citations import format_source_citation
from app.schemas.state import AgentState
from app.tools.llm import llm


def reasoning_agent(state: AgentState) -> dict:
    retrieved_chunks = state.get("retrieved_chunks", [])
    user_query = state.get("user_query")

    if not retrieved_chunks:
        return {"reasoning": None}

    seen = set()
    unique_chunks = []
    for chunk in retrieved_chunks:
        content = chunk.get("content", "")
        if content and content not in seen:
            seen.add(content)
            unique_chunks.append(chunk)

    used_chunks = unique_chunks[:5]
    context = "\n\n".join(c["content"] for c in used_chunks)
    sources = [
        format_source_citation(c, i + 1) for i, c in enumerate(used_chunks)
    ]

    conversation = state.get("conversation", [])
    history_text = ""
    if conversation:
        for turn in conversation[-3:]:
            history_text += f"User: {turn.get('user')}\nAssistant: {turn.get('bot')}\n"

    prompt = f"""
You are a document Q&A assistant. Answer ONLY using the excerpts below.

If the answer is not in the excerpts, respond exactly with:
"The document does not contain enough information to answer this question."

{history_text}
DOCUMENT EXCERPTS:
{context}

USER QUESTION:
{user_query}

Provide one concise plain-text paragraph. Do not use markdown or bullet lists.
"""

    try:
        print(f"📝 Prompt length: {len(prompt)} characters")
        response = llm.invoke(prompt)
        answer = (response.content or "").strip()
        print(f"↩️ Answer length: {len(answer)} characters")

        if not answer:
            return {"reasoning": None, "error": "LLM returned an empty response"}

        if (answer.startswith('"') and answer.endswith('"')) or (
            answer.startswith("'") and answer.endswith("'")
        ):
            answer = answer[1:-1].strip()

        answer = " ".join(line.strip() for line in answer.splitlines() if line.strip())

        new_history = list(conversation)
        new_history.append({"user": user_query, "bot": answer})

        return {
            "reasoning": answer,
            "conversation": new_history,
            "sources": sources,
        }

    except Exception as e:
        return {"reasoning": None, "error": str(e)}
