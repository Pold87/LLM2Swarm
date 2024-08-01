from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


with open('mapmsg.txt', 'r') as file:
    # Read the content of the file and store it in the variable template
    template = file.read()

template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer:
"""

def handle_conversation():
    context = ""
    print("Welcome to the AI chatbot. Type exit to quit.")
    while True:
        user_input = input("You: ")
        
        result = chain.invoke({"context": context,
                       "question": user_input})
        
        print("Bot: ", result)

        context += f"\nUser: {user_input}\nAI: {result}"



model = OllamaLLM(model="phi3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model


if __name__ == "__main__":
    handle_conversation()