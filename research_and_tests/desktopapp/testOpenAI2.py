from langchain_openai import ChatOpenAI
from app import Clip
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.tools import tool





model = ChatOpenAI(model="gpt-4o")

chain = model | StrOutputParser()

chat_history = InMemoryChatMessageHistory()

def get_history() -> InMemoryChatMessageHistory:
    return chat_history

@tool
def transcribe_audio(audio):
	audio_file = open(audio, "rb")
    

def main():
	system_prompt = "Transcribe the following audio clip, where the clip is always in chilean spanish. If you can separate the speakers, please do so."
	messages = [
    SystemMessage(system_prompt),
    HumanMessage("I want to transcribe this audio clip", chat_history=chat_history),
	]

	result = chain.invoke(messages)
	print(result)

#Main
if __name__ == "__main__":
	main()


