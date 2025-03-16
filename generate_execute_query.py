from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import openai
import pymysql
import jwt
import datetime
from typing import List
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import urllib.parse
from langchain_experimental.sql import SQLDatabaseChain


def get_db_connection(db_config):
    try:
        conn = pymysql.connect(**db_config)
        print("Database connection successful!")

        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")   

def get_db_schema(db_config):
    conn = get_db_connection(db_config)
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


def initialize_sql_agent(db_config):
    try:
        # Note: instead of root, use user that have only have read access for safety and accidental update/delete record
        password = urllib.parse.quote_plus(db_config['PASSWORD'])
        connection_string = (
            f"mysql+pymysql://{db_config['USER']}:{password}@"
            f"{db_config['HOST']}:{db_config['PORT']}/{db_config['DATABASE']}"
        )
        db = SQLDatabase.from_uri(connection_string)

        # LLM model
        llm = ChatOpenAI(model_name="gpt-4", temperature=0)
        # schema = get_db_schema(db_config)
        # print(f"Database Schema: {schema}")  # Debugging
        # Create toolkit with LLM
        toolkit = SQLDatabaseToolkit(
            db=db,
            llm=llm
        )

        # Create SQL execution agent (Equivalent to create_sql_agent)
        db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=True)

        return db_chain
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
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)

    db_schema = get_db_schema()

    # Prompt Template including the database schema
    sql_prompt = PromptTemplate(
        input_variables=["question", "schema"],
        template=(
            "You are an expert SQL query generator. Use the provided database schema to create a valid SQL query.\n"
            "Database Schema:\n{schema}\n"
            "Convert the following question into an SQL SELECT query: and then execute on provided database. show in tabular format or structured data\n"
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

def execute_query(natural_query: str, db_config: dict):
    db_chain = initialize_sql_agent(db_config)
    sql_response = db_chain.run(natural_query)
    print(f"Generated SQL response: {sql_response}")  # Debugging

    return {"query": natural_query, "results": sql_response}
