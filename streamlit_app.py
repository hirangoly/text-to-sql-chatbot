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

    # 1. Initialize session state.
    if "db_config" not in st.session_state:
        st.session_state.db_config = {
            'USER': '',
            'PASSWORD': '',
            'HOST': 'localhost',
            'DATABASE': '',
            'PORT': '3306'
        }
    
    if "db_connected" not in st.session_state:
        st.session_state.db_connected = False
    
    if 'databases' not in st.session_state:
        st.session_state.databases = []
    
    # 2. Sidebar user inputs.
    st.sidebar.title("DATABASE CONFIGURATION")
    st.sidebar.subheader("Enter MySQL connection details:", divider=True)
    
    user = st.sidebar.text_input("User", value=st.session_state.db_config['USER'])
    password = st.sidebar.text_input("Password", type="password", value=st.session_state.db_config['PASSWORD'])
    host = st.sidebar.text_input("Host", value=st.session_state.db_config['HOST'])
    port = st.sidebar.text_input("Port", value=st.session_state.db_config['PORT'])
    
    # 3. Single dynamic button label.
    button_label = "Save and Connect" if not st.session_state.db_connected else "Update Connection"
    
    def test_connection(config):
        """Check DB connectivity and, if successful, fetch all databases."""
        try:
            connection_string = (
                f"mysql+pymysql://{config['USER']}:{urllib.parse.quote_plus(config['PASSWORD'])}"
                f"@{config['HOST']}:{config['PORT']}/"
            )
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
    
            # If we succeed, fetch list of databases for the dropdown
            try:
                connection = mysql.connector.connect(
                    host=config['HOST'],
                    user=config['USER'],
                    password=config['PASSWORD'],
                    port=config['PORT']
                )
                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("SHOW DATABASES")
                    dbs = [db[0] for db in cursor.fetchall() 
                           if db[0] not in ('sys', 'mysql','performance_schema','information_schema')]
                    cursor.close()
                    connection.close()
                    return True, dbs
            except Error as e:
                st.sidebar.error(f"Error fetching databases: {e}")
                return False, []
        except Exception as e:
            st.sidebar.error(f"Connection test failed: {str(e)}")
            return False, []
        return False, []
    
    # 4. Single button to connect/update.
    if st.sidebar.button(button_label):
        if all([user, password, host, port]):
            new_config = {
                'USER': user,
                'PASSWORD': password,
                'HOST': host,
                'PORT': port,
                # DATABASE will be selected from dropdown below, so leave it blank initially
                'DATABASE': ''
            }
            ok, db_list = test_connection(new_config)
            if ok:
                st.session_state.db_config = new_config
                st.session_state.db_connected = True
                # Store database list in session for the dropdown
                st.session_state.databases = db_list
                st.sidebar.success("Connection test successful! Please select a database.")
            else:
                st.session_state.db_connected = False
                st.session_state.databases = []
        else:
            st.sidebar.error("All fields are required")
    
    # 5. If connected, show the databases in a dropdown for selection.
    if st.session_state.db_connected and st.session_state.databases:
        db_choice = st.sidebar.selectbox(
            "Select Database",
            options=st.session_state.databases,
            index=st.session_state.databases.index(st.session_state.db_config['DATABASE'])
            if st.session_state.db_config['DATABASE'] in st.session_state.databases else 0
        )
        
        if db_choice and db_choice != st.session_state.db_config['DATABASE']:
            # Update the config to the selected DB
            st.session_state.db_config['DATABASE'] = db_choice

    st.write("### Ask your database anything!")
    query = st.text_input("Enter your query in natural language")
    if st.button("Submit") and query:
        response = generate_execute_query.execute_query(query, st.session_state.db_config)
        
        # Stream the response to the app using `st.write_stream`.
        st.write_stream(response)
        st.write(response["results"])
