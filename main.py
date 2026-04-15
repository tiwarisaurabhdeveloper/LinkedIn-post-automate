from langchain.agents import create_agent
from model_load import load_llm
from linkedin_tool import linkedin_text_post
from langgraph.checkpoint.memory import InMemorySaver
checkpointer=InMemorySaver()

linkedin_prompt="""
            you are Intelligence to make a post according to the user input topic you can do Generate a new post.
            instruction : 
                1. According to the user input topic Generate the post describe the topic and also add hastag(5-10) at the end of the post related topic.
                        Then verify to the user with *generated post* APPROVE for post or edit in this somethings let me know.
                        If user want to change or edit in the generated post then ask to user what kind of things you want to change. once you get the then modify the post and ask to user again approve for post or you want to change.
                2. Generated post Should be in the professional post formated with some dot and ne lines for better visual.
            Tool Calling Selection:
                IF User *APPROVE* then call this 'linkedin_text_post' tool with <generated post> .
            """
main_agent=create_agent(
    model=load_llm(),
    system_prompt=linkedin_prompt,
    tools=[linkedin_text_post],
    checkpointer=checkpointer
)



CONFIG={"configurable":{"thread_id":"t1"}}
while True:
    user_input=input("you: ")
    if user_input in ["exit","bye"]:
        break
    result= main_agent.invoke({"messages":[{"role":"user","content":user_input}]},config=CONFIG)
    response=result['messages'][-1].content
    print("assistant: ",response)
