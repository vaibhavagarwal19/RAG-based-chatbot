from app.schemas.state import AgentState
from app.tools.llm import llm


def reasoning_agent(state: AgentState) -> dict:
    retrieved_docs = state.get("retrieved_docs", [])
    retrieved_scores = state.get("retrieved_scores", [])
    user_query = state.get("user_query")

    # Guard: no retrieved context
    if not retrieved_docs:
        return {
            "reasoning": None,
            "next_agent": "validator"
        }

    # sort chunks by similarity score if provided (lower score == more relevant)
    if retrieved_scores:
        paired = list(zip(retrieved_docs, retrieved_scores))
        paired.sort(key=lambda x: float('inf') if x[1] is None else x[1])
        retrieved_docs = [p[0] for p in paired]
        print(f"📊 Sorted chunks by score: {[p[1] for p in paired]}")

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

    # prepare conversation history if any
    conversation = state.get("conversation", [])
    history_text = ""
    if conversation:
        # include last three turns to keep prompt size reasonable
        for turn in conversation[-3:]:
            history_text += f"User: {turn.get('user')}\nAssistant: {turn.get('bot')}\n"

    # few-shot examples to set response style
    examples = (
        "Example 1:\n"
        "User: What is the capital of France?\n"
        "Assistant: Paris is the capital of France.\n\n"
        "Example 2:\n"
        "User: Who wrote 'Pride and Prejudice'?\n"
        "Assistant: The novel 'Pride and Prejudice' was written by Jane Austen.\n\n"
    )

    prompt = f"""
SYSTEM ROLE:
You are a highly accurate AI assistant whose sole job is to read the provided excerpts and answer the user question.

STRICT RULES:
- Answer ONLY using the information in the provided document excerpts.
- If the answer is not explicitly present, respond exactly with:
  "The document does not contain enough information to answer this question."
- Do NOT use prior knowledge.
- Do NOT infer or assume information.

{examples if not history_text else examples + history_text}
DOCUMENT EXCERPTS:
{context}

USER QUESTION:
{user_query}

RESPONSE GUIDELINES:
- Provide a single, standalone answer in plain text (no lists, bullet points, headings, or markdown).
- Avoid quotation marks around the response and do not prepend phrases like "Answer:" or "Response:".
- Use clear and simple language.
- Be concise but complete; keep it to one paragraph if possible.
- Do NOT reference the document or excerpts explicitly.
- Do NOT include any disclaimers, meta commentary, or extraneous sentences.
"""

    try:
        # debug info
        print(f"📝 Prompt length: {len(prompt)} characters")
        response = llm.invoke(prompt)
        answer = response.content.strip()
        print(f"↩️ Raw answer length: {len(answer)} characters")

        # clean surrounding quotes if model added them
        if (answer.startswith('"') and answer.endswith('"')) or (
            answer.startswith("'") and answer.endswith("'")
        ):
            answer = answer[1:-1].strip()

        # collapse multiple newlines to a single space
        answer = " ".join(line.strip() for line in answer.splitlines() if line.strip())

        # update conversation history so follow-ups can be aware
        new_history = conversation.copy() if conversation else []
        new_history.append({"user": user_query, "bot": answer})

        return {
            "reasoning": answer,
            "used_chunks": len(context_chunks),
            "conversation": new_history,
            "next_agent": "validator"
        }

    except Exception as e:
        # Fail safely — never crash the workflow
        return {
            "reasoning": None,
            "error": str(e),
            "next_agent": "validator"
        }
