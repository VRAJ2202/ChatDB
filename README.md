# LLM Powered SQL Project
## Overview
* Developed an LLM-powered SQL query generation system using Google PaLM to translate natural language into SQL queries.
* Integrated Hugging Face’s all-MiniLM-L6-v2 model to generate semantic embeddings of SQL queries, storing them in ChromaDB for fast and accurate retrieval based on semantic similarity.
* Employed LangChain to build a modular and scalable pipeline for query generation and retrieval.

## Features
**Embeddings Generation:** Utilizes the HuggingFace "all-MiniLM-L6-v2" model to generate embeddings for SQL queries.

**ChromaDB Database:** Stores the generated embeddings in the ChromaDB Database for efficient retrieval and querying.

**Streamlit Deployment:** The model is deployed using Streamlit, providing a user-friendly interface for interacting with the LLM-powered SQL capabilities.


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
