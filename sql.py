import streamlit as st

#mysql_connector.py

import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

def get_connection(db_name=None):
    return mysql.connector.connect(
        host=os.getenv("mysql_host"),
        user=os.getenv("mysql_user"),
        password=os.getenv("mysql_password"),
        database=db_name or os.getenv("mysql_database")
    )

def run_query(query, db_name):
    conn = get_connection(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        if cursor.with_rows:
            columns = [desc[0] for desc in cursor.description]
            result = cursor.fetchall()
            return columns, result
        else:
            conn.commit()
            return ["Status"], [["Query executed successfully"]]
    except Exception as e:
        return ["Error"], [[str(e)]]
    finally:
        cursor.close()
        conn.close()

def get_schema_overview(db_name):
    conn = get_connection(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        schema = ""
        for (table_name,) in tables:
            schema += f"\n📄 Table: `{table_name}`\n"
            cursor.execute(f"DESCRIBE {table_name}")
            for col in cursor.fetchall():
                schema += f"  - {col[0]} ({col[1]})\n"
            schema += "\n"
        return schema.strip()
    finally:
        cursor.close()
        conn.close()






# query_utils.py

def handle_natural_language_query(nl_query: str, db_name: str):
    schema = get_schema_overview(db_name)
    sql = generate_sql(nl_query, schema)
    if not sql:
        return ["Error"], [["Failed to generate SQL."]], None

    print(f"[{db_name}] SQL:", sql)
    columns, result = run_query(sql, db_name)
    return columns, result, sql




#gemini_api.py

import os
import re
import google.generativeai as genai


load_dotenv()
api_key = os.getenv("api_key")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")


def generate_sql(nl_query: str, schema: str) -> str:
    try:
        prompt = f"""
You are an AI assistant that translates natural language to **MySQL** queries.
You can use SELECT, INSERT, UPDATE, DELETE, JOIN, etc.
Avoid using SQLite syntax or sqlite_master.

Here is the database schema:

{schema}

Translate the following question into a valid MySQL query:
"{nl_query}"

Only return the SQL query. Do not include markdown or explanation.
"""
        response = model.generate_content(prompt)
        return re.sub(r"```(?:sql)?|```", "", response.text, flags=re.IGNORECASE).strip()
    except Exception as e:
        print("Gemini Error:", e)
        return None





# main.py


# st.set_page_config(page_title="ChatDB – Multi-DB Interface", layout="centered")
# st.title("🧠 ChatDB: Talk to SQL using Natural Language")


# ✅ Dataset selector
dataset = st.selectbox("Choose a dataset", ["Chinook", "Employees"])

user_question = st.text_area("💬 Ask your question:")

if st.button("Ask Database"):
    if user_question.strip():
        with st.spinner("Thinking..."):
            columns, result, generated_sql = handle_natural_language_query(user_question, dataset)
            st.subheader("📊 Answer")
            st.dataframe(result, use_container_width=True)
            
            if generated_sql:
                st.markdown("#### 🧾 Generated SQL Query")
                st.code(generated_sql, language="sql")
    else:
        st.warning("Please enter a valid question.")

with st.expander("📘 Show Schema Overview"):
    st.text(get_schema_overview(dataset))