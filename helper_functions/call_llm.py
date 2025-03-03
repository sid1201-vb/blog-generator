from langchain_openai import AzureChatOpenAI
import dotenv
import time
import os
dotenv.load_dotenv()


AZURE_OPENAI_API_KEY=os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_MODEL_VERSION=os.getenv("OPENAI_MODEL_VERSION")


model = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version=OPENAI_MODEL_VERSION,
    temperature=0.75,
    max_tokens=2056,
    max_retries=100,
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def send_request_to_llm(formatted_prompt) -> str:
    retries = 3

    for attempt in range(retries):
        try:
            print("calling LLM", AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_MODEL_VERSION)
            # Increment the LLM call counter in Redis

            res = model.invoke(formatted_prompt)
            print(type(res), res.content)
            return res.content

        except Exception as e:
            print(f"Error while calling LLM on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                print("Retrying in 3 seconds...")
                time.sleep(3)

    print("LLM call failed after 3 retries")
    return "LLM call failed"


send_request_to_llm("hi")