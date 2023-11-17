import os
import requests
import pickle
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

from htmlTemplates import css, bot_template, user_template


# from src.config.config import settings

# os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()


# OPENAI_API_KEY = settings.openai_api_key

OPENAI_API_KEY = "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"


def chat(raw_text):
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)
    st.session_state.conversation = get_conversation_chain(vectorstore)


def save_file(raw_text):
    with open("save.txt", "w", encoding="utf-8") as file:
        file.write(raw_text)


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


def close_chat():
    if st.session_state.conversation is not None:
        st.session_state.conversation = None
        st.session_state.chat_history = None
        st.success("Chat closed.")
        st.experimental_rerun()
    else:
        st.warning("No active chat to close.")


def get_html_text(new_doc):
    text = ""
    for doc in new_doc:
        text += doc.page_content
    return text


def get_pdf_text(new_doc):
    text = ""
    for pdf in new_doc:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_docx_text(new_doc):
    text = ""
    for docx in new_doc:
        doc = Document(docx)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    return text


def get_txt_text(new_doc):
    text = ""
    for txt_doc in new_doc:
        text += txt_doc.getvalue().decode('utf-8') + "\n"
    return text


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
