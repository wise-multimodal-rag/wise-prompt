from typing import Final

from langchain_core.prompts import ChatPromptTemplate


class ModelOption:
    TEMPERATURE: float = 0.5
    TOP_K: float = 40


class MagicSentence:
    COT_DEFAULT_MAGIC_SENTENCE: Final[str] = "Let's think step by step."
    COT_ADVANCED_MAGIC_SENTENCE: Final[
        str] = "Let's work this out in a step by step way to be sure we have the right answer."


# TODO: 최적화된 한국어 템플릿으로 변경 (답변을 한국어로 통일) OR 영어와 한국어를 판단해서 번역해서 하나의 언어로 사용?
class PromptTemplate:
    # TODO: 정해진 형식 추출하는 과정 공통으로 빼기
    # TODO: SYSTEM_PROMPT 어떻게 설정하면 좋은 답변이 나오는가? (페르소나)
    SYSTEM_PROMPT = """You are a very kind and smart robot who can speak Korean and English. 
    Answers must always be in Korean."""
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
         """If necessary, please translate the following sentence into Korean or just post the following sentence.: {text}""")])


class APETemplate:
    # TODO: ChatPromptTemplate 패턴으로 변경 ([] -> {})
    ZERO_SHOT_EVALUATION: str = """Instruction: [PROMPT]
    Input: [INPUT]
    Output: [OUTPUT]"""
    INSTRUCTION_WITH_FEW_SHOT: str = """Instruction: [PROMPT]

[full_DEMO]

Input: [INPUT]
Output: [OUTPUT]"""
    DEMO_TEMPLATE: str = """Input: [INPUT]
Output: [OUTPUT]"""
    PROMPT_GENERATE_TEMPLATE: str = "I gave a friend an instruction. Based on the instruction they produced the following input-output pairs:\n\n[full_DEMO]\n\nThe instruction was to [APE]"


SUMMARY = "AI플랫폼팀 Prompt Engineering 🚀"
DESCRIPTION = """### 프롬프트 엔지니어링 기법\n
- _Default_
- CoT (Chain-of-Thought)
    - _Zero-shot CoT_
    - _Auto-CoT (Automatic Chain-of-Thought)_
- _Self-Consistency_
- _ReAct_\n

### 주의사항
- **OpenAI의 경우, 과금이 발생할 수 있으니 주의바랍니다.**
- Ollama 모델은 한국어에 미흡합니다.
- 현재 개발된 방법론은 대부분 OpenAI 모델에 맞춰져 있어 타사의 모델을 사용할 경우 결과가 제대로 나오지 않을 수 있습니다.
- 모델의 입력 토큰 제한에 따라 프롬프트가 제대로 입력되지 않을 수 있습니다.
"""

LICENSE_INFO = {
    "name": "Wisenut"
}
