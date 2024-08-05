from typing import Final

from langchain_core.prompts import ChatPromptTemplate


class ModelOption:
    TEMPERATURE: float = 0.5
    TOP_K: float = 40


class MagicSentence:
    COT_DEFAULT_MAGIC_SENTENCE: Final[str] = "Let's think step by step."
    COT_ADVANCED_MAGIC_SENTENCE: Final[
        str] = "Let's work this out in a step by step way to be sure we have the right answer."


class PromptTemplate:
    # TODO: 정해진 형식 추출하는 과정 공통으로 빼기
    # TODO: SYSTEM_PROMPT 어떻게 설정하면 좋은 답변이 나오는가? (페르소나)
    SYSTEM_PROMPT = """You are a very smart and kind Robot."""
    DEFAULT = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        ("human", "Question: {prompt}")
    ])
    COT = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        ("human", """Question: {prompt}
    
    {magic_sentence}
    
    Answer: """)
    ])
    AUTO_COT = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        ("human", """{examples}
    Question: {prompt}
    Answer: {magic_sentence}
    """)
    ])
    SELF_CONSISTENCY = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        ("human", """{magic_sentence}
    Please answer in JSON format. 
    Please respond in the following format : ("reasoning_chain": [reasoning chain], "answer": {answer})
    Please answer with only one number or one word in JSON 'answer' key. Example: '42' or 'Yes'.
    
    Question: {prompt}
    Answer: """)])
    REACT = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        ("human", """Answer the following questions as best you can. You have access to the following tools:

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
                """)])
    GET_JSON_VALUE = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        ("human", """JSON Object: {json_object}
    Get the Data from {key} key
    Please answer with only one number or one word in JSON 'answer' key. Example: '42' or 'Yes'.
    
    Value: 
    """)])
    TRANSLATE = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        ("human",
         """If necessary, please translate the following sentence into Korean Or just post the following sentence.: {text}""")])
