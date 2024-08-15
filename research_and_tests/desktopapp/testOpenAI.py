from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

model = ChatOpenAI(model="gpt-4o-mini")




def main():
	messages = [
		HumanMessage("Hello! Who am i speaking to?"),
	]

	result = model.invoke(messages)

	print(result)
	return

#Main
if __name__ == "__main__":
	main()
