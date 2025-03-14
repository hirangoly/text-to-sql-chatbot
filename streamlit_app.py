import streamlit as st
import streamlit_app as streamlit_app

st.title("AI-Powered SQL Chatbot")

openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    st.write("### Ask your database anything!")
    query = st.text_input("Enter your query in natural language")
    if st.button("Submit") and query:
        response = streamlit_app.execute_query(query)
        
        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)
