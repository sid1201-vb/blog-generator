import gradio as gr
import os
import uuid
from helper_functions.get_topic_list import get_underserved_blog_topics
from helper_functions.get_questions import get_questions_for_topic_list
from helper_functions.get_search_phrase import get_search_phrase_list
from helper_functions.get_url_with_playwright import get_url_list
from helper_functions.get_url_content import save_webpages
from helper_functions.embed_docs import get_markdown_files, embed
from helper_functions.chroma_search import get_chroma_hybrid_search
from helper_functions.get_qna import get_qna_list
from helper_functions.generate_blog import write_blog_post, increase_word_count, optimize_blog
import shutil

def delete_folder(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        print(f"Deleted folder: {folder_path}")
    else:
        print(f"Folder does not exist: {folder_path}")
        
def delete_file(file_path):
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    else:
        print(f"File does not exist: {file_path}")

def generate_blog(
    purpose, 
    target_audience, 
    pain_points_text, 
    primary_keywords_text, 
    secondary_keywords_text, 
    search_intent, 
    competitors_urls_text, 
    topic, 
    progress=gr.Progress()
):
    # Convert text inputs to appropriate formats
    pain_points = [p.strip() for p in pain_points_text.split(",") if p.strip()]
    primary_keywords = [k.strip() for k in primary_keywords_text.split(",") if k.strip()]
    secondary_keywords = [k.strip() for k in secondary_keywords_text.split(",") if k.strip()]
    competitors_urls = [url.strip() for url in competitors_urls_text.split("\n") if url.strip()]
    blog_id = str(uuid.uuid4().int)[:6]
    
    
    # Progress tracking
    progress(0, "Getting topic list...")
    topic_list = get_underserved_blog_topics(topic)
    
    progress(0.1, "Generating questions...")
    question_list = get_questions_for_topic_list(topic_list=topic_list)
    
    progress(0.2, "Creating search phrases...")
    search_list = get_search_phrase_list(question_list)
    
    progress(0.3, "Finding relevant URLs...")
    url_list = get_url_list(search_phrases=search_list)
    url_list += competitors_urls
    progress(0.4, "Saving and processing web content...")
    save_webpages(url_list, blog_id)
    
    progress(0.5, "Creating embeddings...")
    chroma = get_chroma_hybrid_search(blog_id,blog_id+"hyb")
    chroma.clear_collection()
    mkdwn_paths = get_markdown_files(blog_id)
    for path in mkdwn_paths:
        embed(path, chroma)
    
    chroma._load_persisted_data()
    
    progress(0.6, "Generating QnA...")
    qna_list = get_qna_list(question_list, chroma)
    
    progress(0.7, "Writing first draft...")
    first_draft = write_blog_post(
        purpose,
        target_audience=target_audience,
        pain_points=pain_points,
        primary_keywords=primary_keywords,
        secondary_keywords=secondary_keywords, 
        search_intent=search_intent,
        qna_list=qna_list, 
        topic=topic
    )
    
    progress(0.8, "Increasing word count...")
    second_draft = increase_word_count(first_draft, keywords=primary_keywords)
    
    progress(0.9, "Optimizing blog...")
    final_draft = optimize_blog(blog=second_draft, primary_keywords=primary_keywords)
    
    # Save the blog to a file
    filename = f"{topic.replace(' ','-')}.md"
    os.makedirs("generated-blogs", exist_ok=True)
    with open("generated-blogs/"+filename, "w", encoding="utf-8") as f:
        f.write(final_draft)
        
    progress(1, "Blog generation complete!")
    chroma.clear_collection()
    delete_folder(blog_id)
    delete_file(blog_id+"hyb")
    
    # Return the final blog text and the filename for download
    return final_draft, filename

# Define the Gradio interface
with gr.Blocks(title="AI Blog Generator") as app:
    gr.Markdown("# AI Blog Generator")
    
    with gr.Row():
        with gr.Column():
            # Input fields
            purpose_input = gr.Textbox(label="Purpose", placeholder="Traffic generation, Lead generation")
            target_audience_input = gr.Textbox(label="Target Audience", placeholder="e.g., drupal users")
            pain_points_input = gr.Textbox(
                label="Pain Points", 
                placeholder="Enter pain points separated by commas", 
                lines=3
            )
            primary_keywords_input = gr.Textbox(
                label="Primary Keywords", 
                placeholder="Enter primary keywords separated by commas", 
                lines=4
            )
            secondary_keywords_input = gr.Textbox(
                label="Secondary Keywords", 
                placeholder="Enter secondary keywords separated by commas",
                lines=2
            )
            
        with gr.Column():
            search_intent_input = gr.Dropdown(
                label="Search Intent",
                choices=["Informational", "Transactional", "Navigational", "Commercial Investigation"],
                multiselect=True
            )
            
            competitors_urls_input = gr.Textbox(
                label="Competitor URLs", 
                placeholder="Enter competitor URLs, one per line",
                lines=5
            )
            
            topic_input = gr.Textbox(
                label="Blog Topic", 
                placeholder="e.g., AI agents replacing software developers"
            )
            
            generate_button = gr.Button("Generate Blog", variant="primary")
    
    # Output areas
    with gr.Row():
        blog_output = gr.Textbox(
            label="Generated Blog (Markdown)", 
            lines=20, 
            interactive=False
        )
    
    # Download button for the generated blog
    file_output = gr.File(label="Download Blog as Markdown")
    
    # Connect the button click to the generate function
    generate_button.click(
        fn=generate_blog,
        inputs=[
            purpose_input,
            target_audience_input,
            pain_points_input,
            primary_keywords_input,
            secondary_keywords_input,
            search_intent_input,
            competitors_urls_input,
            topic_input
        ],
        outputs=[blog_output, file_output]
    )
    
    # Add examples
    gr.Examples(
        [
            [
                "Traffic generation, Lead generation",
                "drupal users",
                "Code quality and maintainability, Development process efficiency, Knowledge transfer and documentation",
                "drupal, drupal seo, drupal 10 end of life, best seo tool for drupal",
                "drupal 9 end of life",
                ["Transactional", "Navigational"],
                "https://www.herodevs.com/blog-posts/top-3-strategies-for-managing-drupal-7-end-of-life\nhttps://www.thedroptimes.com/43206/six-migration-options-drupal-7-end-life-in-2025",
                "AI agents replacing software developers"
            ]
        ],
        inputs=[
            purpose_input,
            target_audience_input,
            pain_points_input,
            primary_keywords_input,
            secondary_keywords_input,
            search_intent_input,
            competitors_urls_input,
            topic_input
        ]
    )

# Launch the app
if __name__ == "__main__":
    app.launch()