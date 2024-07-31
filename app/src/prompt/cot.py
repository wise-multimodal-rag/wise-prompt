from langchain_core.prompts import ChatPromptTemplate

from app.src.ollama import model


def cot_prompt(request):
    template = """Question: {question}
    
    {magic_sentence}
    
    Answer: """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    result = chain.invoke(
        {"question": request.prompt,
         "magic_sentence": "Let's work this out in a step by step way to be sure we have the right answer."}
    )
    return result.content


def auto_cot_prompt(request):
    pass
