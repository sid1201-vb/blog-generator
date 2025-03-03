from .call_llm import send_request_to_llm
import json
get_search_phrase_prompt=""" 
Given a question, I'll provide you with a concise search phrase that will help you find the answer on a search engine.

Question: {question}

I'll return the result in this format:
{{
  "search_phrase": "[Optimized search phrase]"
}}

- Return only JSON with no explaination or comments.
- Do not wrap the json in backticks.
- No markdown formatting is allowed.

"""

def get_search_phrase(question:str)->str:
    global get_search_phrase_prompt
    formatted_prompt = get_search_phrase_prompt.format(question=question)
    response = send_request_to_llm(formatted_prompt=formatted_prompt)
    response = json.loads(response)
    return response["search_phrase"]


def get_search_phrase_list(question_list:list)->list[str]:
    search_phrases = []
    for question in question_list:
        phrase = get_search_phrase(question)
        search_phrases.append(phrase)
    return search_phrases