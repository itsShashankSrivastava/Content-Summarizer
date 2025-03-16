# this is the main logic for the entire code which is made with a simple UI

import validators
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.schema import Document
from youtube_transcript_api import YouTubeTranscriptApi
import os
import fitz  # PyMuPDF for PDF text extraction

# Streamlit App Configuration
st.set_page_config(page_title="LangChain: Summarize Text From YT, Website, or PDF", page_icon="🦜")
st.title("🦜 LangChain: Summarize Text From YT, Website, or PDF")
st.subheader('Summarize Content from Various Sources')

# Get the Groq API Key
with st.sidebar:
    groq_api_key = st.text_input("Groq API Key", value="", type="password")
    
    # Set the API key in environment variables for the Groq client
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key

# Input for URL or PDF
generic_url = st.text_input("URL (YouTube or Website)", label_visibility="collapsed")
pdf_file = st.file_uploader("Or upload a PDF file", type="pdf")

# When the user clicks the "Summarize the Content from YT, Website, or PDF" button
if st.button("Summarize the Content from YT, Website, or PDF"):
    # Validate inputs
    if not groq_api_key.strip() or (not generic_url.strip() and pdf_file is None):
        st.error("Please provide the information to get started")
    elif generic_url and not validators.url(generic_url):
        st.error("Please enter a valid URL. It can be a YT video URL or website URL")
    else:
        try:
            llm = ChatGroq(
                model="deepseek-r1-distill-qwen-32b",
                api_key=groq_api_key     
            )
            
            # Define the prompt template for summarization
            prompt_template = """
            Provide a summary of the following content in 300 words:
            Content:{text}
            """
            prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
            
            with st.spinner("Processing content..."):
                docs = []

                # Handle YouTube videos differently
                if "youtube.com" in generic_url or "youtu.be" in generic_url:
                    try:                       
                        # Extract video ID from URL
                        if "youtu.be" in generic_url:
                            video_id = generic_url.split("/")[-1].split("?")[0]
                        else:
                            video_id = generic_url.split("v=")[1].split("&")[0]
                        
                        # Try to get English transcript
                        try:
                            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                            transcript_text = " ".join([item['text'] for item in transcript_list])
                        except:
                            # If English isn't available, try to get any available transcript
                            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                            transcript_text = " ".join([item['text'] for item in transcript_list])
                        
                        # Create a document with the transcript
                        docs = [Document(page_content=transcript_text, metadata={"source": generic_url})]
                    except Exception as e:
                        st.error(f"Failed to extract transcript: {e}")
                        st.info("This video might not have available captions in English.")
                        docs = []
                # Handle regular websites
                elif generic_url:
                    loader = UnstructuredURLLoader(urls=[generic_url], ssl_verify=False,
                                                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})
                    docs = loader.load()
                # Handle PDF file
                elif pdf_file:
                    # Extract text from the uploaded PDF using PyMuPDF (fitz)
                    pdf_text = ""
                    with fitz.open(pdf_file) as doc:
                        for page in doc:
                            pdf_text += page.get_text()
                    
                    # Create a document with the extracted text from the PDF
                    docs = [Document(page_content=pdf_text, metadata={"source": "Uploaded PDF"})]

                if docs:
                    # Set up the chain for summarization
                    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                    
                    try:
                        output_summary = chain.invoke(docs)
                        
                        # Handle the output format to avoid the metadata 
                        if isinstance(output_summary, dict) and "output_text" in output_summary:
                            output_summary = output_summary["output_text"]
                        
                        st.success(output_summary)
                    except Exception as chain_error:
                        st.error(f"Error during summarization: {chain_error}")
                else:
                    st.error("No content could be extracted from the provided URL or PDF.")
                    
        except Exception as e:
            st.exception(f"Exception: {e}")
