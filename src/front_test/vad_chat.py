import os
from pprint import pprint
from urllib.parse import urlparse
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from docx import Document
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from youtube_transcript_api import YouTubeTranscriptApi

from htmlTemplates import css, bot_template, user_template

# from src.config.config import settings

# os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

# OPENAI_API_KEY = settings.openai_api_key

OPENAI_API_KEY = "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"


def save_file(raw_text, file_name):
    with open(f"history/{file_name}.txt", "w", encoding="utf-8") as file:
        file.write(raw_text)


def file_name_web(link_doc):
    parsed_url = urlparse(link_doc)
    name = os.path.basename(parsed_url.path)
    file_name, file_extension = os.path.splitext(name)
    return file_name


def get_web_text(web_doc):
    text = ""
    for doc in web_doc:
        text += doc.page_content
    return text


def file_name_youtube(youtube_link):
    file_name = "watch_" + youtube_link.split('watch?v=')[-1]
    return file_name


def get_youtube_text(youtube_link):
    video_id = youtube_link.split('watch?v=')[-1]

    target_language = None
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    for transcript in transcript_list:
        target_language = transcript.language_code
        try:
            transcript_data = transcript.fetch()
            translated_transcript = transcript.translate(target_language).fetch()
        except Exception as e:
            print(f"Error fetching transcript: {e}")

    target_language = target_language

    try:
        transcript = transcript_list.find_transcript([target_language])
        transcript_data = transcript.fetch()
        text = " ".join(entry['text'] for entry in transcript_data)
        print(text)
        return text
    except Exception as e:
        print(f"Error fetching transcript: {e}")


def file_name_pdf(pdf_docs):
    first_doc = pdf_docs[0] if len(pdf_docs) > 0 else None
    if first_doc:
        name = first_doc.name
        file_name, file_extension = os.path.splitext(name)
        return file_name
    return None


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def file_name_docx(docs_doc):
    first_doc = docs_doc[0] if len(docs_doc) > 0 else None
    if first_doc:
        name = first_doc.name
        file_name, file_extension = os.path.splitext(name)
        return file_name
    return None


def get_docx_text(docs_doc):
    text = ""
    try:
        for docx in docs_doc:
            doc = Document(docx)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
    except Exception as e:
        # Handle specific exceptions here, e.g., catching an incomplete file
        st.warning(f"Error reading DOCX file: {e}. No file to save.")
        return None  # Return None to indicate an error

    return text


def file_name_txt(txt_docs):
    first_doc = txt_docs[0] if len(txt_docs) > 0 else None
    if first_doc:
        name = first_doc.name
        file_name, file_extension = os.path.splitext(name)
        return file_name
    return None


def get_txt_text(txt_doc):
    text = ""
    for txt_doc in txt_doc:
        text += txt_doc.getvalue().decode('utf-8') + "\n"
    return text


def chat(raw_text):
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)
    st.session_state.conversation = get_conversation_chain(vectorstore)


def get_load_text(file_name):
    if file_name is not None:
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            st.warning(f"Error loading file: {e}")
    else:
        st.warning("No file selected.")
        return ""


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    if st.session_state.conversation is not None:
        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history']

        for i, message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
    else:
        pass


def close_chat():
    if st.session_state.conversation is not None:
        st.session_state.conversation = None
        st.session_state.chat_history = None
        st.success("Chat closed.")
        st.rerun()
    else:
        st.warning("No active chat to close.")
