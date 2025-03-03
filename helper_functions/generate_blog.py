from .call_llm import send_request_to_llm
import json

write_blog_prompt = """
Create a high-ranking, engaging, and SEO-optimized blog post based on the information below.

PURPOSE: {purpose}
TARGET AUDIENCE: {target_audience}
PAIN POINTS: {pain_points}
SEARCH INTENT: {search_intent}
TOPIC: {topic}
QUESTIONS & ANSWERS: 
{q_n_a_list}
PRIMARY KEYWORD: {primary_keywords}
SECONDARY KEYWORDS: {secondary_keywords}

Please create a complete blog post with:

1. A catchy headline under 55 characters that includes the primary keyword
2. An engaging introduction with a hook (question/stat/pain point), problem statement, and value proposition
3. A table of contents if the post exceeds 2,000 words
   - Link table of content with other sections of the blog.
4. Main body content with:
   - Keyword-rich H2 and H3 subheadings
   - Short paragraphs (1-3 sentences)
   - Bullet points and numbered lists
   - Data, statistics, and examples
   - Relevant internal and external links (suggested placeholders)
   - Image placement suggestions
5. Compelling CTAs throughout
6. A conclusion with key takeaways and next steps
7. SEO elements:
   - Meta description (155-160 characters)
   
   

Use a conversational, engaging, human-like tone with formatting for emphasis. Focus on providing actionable value and use storytelling techniques where appropriate. Make the content scannable, credible, and valuable to the target audience.

"""


def write_blog_post(purpose, target_audience, pain_points, search_intent, topic, qna_list, primary_keywords, secondary_keywords):
    formatted_prompt = write_blog_prompt.format(purpose=purpose, target_audience=target_audience, pain_points=pain_points, search_intent=search_intent, topic=topic, q_n_a_list=qna_list, primary_keywords=primary_keywords, secondary_keywords=secondary_keywords)
    response = send_request_to_llm(formatted_prompt)
    return response


########################################################################

optimizing_prompt = """
Act as Neil Patel, the renowned SEO and content marketing expert from Ubersuggest. I need you to optimize my blog post to achieve high scores on SEO Review Tools content analysis. Please transform the following blog post while maintaining a natural, human-written feel:

1. KEYWORD OPTIMIZATION:
   - Ensure primary keywords appear in the first 100 words
   - Maintain ideal keyword density (1.5-2.5%) without keyword stuffing
   - Include keywords naturally in headings, especially H2s

2. CONTENT STRUCTURE:
   - Create a compelling H1 headline (65-70 characters) with primary keyword
   - Organize content with proper H1, H2, H3, and H4 hierarchy
   - Keep all paragraphs under 300 characters for readability
   - Ensure 40-60% of sentences are under 20 words for better readability scores
   - Include numbered and bulleted lists where appropriate 
   - Link Table of contents with other sections of the blog

3. ENGAGEMENT ELEMENTS:
   - Add compelling questions throughout to improve engagement metrics
   - Create a strong introduction with a hook, problem statement, and solution promise
   - Include transition phrases between sections
   - Add a compelling call-to-action at the end
   - Incorporate statistics or data points with citations


4. READABILITY IMPROVEMENTS:
   - Simplify complex sentences to achieve 60-70 Flesch Reading Ease score
   - Break up text walls with strategic headings
   - Convert passive voice to active voice where possible
   - Ensure variety in sentence beginnings
   - Use power words and emotional triggers strategically

5. Meta Description:
   - Create a meta description (150-160 characters) with primary keyword
   
Maintain my original ideas and voice while making these improvements. Use Neil's conversational yet authoritative style - approachable, data-driven, and with occasional personal insights.

Here's my blog post:
{blog_draft}

Primary Keywords:
{keywords}



"""


complete_blog_prompt = """
You are tasked with completing text that was cut off due to token limitations in a previous generation attempt. Your goal is to analyze the incomplete text, understand its content and intended direction, and provide ONLY the continuation from the exact point where it was cut off.

INPUT:
The following is an incomplete blog that needs to be continued from the last sentence:
{json_blog}

INSTRUCTIONS:
1. Carefully examine the content and identify exactly where the text was cut off
2. Generate ONLY the remaining text that would naturally continue from that point
3. Maintain consistency with the style, tone, and format of the existing content
4. Do not repeat or restate any content that is already present in the input
5. Begin your response exactly where the input text ended (after the last complete sentence)
6. Ensure your continuation flows naturally from the existing content
7. Return only the text continuation without any explanatory comments
8. Format the output as valid JSON content (properly escaped)

OUTPUT:
{{
   "optimized_blog": "YOUR CONTINUATION TEXT ONLY"
}}

- Do not wrap json in backticks.
- Do not include any markdown formatting.
- Do not regenerate or repeat any content from the input.
- Only provide the text that would logically follow after the last complete sentence.
"""

def optimize_blog(blog, primary_keywords, max_retries=3):
    global optimizing_prompt
    optimize_blog_prompt_formatted = optimizing_prompt.format(blog_draft=blog, keywords=primary_keywords)
    
    for attempt in range(max_retries):
        optimized_blog = send_request_to_llm(optimize_blog_prompt_formatted)
        try:
            optimized_blog_dic = json.loads(optimized_blog)
            return optimized_blog_dic["optimized_blog"]
        except json.JSONDecodeError:
            if attempt == max_retries - 1:
                raise ValueError("Failed to retrieve a valid JSON response from LLM after multiple attempts.")
            return complete_remaining_blog(optimized_blog)
    
    return None

def complete_remaining_blog(optimized_blog):
   global complete_blog_prompt
   complete_blog_prompt_formatted = complete_blog_prompt.format(json_blog=optimized_blog)

   remaining_text_json = send_request_to_llm(complete_blog_prompt_formatted)
   remaining_text = json.loads(remaining_text_json)["optimized_blog"]
   optimized_blog += remaining_text 
   return optimized_blog
   
   


blog_increse_template = """ 
# Blog Completion Prompt Template

## Instructions
Please complete the following blog article draft by expanding it to approximately 1500 words. Use the provided keywords to guide your content development while maintaining the tone, style, and theme of the original draft.

## Article Draft
{article_draft}

## Keywords
{keywords}

## Requirements
1. Maintain the original voice and writing style
2. Expand the article to approximately 1200 words
3. Incorporate all the provided keywords naturally
4. Ensure logical flow between the existing content and your additions
5. Add appropriate section headings if needed
6. Include a strong conclusion that ties back to the introduction
7. Keep the content informative and engaging

Please complete the blog while preserving any existing formatting, links, or special elements in the markdown.

"""

def increase_word_count(blog, keywords):
    global blog_increse_template
    inc_word_prompt = blog_increse_template.format(article_draft=blog, keywords=keywords)
    inc_blog = send_request_to_llm(inc_word_prompt)
    return inc_blog