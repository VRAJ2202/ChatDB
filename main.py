
import streamlit as st
st.set_page_config(page_title="ChatDB – SQL + NoSQL", layout="centered")


import re
import json
from datetime import datetime

# === Import only what's needed from main and back without modifying them ===
from sql import handle_natural_language_query, get_schema_overview
from mongo import create_query_prompt, ask_gemini, run_operation, create_summary_prompt


st.title("🧠 ChatDB – Unified Chat Interface")

# User chooses between SQL and NoSQL
mode = st.radio("Choose database type:", ["SQL", "NoSQL"])

# SQL Section
if mode == "SQL":
    dataset = st.selectbox("Choose a dataset", ["Chinook"], key="sql_dataset")
    sql_question = st.text_area("💬 Ask your SQL question:", key="sql_question")

    if st.button("Ask SQL"):
        if sql_question.strip():
            with st.spinner("Generating SQL and querying..."):
                cols, result, gen_sql = handle_natural_language_query(sql_question, dataset)
                st.subheader("📊 Answer")
                st.dataframe(result, use_container_width=True)
                if gen_sql:
                    st.markdown("#### 🧾 Generated SQL Query")
                    st.code(gen_sql, language="sql")
        else:
            st.warning("Please enter a valid SQL question.")

    with st.expander("📘 Show Schema Overview"):
        st.text(get_schema_overview(dataset))

# NoSQL Section



elif mode == "NoSQL":
    nosql_question = st.chat_input("Ask your MongoDB database something...")

    

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if nosql_question:
        timestamp = datetime.now().strftime('%H:%M:%S')
        st.session_state.chat_history.append((f"🧠 [{timestamp}] You", nosql_question))

        prompt = create_query_prompt(nosql_question)
        query_text = ask_gemini(prompt)
        query_text = query_text.replace("```python", "").replace("```", "").strip()

        st.session_state.chat_history.append(("💻 MongoDB Query", f"```{query_text}```"))

        match = re.search(r"db\.(\w+)\.", query_text)
        collection = match.group(1) if match else None

        if collection:
            try:
                results = run_operation(query_text, collection)
                results_json = json.dumps(results, indent=2, default=str)
                summary = ask_gemini(create_summary_prompt(results_json))
                st.session_state.chat_history.append(("🤖 ChatDB", summary.strip()))
            except Exception as e:
                st.session_state.chat_history.append(("🤖 ChatDB", f"❌ Error: {e}"))
        else:
            st.session_state.chat_history.append(("🤖 ChatDB", "❌ Could not detect collection name."))

    for role, msg in st.session_state.chat_history:
        with st.chat_message("user" if "You" in role else "assistant"):
            st.markdown(f"**{role}**\n\n{msg}")
