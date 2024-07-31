from langchain_core.prompts import ChatPromptTemplate

from app.src.ollama import model


def default_prompt(request):
    template = """Question: {question}"""
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    result = chain.invoke({"question": request.prompt})
    return result.content
