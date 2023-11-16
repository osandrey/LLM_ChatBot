import os
import requests
import pickle
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from docx import Document
from transformers import GPT2TokenizerFast
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
from langchain.document_loaders import WebBaseLoader

chat_history = []


def print_chat_history():
    for user_query, bot_response in chat_history:
        print(f'User: {user_query}')
        print(f'Bot: {bot_response}')
        print('-' * 20)


def get_text_chunks(text):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=24,
        length_function=len(tokenizer.encode(text))
    )

    chunks = text_splitter.create_documents([text])
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vector_db = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vector_db


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


def chat(raw_text):
    text_chunks = get_text_chunks(raw_text)
    vector_db = get_vectorstore(text_chunks)
    st.session_state.conversation = get_conversation_chain(vector_db)


def save_file(raw_text, file_name):
    try:
        with open(f"{file_name}.txt", "w", encoding="utf-8") as file:
            file.write(raw_text)
            st.success("Saved successfully.")
    except Exception as er:
        st.warning(f"Error: {er}. No file to save.")


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


def main():
    print("Welcome to my BOT! Type 'exit' to stop")

    while True:
        user_input = input("You: ")

        if user_input.lower() == 'exit':
            print("Thank you for using the chatbot. Goodbye!")
            break
        result = qa({"question": user_input, "chat_history": chat_history})
        bot_response = result["answer"]
        chat_history.append((user_input, bot_response))
        print_chat_history()


if __name__ == '__main__':
    main()
