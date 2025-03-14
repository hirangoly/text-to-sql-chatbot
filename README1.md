To run the chatbot locally and test it, follow these steps:

1️⃣ Install Dependencies
Ensure you have the required Python packages installed. Run:

bash
Copy
Edit
pip install fastapi uvicorn openai pymysql langchain pyjwt
2️⃣ Update Database Configuration
Modify the db_config in your script with your actual MySQL credentials:

python
Copy
Edit
db_config = {
    "host": "localhost",  # Change if needed
    "user": "your_user",
    "password": "your_password",
    "database": "your_database"
}
3️⃣ Start the FastAPI Server
Run the following command in your terminal:

bash
Copy
Edit
uvicorn Fastapi_Chatbot_Sql:app --reload
(Replace Fastapi_Chatbot_Sql with your actual script filename, if different.)

4️⃣ Authenticate & Get Token
Open a terminal and run:

bash
Copy
Edit
curl -X 'POST' \
  'http://127.0.0.1:8000/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin&password=password'
This should return a token like:

json
Copy
Edit
{"access_token":"your_token","token_type":"bearer"}
5️⃣ Test the Chatbot by Running a Query
Replace <your_token> with the token from Step 4 and send a query:

bash
Copy
Edit
curl -X 'GET' \
  'http://127.0.0.1:8000/query?natural_query=Show%20me%20all%20customers' \
  -H 'Authorization: Bearer <your_token>'
If everything is set up correctly, you should get a response with the SQL query and results from the database.