import streamlit as st
import requests

API_URL = "http://localhost:8000/query"  # Adjust if hosted elsewhere
TOKEN = None  # Will store the auth token

def authenticate(username, password):
    response = requests.post("http://localhost:8000/token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

st.title("AI-Powered SQL Chatbot")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    
    if submit:
        TOKEN = authenticate(username, password)
        if TOKEN:
            st.session_state.authenticated = True
            st.session_state.token = TOKEN
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")
else:
    st.write("### Ask your database anything!")
    query = st.text_input("Enter your query in natural language")
    if st.button("Submit") and query:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(API_URL, params={"natural_query": query}, headers=headers)
        
        if response.status_code == 200:
            st.write("### Generated SQL Query:")
            st.code(response.json()["query"], language="sql")
            st.write("### Results:")
            st.table(response.json()["results"])
        else:
            st.error(response.json()["detail"])
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.experimental_rerun()
