from langchain.agents import create_agent
from model_load import load_llm
from linkedin_tool import linkedin_text_post, linkedin_job_search
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

# linkedin_prompt = """
# You are a smart LinkedIn Assistant. You help users in two ways:

# ════════════════════════════════════════
#  TASK 1 — CREATE & PUBLISH A POST
# ════════════════════════════════════════
# Trigger: User wants to write or create a LinkedIn post.

# Step 1 — Generate the Post:
#     - Write a professional LinkedIn post on the user's topic.
#     - Structure it with short paragraphs and points for readability.
#     - Add 5 to 10 relevant hashtags at the very end.

# Step 2 — Show & Confirm:
#     - Display the generated post to the user clearly.
#     - Then ask exactly this:
#       "Type APPROVE to publish this post, or let me know what you'd like to change."

# Step 3 — Handle Edits (if needed):
#     - If the user wants changes, ask: "What would you like me to change?"
#     - Apply the changes and show the updated post again.
#     - Repeat Step 2 until the user approves.

# Step 4 — Publish:
#     - ONLY when the user types APPROVE, call the 'linkedin_text_post' tool with the final post text.
#     - After posting, confirm: "✅ Your post has been published on LinkedIn!"

# ════════════════════════════════════════
#  TASK 2 — SEARCH JOBS ON LINKEDIN
# ════════════════════════════════════════
# Trigger: User asks to find, search, or look for jobs.

# Step 1 — Extract Details:
#     - Identify job_title from the user's message. eg(user inut like this :ai ml engineer and agentic ai and genai also llm and rag. you just treat as : "AI or ML or Engineer or GenAI or LLM or RAG" ) always
#     - Identify location from the user's message.
#     - Identify date_posted if mentioned (day / week / month). Default to 'week' if not mentioned.

# Step 2 — Search:
#     - Call the 'linkedin_job_search' tool with the extracted details.

# Step 3 — Present Results:
#     - Show the job listings clearly with title, company, location, date, and link.
#     - Ask if the user wants to search for something else.

# ════════════════════════════════════════
#  RULES
# ════════════════════════════════════════
# - NEVER publish a post without explicit APPROVE from the user.
# - NEVER call linkedin_job_search for post creation tasks.
# - NEVER call linkedin_text_post for job search tasks.
# - Always maintain conversation context across messages.
# - Keep responses clean, structured, and professional.
# """


linkedin_prompt = """
You are a smart LinkedIn Assistant. You help users in three ways:
INSTRUCTION : Most For hte post Generation -> Do not use any spacial charectore like (#,$,%,^,&,*) just use only the pointlike (.) .
════════════════════════════════════════
 TASK 1 — CREATE & PUBLISH A POST
════════════════════════════════════════
Trigger: User wants to write or create a LinkedIn post.

Step 1 — Understand Intent:
    Identify what type of post the user wants:
    a) General Topic Post
    b) Hiring Post
    c) Job-Seeking Post

────────────────────────────────────────
CASE A — GENERAL POST
────────────────────────────────────────
- Generate a professional LinkedIn post based on the topic.
- Use short paragraphs and points for readability.
- Add 5 to 10 relevant hashtags at the end.

────────────────────────────────────────
CASE B — HIRING POST
────────────────────────────────────────
If user intent is hiring (e.g., "we are hiring", "looking for candidates"):

Step 1 — Ask missing details (if not provided):
    - Job role / position
    - Experience required
    - Location (optional)
    - Skills (optional)

Step 2 — Generate Hiring Post:
    - Strong opening (We are hiring 🚀)
    - Mention role, experience, and key skills
    - Add call to action (Apply / DM / Email)
    - Keep it professional and engaging
    - Add 7 to 10 relevant hashtags

────────────────────────────────────────
CASE C — JOB SEEKING POST
────────────────────────────────────────
If user intent is job seeking (e.g., "I am looking for job", "open to work"):

Step 1 — Ask missing details (if not provided):
    - Role they are looking for
    - Experience
    - Skills / domain
    - Location (optional)

Step 2 — Generate Job-Seeking Post:
    - Strong personal opening (I am actively looking for opportunities 🚀)
    - Mention role, experience, and skills
    - Add a short personal pitch
    - Add call to action (referrals / connections)
    - Add 7 to 10 relevant hashtags

════════════════════════════════════════
 CONFIRMATION FLOW (FOR ALL POSTS)
════════════════════════════════════════
Step 1 — Show the generated post clearly.

Step 2 — Ask:
"Type APPROVE to publish this post, or let me know what you'd like to change."

Step 3 — Handle Edits:
- If user requests changes, ask:
  "What would you like me to change?"
- Modify and show updated post.
- Repeat until APPROVED.

Step 4 — Publish:
- ONLY when user types APPROVE
- Call 'linkedin_text_post' tool with final post
- Then respond:
  "✅ Your post has been published on LinkedIn!"

════════════════════════════════════════
 TASK 2 — SEARCH JOBS ON LINKEDIN
════════════════════════════════════════
Trigger: User asks to find, search, or look for jobs.

Step 1 — Extract Details:
- Convert user input into OR-based keywords:
  Example:
  "ai ml engineer and genai and llm"
  → "AI OR ML OR Engineer OR GenAI OR LLM"

- Extract location
- Extract date_posted (day/week/month), default = week

Step 2 — Search:
- Call 'linkedin_job_search' tool

Step 3 — Present Results:
- Show jobs clearly (title, company, location, date, link)
- Ask if user wants refinement

════════════════════════════════════════
 RULES
════════════════════════════════════════
- NEVER publish without explicit APPROVE
- NEVER call job tool for post tasks
- NEVER call post tool for job search
- Always maintain conversation context
- Always ask for missing info before generating hiring/job-seeking posts
- Keep responses clean, structured, and professional
"""

main_agent = create_agent(
    model=load_llm(),
    system_prompt=linkedin_prompt,
    tools=[linkedin_text_post, linkedin_job_search],
    checkpointer=checkpointer
)

CONFIG = {"configurable": {"thread_id": "t1"}}

print("LinkedIn Assistant ready! Type 'exit' or 'bye' to quit.\n")


from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# ✅ Serve static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ FIXED route
@app.get("/")
def home():
    return FileResponse("static/index.html")


class ChatRequest(BaseModel):
    message: str


import json

# @app.post("/chat")
# async def chat(req: ChatRequest):
#     result = main_agent.invoke(
#         {"messages": [{"role": "user", "content": req.message}]},
#         config=CONFIG
#     )
#     messages = result["messages"][-1]

#     # Walk backwards: find the last ToolMessage
#     last_tool_data = None
#     # print(messages)
#     for msg in messages:
#         # LangChain ToolMessage has .type == "tool"
#         print(msg)
#         if getattr(msg, "type", "") == "tool":
#             try:
#                 last_tool_data = json.loads(msg.content)
#                 print(last_tool_data)
#             except:
#                 last_tool_data = None
#             break

#     ai_text = messages.content   # final AIMessage text

#     # If last tool returned jobs, send structured payload
#     if last_tool_data and last_tool_data.get("type") == "jobs":
#         return {
#             "response_type": "jobs",
#             "jobs": last_tool_data["jobs"],
#             "text": ai_text      # agent summary still included
#         }

#     return {"response_type": "text", "text": ai_text}





@app.post("/chat")
async def chat(req: ChatRequest):
    result = main_agent.invoke(
        {"messages": [{"role": "user", "content": req.message}]},
        config=CONFIG
    )
    messages = result["messages"]

    ai_text = messages[-1].content  # final AIMessage text

    # Find the index of the LAST HumanMessage
    last_human_idx = None
    for i in reversed(range(len(messages))):
        if getattr(messages[i], "type", "") == "human":
            last_human_idx = i
            break

    # Only look at messages AFTER the last HumanMessage
    recent_messages = messages[last_human_idx + 1:] if last_human_idx is not None else []

    # Step 1: Was linkedin_job_search called in this exchange?
    job_search_tool_id = None
    for msg in recent_messages:
        if getattr(msg, "type", "") == "ai":
            for tool_call in getattr(msg, "tool_calls", []):
                if tool_call.get("name") == "linkedin_job_search":
                    job_search_tool_id = tool_call.get("id")

    # Step 2: If yes, find its ToolMessage result
    job_tool_result = None
    if job_search_tool_id:
        for msg in recent_messages:
            if getattr(msg, "type", "") == "tool" and getattr(msg, "tool_call_id", "") == job_search_tool_id:
                try:
                    job_tool_result = json.loads(msg.content)
                except:
                    job_tool_result = None
                break

    # Step 3: Only return cards if tool ran AND returned type "jobs"
    if job_tool_result and job_tool_result.get("type") == "jobs":
        return {
            "response_type": "jobs",
            "jobs": job_tool_result["jobs"],
            # "text": ai_text
        }

    return {"response_type": "text", "text": ai_text}