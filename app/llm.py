
# from openai import OpenAI
from .config import settings

# client = OpenAI(
#     base_url=settings.OPENAI_BASE_URL,
#     api_key=settings.OPENAI_API_KEY
# )

# SYS_PROMPT = (
#     "You are a precise RAG assistant. Answer ONLY using the provided context. "
#     "If the answer is not in the context, say 'I cannot find this in the provided sources.' "
#     "Be concise and cite source chunk ids where relevant."
# )

def build_context_block(sources):
    lines = []
    for s in sources:
        # sid = s["id"]
        txt = s["text"].replace("\n", " ").strip()
        lines.append(f"{txt}")
    return "\n".join(lines[:12])  # safety cap

def generate_answer(query: str, sources: list[dict]) -> str:
    # context = build_context_block(sources)
    print('context\n',context)
    messages = [
        # {"role": "system", "content": SYS_PROMPT},
        {"role": "user", "content": f"Question: {query}\n\nContext:\n{context}"}
    ]
    # resp = client.chat.completions.create(
    #     model=settings.LLM_MODEL,
    #     messages=messages,
    #     temperature=0.2,
    #     max_tokens=600
    # )
    return resp.choices[0].message.content.strip()
