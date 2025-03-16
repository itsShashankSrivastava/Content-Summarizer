# This code is written with a better UI taken in mind

import validators
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.schema import Document
from youtube_transcript_api import YouTubeTranscriptApi
import os
import fitz
import time

# App theme and configuration
st.set_page_config(
    page_title="Content Summarizer App",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

image_path = r"c:\Users\shashank.srivastava\Downloads\image-removebg-preview (2).png"
# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #f0f9ff;
        border-left: 5px solid #1E88E5;
        padding: 20px;
        border-radius: 5px;
        color: black; /* Changed text color to black */
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .info-box {
        background-color: #e8f4f8;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 15px;
        color: black; /* Changed text color to black */
    }
    .source-tag {
        font-size: 0.8rem;
        color: #666;
        margin-top: 5px;
    }
    .progress-bar {
        height: 10px;
        background-color: #E3F2FD;
        border-radius: 5px;
    }
    .progress-value {
        height: 10px;
        background-color: #1E88E5;
        border-radius: 5px;
    }
    .rounded-img {
        width: 100px;  /* Adjust width to make it shorter */
        height: 100px; /* Adjust height to make it square */
        border-radius: 50%; /* Make it round */
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("<h1 class='main-header'>📝 Content Summarizer Pro</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Get concise, AI-powered summaries from YouTube videos, websites, or PDF documents</p>", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown('<img src="https://cdn6.aptoide.com/imgs/6/5/9/65917be31f8374db3f8bf15cbef769de_icon.png" class="rounded-img" />', unsafe_allow_html=True)
    st.caption("Powered by LangChain & Groq")
    st.markdown("### Configuration")
    
    groq_api_key = st.text_input("Groq API Key", value="", type="password", help="Enter your Groq API key to enable summarization")
    
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
    
    st.markdown("### Advanced Settings")
    model_selection = st.selectbox(
        "Select AI Model",
        ["deepseek-r1-distill-qwen-32b", "llama3-70b-8192", "mixtral-8x7b-32768"],
        index=0,
        help="Choose the AI model for summarization"
    )
    
    summary_length = st.slider(
        "Summary Length (words)",
        min_value=100,
        max_value=500,
        value=300,
        step=50,
        help="Adjust the length of your summary"
    )
    
    st.markdown("### About")
    st.info("This app uses AI to summarize content from multiple sources. Upload a PDF or provide a URL to get started.")

# Main content area with tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💡 How It Works", "🔧 Settings"])

with tab1:
    # Input section with cards
    st.markdown("### 📄 Select Your Content Source")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="info-box">🌐 Enter a URL</div>', unsafe_allow_html=True)
        generic_url = st.text_input(
            "YouTube or Website URL",
            placeholder="https://youtube.com/watch?v=... or https://example.com",
            label_visibility="collapsed"
        )
        
        # Auto-detect source type
        source_type = None
        if generic_url:
            if "youtube.com" in generic_url or "youtu.be" in generic_url:
                st.success("✅ YouTube video detected")
                source_type = "youtube"
            elif validators.url(generic_url):
                st.success("✅ Website URL detected")
                source_type = "website"
            else:
                st.error("❌ Invalid URL format")
    
    with col2:
        st.markdown('<div class="info-box">📑 Or Upload a PDF</div>', unsafe_allow_html=True)
        pdf_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")
        
        if pdf_file:
            st.success(f"✅ PDF uploaded: {pdf_file.name}")
            source_type = "pdf"
    
    # Summary options
    st.markdown("### 🔍 Summary Options")
    col1, col2 = st.columns(2)
    
    with col1:
        summary_style = st.radio(
            "Summary Style",
            ["Concise", "Detailed", "Bullet Points"],
            horizontal=True
        )
    
    with col2:
        include_metadata = st.checkbox("Include source metadata", value=True)
    
    # Action button
    summarize_button = st.button("✨ Generate Summary", use_container_width=True)
    
    # Processing logic
    if summarize_button:
        # Validate inputs
        if not groq_api_key.strip():
            st.error("⚠️ Please provide a Groq API key in the sidebar")
        elif not source_type:
            st.error("⚠️ Please provide a valid URL or upload a PDF file")
        else:
            try:
                # Show processing animation
                with st.spinner("Processing your content..."):
                    progress_placeholder = st.empty()
                    # Simulate progress
                    for i in range(101):
                        progress_placeholder.markdown(f"""
                        <div class="progress-bar">
                            <div class="progress-value" style="width:{i}%"></div>
                        </div>
                        <p class="source-tag">Processing {i}%</p>
                        """, unsafe_allow_html=True)
                        time.sleep(0.01)
                
                    # Initialize the language model
                    llm = ChatGroq(
                        model=model_selection,
                        api_key=groq_api_key
                    )
                    
                    # Adjust the prompt based on selected style
                    prompt_template = ""
                    if summary_style == "Concise":
                        prompt_template = f"""
                        Provide a concise summary of the following content in {summary_length} words:
                        Content: {{text}}
                        """
                    elif summary_style == "Detailed":
                        prompt_template = f"""
                        Provide a detailed analysis and summary of the following content in {summary_length} words,
                        highlighting the key points, main arguments, and important details:
                        Content: {{text}}
                        """
                    else:  # Bullet Points
                        prompt_template = f"""
                        Summarize the following content in {summary_length} words using bullet points for clarity.
                        Focus on the most important information and organize it logically:
                        Content: {{text}}
                        """
                    
                    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
                    docs = []
                    source_info = ""

                    # Handle YouTube videos
                    if source_type == "youtube":                    
                        # Extract video ID from URL
                        if "youtu.be" in generic_url:
                            video_id = generic_url.split("/")[-1].split("?")[0]
                        else:
                            video_id = generic_url.split("v=")[1].split("&")[0]
                        
                        # Try to get transcript
                        try:
                            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                            transcript_text = " ".join([item['text'] for item in transcript_list])
                            source_info = f"YouTube Video (ID: {video_id})"
                        except:
                            # If English isn't available, try any transcript
                            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                            transcript_text = " ".join([item['text'] for item in transcript_list])
                            source_info = f"YouTube Video (ID: {video_id}, Non-English)"
                        
                        docs = [Document(page_content=transcript_text, metadata={"source": generic_url})]
                    
                    # Handle websites
                    elif source_type == "website":
                        loader = UnstructuredURLLoader(
                            urls=[generic_url], 
                            ssl_verify=False,
                            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                        )
                        docs = loader.load()
                        source_info = f"Website: {generic_url}"
                    
                    # Handle PDFs
                    elif source_type == "pdf":
                        pdf_text = ""
                        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
                            page_count = len(doc)
                            for page_num, page in enumerate(doc):
                                pdf_text += page.get_text()
                                # Update progress
                                progress = int((page_num + 1) / page_count * 100)
                                progress_placeholder.markdown(f"""
                                <div class="progress-bar">
                                    <div class="progress-value" style="width:{progress}%"></div>
                                </div>
                                <p class="source-tag">Processing PDF page {page_num + 1}/{page_count}</p>
                                """, unsafe_allow_html=True)
                        
                        docs = [Document(page_content=pdf_text, metadata={"source": pdf_file.name})]
                        source_info = f"PDF: {pdf_file.name}"

                    # Process the content if documents were obtained
                    if docs:
                        chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                        
                        with st.spinner("📝 Generating your summary..."):
                            output_summary = chain.invoke(docs)
                            
                            # Handle the output format
                            if isinstance(output_summary, dict) and "output_text" in output_summary:
                                output_summary = output_summary["output_text"]
                            
                            # Display the result with styling
                            st.markdown("### 📋 Summary Result")
                            st.markdown(f'<div class="success-box">{output_summary}</div>', unsafe_allow_html=True)
                            
                            if include_metadata:
                                st.markdown(f'<p class="source-tag">Source: {source_info}</p>', unsafe_allow_html=True)
                            
                            # Add download button for the summary
                            st.download_button(
                                label="📥 Download Summary",
                                data=output_summary,
                                file_name="content_summary.txt",
                                mime="text/plain"
                            )
                    else:
                        st.error("❌ No content could be extracted from the provided source.")
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("If you're having issues with YouTube videos, check if captions are available for this video.")

with tab2:
    st.markdown("### How Content Summarizer Pro Works")
    
    st.markdown("""
    <div class="info-box">
    <h4>🔍 Three Simple Steps</h4>
    <ol>
        <li><strong>Source Selection</strong>: Provide a YouTube URL, website link, or upload a PDF document</li>
        <li><strong>AI Processing</strong>: Our advanced AI models analyze and extract key information</li>
        <li><strong>Summary Generation</strong>: Get a concise, well-formatted summary based on your preferences</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center;">
        <h4>🌐 Websites</h4>
        <p>Extract and summarize content from any web page</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
        <h4>🎥 YouTube</h4>
        <p>Convert video transcripts into readable summaries</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center;">
        <h4>📄 PDFs</h4>
        <p>Extract text from documents for quick comprehension</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("### Application Settings")
    
    st.info("Configure your preferences for the application here. These settings are saved for your current session.")
    
    theme_choice = st.selectbox(
        "UI Theme",
        ["Light", "Dark", "System Default"],
        index=0
    )
    
    default_model = st.selectbox(
        "Default AI Model",
        ["deepseek-r1-distill-qwen-32b", "llama3-70b-8192", "mixtral-8x7b-32768"],
        index=0
    )
    
    st.markdown("### Advanced Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cache_results = st.checkbox("Cache results to improve performance", value=True)
    
    with col2:
        debug_mode = st.checkbox("Enable debug mode", value=False)
    
    st.button("Save Settings", type="primary", use_container_width=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 40px; padding: 20px; border-top: 1px solid #eee;">
    <p>Content Summarizer Pro • Built with Streamlit & LangChain • Powered by Groq</p>
</div>
""", unsafe_allow_html=True)