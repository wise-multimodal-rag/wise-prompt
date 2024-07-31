from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate

from app.src.ollama import model


def react_prompt(request):
    tools = [TavilySearchResults(max_results=1)]
    template = """Answer the following questions as best you can. You have access to the following tools:

                {tools}

                Use the following format:

                Question: the input question you must answer
                Thought: you should always think about what to do
                Action: the action to take, should be one of [{tool_names}]
                Action Input: the input to the action
                Observation: the result of the action
                ... (this Thought/Action/Action Input/Observation can repeat N times)
                Thought: I now know the final answer
                Final Answer: the final answer to the original input question

                Begin!

                Question: {input}
                Thought:{agent_scratchpad}
                """
    prompt = ChatPromptTemplate.from_template(template)
    agent = create_react_agent(model, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    result = agent_executor.invoke(
        {"question": request.prompt,
         "magic_sentence": "Let's work this out in a step by step way to be sure we have the right answer."}
    )
    return result
