import dotenv
import time
import os
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(
    api_key=OPEN_AI_API_KEY,
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def send_request_to_llm(formatted_prompt) -> str:
    retries = 3

    for attempt in range(retries):
        try:
            # Increment the LLM call counter in Redis

            res = model.invoke(formatted_prompt)
            print(res)
            return res.content

        except Exception as e:
            print(f"Error while calling LLM on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                print("Retrying in 3 seconds...")
                time.sleep(3)

    print("LLM call failed after 3 retries")
    return "LLM call failed"


send_request_to_llm("what is the capital of France?")