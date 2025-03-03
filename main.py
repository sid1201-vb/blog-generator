from helper_functions.get_topic_list import get_underserved_blog_topics
from helper_functions.get_questions import get_questions_for_topic_list
from helper_functions.get_search_phrase import get_search_phrase_list
from helper_functions.get_url_with_playwright import get_url_list
from helper_functions.get_url_content import save_webpages
from helper_functions.embed_docs import get_markdown_files, embed
from helper_functions.chroma_search import get_chroma_hybrid_search
from helper_functions.get_qna import get_qna_list
from helper_functions.generate_blog import write_blog_post, increase_word_count, optimize_blog
import os
## take inputs
purpose = " Traffic generation, Lead generation"
target_audience = "drupal users"
pain_points = ["Code quality and maintainability", "Development process efficiency","Knowledge transfer and documentation"]

primary_keywords = ["drupal", "drupal seo", "drupal 10 end of life", "best seo tool for drupal", "drupal to wordpress migration", "migrating from drupal​", "drupal migration services", "drupal 7 to 10 migration", "drupal migrate module", "audit drupal", "drupal web development services", "drupal web development company", "drupal 10 module developmen", "drupal website development company​"]
secondary_keywords = ["drupal 9 end of life"]

search_intent = "Transactional, Navigational"
competitors_urls = [
"https://www.herodevs.com/blog-posts/top-3-strategies-for-managing-drupal-7-end-of-life#:~:text=With%20Drupal%207%20EOL%20on%20January%205%2C%202025%2C,...%203%203.%20Prioritize%20Security%20Patches%20and%20Updates",
"https://www.bing.com/search?pglt=417&q=Risk-Free+Drupal+7+Migration+Strategies&cvid=366ef32d8cfb4600ad5eac3a92bbcd68&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOTIGCAEQABhAMgYIAhAAGEAyBggDEAAYQDIGCAQQABhAMgYIBRAAGEAyBggGEAAYQDIGCAcQABhAMgYICBAAGEDSAQgxMzI3ajBqMagCALACAA&FORM=ANNTA1&PC=SMTS",
"https://www.thedroptimes.com/43206/six-migration-options-drupal-7-end-life-in-2025"
]

topic = "AI agents replacing software developers"


# # get topic list
topic_list = get_underserved_blog_topics(topic)


# ## get questions
question_list = get_questions_for_topic_list(topic_list=topic_list)

# get search phrases
search_list = get_search_phrase_list(question_list)

## find URLs
url_list = get_url_list(search_phrases=search_list)
print(url_list)

## get all url contents
## clean content
save_webpages(url_list)

## create embeddings
chroma = get_chroma_hybrid_search("blogs_data")
chroma.clear_collection()
mkdwn_paths = get_markdown_files("blogs")
for path in mkdwn_paths:
    embed(path, chroma)

chroma._load_persisted_data()


## generate qna
qna_list = get_qna_list(question_list, chroma)

## give qna to generate blog
first_draft = write_blog_post(purpose,target_audience=target_audience,pain_points=pain_points,primary_keywords=primary_keywords,secondary_keywords=secondary_keywords, search_intent=search_intent,qna_list=qna_list, topic=topic)


## modify blog to be longer
second_draft = increase_word_count(first_draft,keywords=primary_keywords)


## give persona to blog
final_draft = optimize_blog(blog=second_draft, primary_keywords=primary_keywords)

# os.makedirs(f"{topic.replace(" ","-")}.md", exist_ok=True)
with open(f"{topic.replace(" ","-")}.md", "w", encoding="utf-8") as f:
    f.write(final_draft)