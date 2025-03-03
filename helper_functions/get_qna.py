from .call_llm import send_request_to_llm
from .chroma_search import ChromaSearch 

blog_q_n_a = """ 
## Instruction
You are a helpful assistant that answers questions about blog content. You will receive a question and context from multiple blogs. Your task is to determine if the question can be answered based on the provided context.

If the answer is present in the context:
- Extract the relevant information that answers the question
- Provide the answer in a clear, concise manner

If the answer is not present in the context:
- Return "Not Found"

## Question
{question}

## Context
{context}

## Response Format
Return your response in JSON format without backticks or markdown formatting as follows:

{{
  "question": "[The original question]",
  "answer": "[Your answer or 'Not Found' if not present in context]"
}}

## Guidelines
- Only use information provided in the context to answer the question
- Do not make up information or use external knowledge
- If multiple blog contexts contain relevant information, combine them for a complete answer
- Keep answers concise and relevant
- Maintain the exact JSON format specified above - no backticks, no markdown formatting
- The JSON should be valid and properly formatted
"""


import json
def get_qna_list(quest_list, hyb: ChromaSearch):
    q_n_a_list = []
    
    for question in quest_list:
        context = hyb.search(question, 6, "all")
        print(context)
        context_str = ""
        for j in context:
            context_str += j["document"] + "\n\n"
        print(context_str)
        
        formatted_prompt = blog_q_n_a.format(question=question, context=context_str)
        res = json.loads(send_request_to_llm(formatted_prompt))
        if res["answer"].lower() != "not found":
            q_n_a_list.append(res)
    return q_n_a_list