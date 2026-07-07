
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

import os


from tools import (
    feedback_search,
    sql_query,
    sentiment_analysis,
    compare_lecturers,
    recommend_lecturer,
    save_message,
    load_history
   
)


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key="GOOGLE_API_KEY",
    temperature=0
)

system_prompt = """
You are a College Feedback Assistant.

You have access to these tools.

1. sql_query
Use for:
- average rating
- pass percentage
- fail percentage
- attendance
- marks
- highest rating
- lowest rating
- count
- subjects
- semester
- lecturer information

IMPORTANT:
Always pass the USER'S ORIGINAL QUESTION to sql_query.
Do NOT rewrite or summarize the question.

Example:
User: What is the pass percentage?
Tool:
sql_query(question="What is the pass percentage?")

Example:
User: What is the average rating of Ajay Yadav?
Tool:
sql_query(question="What is the average rating of Ajay Yadav?")

2. feedback_search
Use whenever the user asks about:
- comments
- reviews
- feedback
- opinions
- teaching quality

Pass the complete user question.

3. sentiment_analysis
Use when the user wants a summary of feedback for a lecturer.

4. compare_lecturers
Use only when the user compares two lecturers.

5. recommend_lecturer
Use only when the user asks for a recommendation.

Never answer from your own knowledge.
Always use a tool.


"""

agent = create_agent(
    model=llm,
    tools=[
        feedback_search,
        sql_query,
        sentiment_analysis,
        compare_lecturers,
        recommend_lecturer,
    ],
    system_prompt=system_prompt,
)


def ask_agent(session_id, user_question):

    history = load_history(session_id)

    messages = [("system", system_prompt)]

    for role, message in history:
        messages.append((role, message))

    messages.append(("user", user_question))

    response = agent.invoke({"messages": messages})

    print("=" * 80)

    tool_used = "No Tool"

    for i, msg in enumerate(response["messages"]):
        print(f"\nMessage {i}")
        print(type(msg))
        print(msg)

        # Detect the tool that was called
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            tool_used = msg.tool_calls[0]["name"]

    print("=" * 80)

    answer = response["messages"][-1].content

    save_message(session_id, "user", user_question)
    save_message(session_id, "assistant", answer)

    return answer, tool_used