import chainlit as cl
import os
from langchain import OpenAI
from langchain.agents import initialize_agent, Tool, ZeroShotAgent, agent_types

from utils.research_papers import ResearchWrapper

@cl.on_chat_start
def start():
    llm_chain = OpenAI(temperature=0, streaming=True)
    research = ResearchWrapper()

    tools = [  
        Tool(
            name="ResearchPapers",
            func=research.research_papers, 
            description="useful for when you need to find information research papers. "
        ),
        Tool(
            name="ResearchPapersSummary",
            func=research.research_papers_summary, 
            description="Useful for when you need to find summary information on research papers. "
        )     
    ]

    agent = initialize_agent(
        tools, llm_chain, agent=agent_types.AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )
    cl.user_session.set("agent", agent)

@cl.on_message
async def main(message):
    answer_prefix_tokens=["Final Answer:"]
    agent = cl.user_session.get("agent")  # type: AgentExecutor
    cb = cl.LangchainCallbackHandler(stream_final_answer=True, answer_prefix_tokens=answer_prefix_tokens,)

    res = await cl.make_async(agent.run)(message, callbacks=[cb])
    await cl.Message(content=res).send()
