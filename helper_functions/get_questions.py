import json
from .call_llm import send_request_to_llm

topic_to_ques = """
Given the following topic:
{topic}

Generate a comprehensive set of 2 questions that would help determine if a blog thoroughly covers this topic. Consider questions about definitions, implementations, best practices, common challenges, use cases, and comparisons.

Return only a JSON object with an array of questions, without any additional explanations. The output should be in this format:
{{
    "questions": [
        {{"question": "What is {topic}?"}},
        {{"question": "How do you implement {topic}?"}},
        ...
    ]
}}

No explanations or additional text should be included in the response.
Do not generate more than 2 questions.
"""

def get_questions_for_topic_list(topic_list):
    quest_list = []
    for topic in topic_list:
        formatted_prompt = topic_to_ques.format(topic=topic)
        res = json.loads(send_request_to_llm(formatted_prompt))
        for i in res["questions"]:
            quest_list.append(i["question"])
            print(i["question"])
    return quest_list