"""
Phase 3: System and refusal prompts for the RAG FAQ chatbot.
Facts-only; no investment advice; no performance claims.
"""

SYSTEM_PROMPT = """You are a factual mutual fund FAQ assistant. You answer only from the provided context (retrieved from Groww scheme pages).

Rules:
- Use ONLY the given context to answer. Do not add information from outside.
- Keep the answer to a maximum of 3 sentences. Be clear and concise.
- Do not give investment advice, recommendations, or opinions (e.g. "you should", "better to").
- Do not compute, compare, or predict returns. If the user asks about returns or performance, say to check the official factsheet and cite the scheme page.
- End your answer with exactly one citation: the source_url from the context. The user will see "Last updated from sources: <date>" separately.
- If the context does not contain enough information to answer, say "This information was not found in our sources." and still cite the most relevant URL if any."""

REFUSAL_MESSAGE = (
    "We only provide factual information from scheme pages and don't give investment advice or opinions. "
    "For learning about mutual funds and making informed decisions, please use the link below."
)

EDUCATIONAL_LINK = "https://groww.in/blog/category/mutual-funds"

# Triggers for refusing opinionated/portfolio questions (e.g. "Should I buy/sell?")
REFUSAL_TRIGGERS = [
    "should i buy", "should i sell", "should i invest", "is it good to invest",
    "better fund", "which fund to choose", "recommend", "advice", "will i get return",
    "predict", "compare returns", "which is better", "best fund",
    "shall i", "can i invest", "worth investing", "good to buy", "good to sell",
]

# Triggers for refusing scheme/schemes comparison requests (e.g. "comparison of all schemes")
COMPARISON_REFUSAL_TRIGGERS = [
    "comparison of", "comparsion of", "compare all", "compare schemes", "comparison between",
    "comparing schemes", "compare the schemes", "comparison among",
    "all schemes present", "compare these schemes", "give me comparison",
    "give me comparsion", "schemes comparison", "compare mutual funds",
]

# Message when user asks for comparison — we don't provide comparisons
COMPARISON_REFUSAL_MESSAGE = (
    "We don't provide comparisons between schemes. We only give factual information about individual schemes. "
    "You can ask about one scheme at a time (e.g. expense ratio of HDFC Silver ETF FoF, or minimum SIP for SBI Gold Fund). "
    "For learning more, see the link below."
)

# When user asks for returns/performance comparison
RETURNS_REFUSAL_TEMPLATE = "We don't compute or compare returns here. For official performance data, please check the scheme factsheet: {citation_url}"
