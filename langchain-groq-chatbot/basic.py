from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.0,
    max_retries=2,
)

while True:
    prompt = input("User Input: ")
    if prompt.strip().lower() == "exit":
        break

    response = model.invoke(prompt)
    print("AI:", response.content)

