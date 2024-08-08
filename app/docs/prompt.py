from app.constants import PromptTemplate
from app.models import SelfConsistencyRequest, Request, LLMProviderRequest, AutoCoTRequest, ReActRequest

OPENAI_LLM_TOOL = "OpenAI"
OPENAI_DEFAULT_MODEL = "gpt-4o-mini"

ollama_default_example = {
    "summary": "Ollama default prompting 기본 예제",
    "description": "Ollama 기본 프롬프트 기법 예제",
    "value": Request(prompt="이 그룹의 홀수의 합은 짝수야: 15, 32, 5, 13, 82, 7, 1.\nA: ")
}
openai_default_example = {
    "summary": "OpenAI default prompting 기본 예제",
    "description": "OpenAI 기본 프롬프트 기법 예제",
    "value": Request(system_prompt="너는 아주 훌륭한 수학선생님이야. 학생들의 질문에 친절하게 답변해줘.",
                     prompt="이 그룹의 홀수의 합은 짝수야: 15, 32, 5, 13, 82, 7, 1.\n"
                            "위 문장이 참인지 거짓인지 알려주세요!",
                     llm_provider=LLMProviderRequest(llm_tool=OPENAI_LLM_TOOL, model=OPENAI_DEFAULT_MODEL))
}
default_prompt_examples = {
    "ollama_default": ollama_default_example,
    "openai_defualt": openai_default_example
}

ollama_auto_cot_example = {
    "summary": "Ollama Auto-CoT prompting 기본 예제",
    "description": "Ollama Auto-CoT 프롬프트 기법 예제",
    "value": AutoCoTRequest(prompt="이 그룹의 홀수의 합은 짝수야: 15, 32, 5, 13, 82, 7, 1.\nA: ")
}
openai_auto_cot_example = {
    "summary": "OpenAI Auto-CoT prompting 기본 예제",
    "description": "초등학교 3학년 수학문제 예제",
    "value": AutoCoTRequest(system_prompt="너는 아주 훌륭한 수학선생님이야. 해당 수학문제를 정확한 알려줘.",
                            prompt="호박의 무게가 5kg 800g, 사과의 무게가 180g입니다. 호박과 사과의 무게는 모두 몇 kg 몇 g입니까?",
                            llm_provider=LLMProviderRequest(llm_tool=OPENAI_LLM_TOOL, model=OPENAI_DEFAULT_MODEL))
}
auto_cot_examples = {
    "ollama_auto_cot": ollama_auto_cot_example,
    "openai_auto_cot": openai_auto_cot_example,
}

self_consistency_prompt = """Q: The school cafeteria had 23 apples. If they used 20 to make lunch for the students and then bought 6 more, how many apples would they have?
        A: The school cafeteria had 23 apples. If they used 20 to make lunch for the students and then bought 6 more, How many apples would they have? The school cafeteria would have 23 + 6, or 29, apples. 
        Therefore, the answer (arabic numerals) is 29.
        
        Q: Nancy picked 12 carrots from her garden. If she threw out 2 of them and then picked 21 more the next day, how many carrots would she have total?
        A: Nancy picked 12 carrots from her garden. So she has 12 carrots. If she threw out 2 of them, she would have 10 carrots. If she picked 21 more the next day, she would have 21 carrots. So she would have 10 + 21 = 31 carrots in total.
        Therefore, the answer (arabic numerals) is 31.
        
        Q: Roger had 25 books. If he sold 21 of them and used the money he earned to buy 30 new books, how many books would Roger have?
        A: Roger had 25 books. He sold 21 of them. That means he has 4 books left. He used the money he earned to buy 30 new books. That means he has 34 books in total. 
        Therefore, the answer (arabic numerals) is 34.
        
        Q: At the fair there were 12 people in line for the bumper cars. If 10 of them got tired of waiting and left and 15 more got in line, how many people would be in line?
        A: There were 12 people in line for the bumper cars. 10 of them got tired of waiting and left. 15 more got in line. That means that there are now 15 people in line for the bumper cars. 
        Therefore, the answer (arabic numerals) is 15.
        
        Q: While playing a trivia game, George answered 6 questions correct in the first half and 4 questions correct in the second half. If each question was worth 3 points, what was his final score?
        A:"""
ollama_self_consistency_example = {
    "summary": "Ollama Self-Consistency prompting 기본 예제",
    "description": "Multiarith Zero-shot 예제 중 일부를 Few-shot 예제로 가져옴 (정답: 30)",
    "value": SelfConsistencyRequest(
        system_prompt=PromptTemplate.SYSTEM_PROMPT,
        prompt=self_consistency_prompt,
    )
}
openai_self_consistency_example = {
    "summary": "OpenAI Self-Consistency prompting 기본 예제",
    "description": "Multiarith Zero-shot 예제 중 일부를 Few-shot 예제로 가져옴 (정답: 30)",
    "value": SelfConsistencyRequest(
        system_prompt=PromptTemplate.SYSTEM_PROMPT,
        prompt=self_consistency_prompt,
        llm_provider=LLMProviderRequest(llm_tool=OPENAI_LLM_TOOL, model=OPENAI_DEFAULT_MODEL),
        num=3
    )
}
self_consistency_examples = {
    "ollama_self_consistency": ollama_self_consistency_example,
    "openai_self_consistency": openai_self_consistency_example,
}

ollama_react_example = {
    "summary": "Ollama ReAct prompting 기본 예제",
    "description": "Ollama ReAct 프롬프트 기법 예제",
    "value": ReActRequest(system_prompt="""You an intelligent assistant specialized in helping users solve complex problems through reasoning and action. Your goal is to assist the user by providing accurate information, clear explanations, and actionable steps. Follow these guidelines:

1. Carefully read the user's query and identify the key issues or questions.
2. Break down complex problems into manageable parts and explain your reasoning process clearly.
3. Provide step-by-step instructions or solutions when necessary.
4. If additional information is needed from the user, ask clarifying questions.
5. Avoid making assumptions or providing incorrect information. If unsure, state the limitations or suggest alternative resources.

Example interaction:
User: How can I improve my productivity at work?
Bot: Improving productivity at work involves several strategies:
1. Prioritize tasks: Identify the most important tasks and tackle them first.
2. Time management: Use tools like calendars or to-do lists to organize your day.
3. Minimize distractions: Set specific times for checking emails and avoid social media during work hours.
4. Take breaks: Short breaks can help maintain focus and prevent burnout.
5. Seek feedback: Regularly ask for feedback from colleagues or supervisors to identify areas for improvement.

If you have any specific concerns or need detailed advice on a particular aspect, please let me know!""",
                          prompt="신데렐라의 결말은 뭐야?")
}
openai_react_example = {
    "summary": "OpenAI ReAct prompting 기본 예제",
    "description": "OpenAI ReAct 프롬프트 기법 예제",
    "value": ReActRequest(system_prompt="""You are ChatGPT, an intelligent assistant specialized in helping users solve complex problems through reasoning and action. Your goal is to assist the user by providing accurate information, clear explanations, and actionable steps. Follow these guidelines:

1. Carefully read the user's query and identify the key issues or questions.
2. Break down complex problems into manageable parts and explain your reasoning process clearly.
3. Provide step-by-step instructions or solutions when necessary.
4. If additional information is needed from the user, ask clarifying questions.
5. Avoid making assumptions or providing incorrect information. If unsure, state the limitations or suggest alternative resources.

Example interaction:
User: How can I improve my productivity at work?
ChatGPT: Improving productivity at work involves several strategies:
1. Prioritize tasks: Identify the most important tasks and tackle them first.
2. Time management: Use tools like calendars or to-do lists to organize your day.
3. Minimize distractions: Set specific times for checking emails and avoid social media during work hours.
4. Take breaks: Short breaks can help maintain focus and prevent burnout.
5. Seek feedback: Regularly ask for feedback from colleagues or supervisors to identify areas for improvement.

If you have any specific concerns or need detailed advice on a particular aspect, please let me know!""",
                          prompt="신데렐라의 결말은 뭐야?",
                          llm_provider=LLMProviderRequest(llm_tool=OPENAI_LLM_TOOL, model=OPENAI_DEFAULT_MODEL))
}
react_examples = {
    "ollama_self_react": ollama_react_example,
    "openai_self_react": openai_react_example
}
