import streamlit as st
import re
import nltk
import fitz  
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from datetime import datetime
import io

nltk.download('punkt')
nltk.download('stopwords')


def extract_text_from_pdf(pdf_file):                                         # Function to extract text from PDF
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def find_relevant_answer(content, query, limit=3):                            # Function to find and rank relevant answers based on user query
    content_lower = content.lower()
    query_lower = query.lower()
    sentences = sent_tokenize(content)  
    stop_words = set(stopwords.words('english'))
    query_words = [word for word in word_tokenize(query_lower) if word.isalnum() and word not in stop_words]
    sentence_scores = {}
    for sentence in sentences:
        words = [word for word in word_tokenize(sentence.lower()) if word.isalnum() and word not in stop_words]
        score = sum(Counter(words)[word] for word in query_words)
        if score > 0:
            sentence_scores[sentence] = score   
    sorted_sentences = sorted(sentence_scores.items(), key=lambda item: item[1], reverse=True)
    if sorted_sentences:
        top_sentences = [sentence for sentence, score in sorted_sentences[:limit]]  
        return top_sentences
    else:
        return ["No relevant information found for your query."]


def main():                                                                  #main function of the web app
    st.title("Chatbot File Upload")
    st.write("Upload a PDF or TXT file and ask questions to get relevant answers based on its content. Type 'exit' to stop.")

    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])

    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            content = extract_text_from_pdf(uploaded_file)
        else:
            content = uploaded_file.read().decode("utf-8")
            
        st.text_area("File Content", content, height=300)
        if 'conversation' not in st.session_state:
            st.session_state.conversation = []
            st.session_state.last_query = None                              # To store the last query for follow-up

        
        query = st.text_input("Ask a question about the content:")          # User input for query

        if query:
            if query.lower() == "exit":                                     # Stop the Streamlit app 
                st.write("Exiting the chat. Thank you!")
                st.stop() 
            elif query.lower() == "more" and st.session_state.last_query:
                relevant_answers = find_relevant_answer(content, st.session_state.last_query, limit=3)
                for answer in relevant_answers:
                    st.write(f"**Chatbot:** {answer}")
            else:
                relevant_answers = find_relevant_answer(content, query, limit=3)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
                st.session_state.conversation.append((timestamp, query, relevant_answers))
                st.session_state.last_query = query 
              
                for answer in relevant_answers:                            # Display the answers
                    st.write(f"**Chatbot:** {answer}")

        st.subheader("Conversation History:")                              # Display the conversation history in reverse order         
        for timestamp, user_query, bot_response in reversed(st.session_state.conversation):
            st.write(f"**You:** {user_query}")
            for response in bot_response:
                st.write(f"**Chatbot:** {response}")

if __name__ == "__main__":
    main()
