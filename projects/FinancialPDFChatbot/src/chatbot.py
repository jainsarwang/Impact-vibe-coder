
import streamlit as st
import os
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import ChromaDB
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import Groq

def initialize_chatbot():
    load_dotenv()
    groq_api_key = os.environ.get("")
    if not groq_api_key:
        st.error("GROQ_API_KEY not found in environment variables. Please set it.")
        return None, None, None

    llm = Groq(temperature=0.1, groq_api_key=groq_api_key, model_name="llama3-70b-8192")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return llm, embeddings, groq_api_key

def process_pdf(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def create_vectorstore(chunks, embeddings):
    vectorstore = ChromaDB.from_texts(texts=chunks, embedding=embeddings)
    return vectorstore

def create_conversational_chain(llm, vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return chain

def handle_user_input(question, chain, chat_history):
    response = chain({"question": question, "chat_history": chat_history})
    answer = response["answer"]
    chat_history.append((question, answer))
    return answer, chat_history

def main():
    st.header("Financial PDF Chatbot")

    # Initialize
    llm, embeddings, groq_api_key = initialize_chatbot()
    if not llm or not embeddings or not groq_api_key:
        return

    # PDF Input
    pdf_docs = st.file_uploader(
        "Upload your Financial PDFs here", accept_multiple_files=True)

    if pdf_docs:
        with st.spinner("Processing PDF ..."):
            chunks = process_pdf(pdf_docs)
            vectorstore = create_vectorstore(chunks, embeddings)
            chain = create_conversational_chain(llm, vectorstore)
            st.session_state.conversation = chain
            st.success("PDF processed successfully!")

    # Chat Input
    question = st.chat_input("Ask questions about your PDF:")
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if question:
        if st.session_state.conversation is not None:
            with st.spinner("Generating response..."):
                answer, st.session_state.chat_history = handle_user_input(question, st.session_state.conversation, st.session_state.chat_history)
            st.write(f"**Question:** {question}")
            st.write(f"**Answer:** {answer}")
        else:
            st.warning("Please upload and process a PDF document first.")

if __name__ == '__main__':
    main()
