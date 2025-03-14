import streamlit as st
import generate_execute_query as generate_execute_query
import os

st.title("AI-Powered SQL Chatbot")

OPENAI_API_KEY = st.text_input("OpenAI API Key", type="password")

# OPENAI_API_KEY = st.secrets["openai"]["OPENAI_API_KEY"]
if not OPENAI_API_KEY:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Set environment variables
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    
    # Create an OpenAI client.
    # client = OpenAI(api_key=OPENAI_API_KEY)

    st.write("### Ask your database anything!")
    query = st.text_input("Enter your query in natural language")
    if st.button("Submit") and query:
        response = generate_execute_query.execute_query(query)
        
        # Stream the response to the app using `st.write_stream`.
        st.write_stream(response)
        st.write(response["results"])

        result = response["results"]
        # Convert result to Pandas DataFrame
        if isinstance(result, list):  # If result is a list of tuples
            df = pd.DataFrame(result, columns=["Column1", "Column2", "Column3"])  # Adjust columns accordingly
        elif isinstance(result, str):  # If result is a string (error handling)
            df = pd.DataFrame({"Response": [result]})
        else:
            df = pd.DataFrame({"Message": ["No valid data returned"]})

        # Display results in a table
        st.dataframe(df)  # Interactive table
