import openai
import pymysql
import jwt
import datetime
from typing import List
from langchain import SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType
from langchain.agents import create_sql_agent
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.agent_toolkits import SQLDatabaseToolkit

OPENAI_API_KEY = st.secrets["openai"]["OPENAI_API_KEY"]
db_config = {
    "host": "database-1.c7ew0quossbs.us-east-1.rds.amazonaws.com",
    "user": "root",
    "password": "MamaGrentina$100!",
    "database": "ecommerce"
}

def get_db_connection():
    try:
        conn = pymysql.connect(**db_config)
        print("Database connection successful!")

        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")   

def get_db_schema():
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to the database")
    else:
        cursor = conn.cursor()  # Safe to use .cursor() now
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    schema = ""
    for (table,) in tables:
        cursor.execute(f"DESCRIBE {table}")
        columns = cursor.fetchall()
        schema += f"Table: {table}\n"
        for column in columns:
            schema += f" - {column[0]} ({column[1]})\n"
    conn.close()
    return schema


def initialize_sql_agent():
    try:
        # Note: instead of root, use user that have only have read access for safety and accidental update/delete record
        db = SQLDatabase.from_uri("mysql+pymysql://root:MamaGrentina$100!@database-1.c7ew0quossbs.us-east-1.rds.amazonaws.com:3306/ecommerce")
        llm = ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=OPENAI_API_KEY)
        schema = get_db_schema()
        print(f"Database Schema: {schema}")  # Debugging
        # Create toolkit with LLM
        toolkit = SQLDatabaseToolkit(
            db=db,
            llm=llm
        )
        agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            extra_prompt_data={"schema": schema}
        )
        return agent_executor
    except Exception as e:
        print(f"Error in create_sql_agent: {e}")  # Log error
        raise HTTPException(status_code=500, detail=str(e))

def text_to_sql(natural_query: str) -> str:
    prompt = f"Convert this natural language query into SQL: '{natural_query}'"
    response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
    sql_query = response["choices"][0]["message"]["content"]
    return sql_query.strip()

def generate_query(natural_query: str):
    # Initialize LLM
    llm = ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=OPENAI_API_KEY)

    db_schema = get_db_schema()

    # Prompt Template including the database schema
    sql_prompt = PromptTemplate(
        input_variables=["question", "schema"],
        template=(
            "You are an expert SQL query generator. Use the provided database schema to create a valid SQL query.\n"
            "Database Schema:\n{schema}\n"
            "Convert the following question into an SQL SELECT query:\n"
            "Question: {question}\n"
            "SQL Query:"
        )
    )

    # Create an LLM chain
    sql_chain = LLMChain(llm=llm, prompt=sql_prompt)

    sql_query = sql_chain.run({"question": natural_query, "schema": db_schema})

    print(f"Generated SQL Query: {sql_query}")  # Debugging

    # sql_query = text_to_sql(natural_query)
    if not sql_query.lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        return {"query": sql_query, "results": results}
    except Exception as e:
        print(f"Database query execution failed: {e}")  # Debugging
        raise HTTPException(status_code=500, detail=str(e))

def execute_query(natural_query: str):
    agent = initialize_sql_agent()
    sql_response = agent.run(natural_query)
    print(f"Generated SQL response: {sql_response}")  # Debugging

    return {"query": natural_query, "results": sql_response}
