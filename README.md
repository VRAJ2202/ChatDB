# ChatDB: Natural Language Interface for Databases

ChatDB is a Streamlit-based application that allows users to interact with SQL and NoSQL (MongoDB) databases using natural language queries powered by large language models (LLMs).

## Features

- Natural language query interpretation
- MongoDB and MySQL support
- Interactive Streamlit UI
- Dual-mode support: SQL and NoSQL
- Dynamic schema overview

## Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/VRAJ2202/ChatDB.git
cd ChatDB
```

2. (Optional) Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your `.env` file in the root directory with the following variables:

```env
api_key="your LLM API key (e.g., Google Gemini API key)"
mysql_host="localhost"
mysql_user="your MySQL username"
mysql_password="your MySQL password"
MONGO_URI="your MongoDB Atlas connection string"
```

5. Run the application using Streamlit:

```bash
streamlit run main.py
```

## File Structure

- `main.py` – Main Streamlit application
- `mongo.py` – MongoDB query handling
- `sql.py` – SQL query handling
- `requirements.txt` – Dependency list
- `README.md` – Project documentation