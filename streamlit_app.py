import streamlit as st
import streamlit_app as streamlit_app

st.title("AI-Powered SQL Chatbot")

OPENAI_API_KEY = st.secrets["openai"]["OPENAI_API_KEY"]
if not OPENAI_API_KEY:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Set environment variables
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    
    # Create an OpenAI client.
    client = OpenAI(api_key=OPENAI_API_KEY)

    st.write("### Ask your database anything!")
    query = st.text_input("Enter your query in natural language")
    if st.button("Submit") and query:
        response = streamlit_app.execute_query(query)
        
        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)
