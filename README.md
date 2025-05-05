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
git clone https://github.com/yourusername/chatdb.git
cd chatdb
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Set up your `.env` file for environment variables (e.g., API keys, DB URIs).

5. Run the Streamlit app:

```bash
streamlit run main.py
```

## File Structure

- `main.py` – Main Streamlit application
- `mongo.py` – MongoDB query handling
- `sql.py` – SQL query handling
- `requirements.txt` – Project dependencies

## License

This project is licensed under the MIT License.