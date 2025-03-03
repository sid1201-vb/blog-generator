from typing import List
from .call_llm import send_request_to_llm

topic_list_prompt = """
Generate a list of the top 5 underserved blog topics of {topic} with high 
search volume and low competition. Return the results in JSON format with each 
topic as an object containing the topic name and primary keyword only. 
No explanations or additional text should be included in the response. 
Example format: 
{{
  "topics": [
    {{
      "topic": "Topic 1",
      "primary_keyword": "keyword 1"
    }},
    {{
      "topic": "Topic 2",
      "primary_keyword": "keyword 2"
    }}
  ]
}}

 
 - give only valid json
 - do not enclose json in backticks or double quotes
 - markdown formatting is not allowed
"""

import json
def get_underserved_blog_topics(topic:str) -> List[str] :
    global topic_list_prompt
    formatted_prompt = topic_list_prompt.format(topic=topic)
    response = json.loads(send_request_to_llm(formatted_prompt))
    topic_list = []
    for i in response["topics"]:
        topic_list.append(i["topic"])
    return topic_list