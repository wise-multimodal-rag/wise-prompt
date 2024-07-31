from langchain_community.chat_models import ChatOllama

# TODO: ollama 환경변수 설정 or MODELFILE (https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values)
ollama_base_url = "http://61.82.137.170:11434"
ollama_model_name = "llama3"
model = ChatOllama(base_url=ollama_base_url, model=ollama_model_name)
