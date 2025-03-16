# text-to-sql-chatbot
AI chatbot that take text, convert to SQL query and run to the database

GenAI SQL & Python Agent

A Streamlit-based GenAI assistant for querying SQL databases using Large Language Models (LLMs). This AI-powered tool allows users to interact with databases using natural language.

🚀 **Features**

* Natural Language to SQL Query Conversion – Use GenAI to convert text queries into SQL and execute on selected database.

* Streamlit-Based UI – Intuitive interface for a smooth user experience.

🛠 **Installation**

1️⃣ **Clone the Repository**

git clone https://github.com/hirangoly/text-to-sql-chatbot.git 
cd text-to-sql-chatbot

2️⃣ **Create a Virtual Environment & Install Dependencies**

python -m venv venv source venv/bin/activate # On Windows, use 'venv\Scripts\activate' pip install -r requirements.txt

3️⃣ **Set Up Environment Variables**

Create a .env file in the project directory and add:

OPENAI_API_KEY=your_openai_api_key DATABASE_HOST=your_database_host DATABASE_USER=your_database_user DATABASE_PASSWORD=your_database_password

4️⃣ **Run the Streamlit App**

streamlit run app.py

**Future Advancement:**

* Python Data Visualization Generation – Generate Python code for data plots automatically.

* Conversational Memory – Retains context for more meaningful responses.

* Multi-LLM Support – Select from OpenAI, Llama, or Gemini for enhanced accuracy.

