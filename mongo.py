# Cell 1: Imports & Setup
import os
import json
import requests
import re
import ast
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv


# If using environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("api_key")
MONGO_URI = os.getenv("MONGO_URI")



API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

client = MongoClient(MONGO_URI)
db = client["sample_mflix"]




# Cell 2: Prompt Builders

def get_schema_summary():
    schema = []
    for col in db.list_collection_names():
        sample = db[col].find_one()
        if sample:
            fields = ', '.join(sample.keys())
            schema.append(f"{col} ({fields})")
    return schema

def create_query_prompt(user_question):
    schema = get_schema_summary()
    schema_text = "\n".join([f"{i+1}. {line}" for i, line in enumerate(schema)])

    return f"""
You are a MongoDB expert. Convert the following natural language request into a valid PyMongo query.

Guidelines:
- Use standard operations like: .find(), .aggregate(), .insert_one(), .insert_many(), .update_one(), .delete_one(), .drop()
- For joins, use the `$lookup` operator inside `.aggregate()`.
- Always prefer `.find()` instead of `.find_one()`.
- dont use .find_one() 
- always use .find()
- Make string matching case-insensitive using `$regex` with `$options: "i"` whenever applicable.
- Close all brackets properly in the query.
- Do not include comments or explanations.
- Do not return placeholder collection names like `db.collection`.
- Always match the collection name exactly as mentioned in the user query.
- find_one()

just only for refference i am giving an just example of how to use aggregate and lookup
example:

total number of comments of movie title ...

db.comments.aggregate([
  
    "$lookup": 
      "from": 
      "localField": ,
      "foreignField": 
      "as": "movie"
    
  
   "$unwind": "$movie" ,
   "$match":  "movie.title":  "$regex": "", "$options": "i"   ,
  
    "$group": 
      "_id": "",
      "total_comments": "": 1 
    
  
])


Return ONLY the full PyMongo query in this format:
db.collection.operation(arguments)

Here are the available collections and their fields:
{schema_text}

User: {user_question}
MongoDB Query:
"""



def create_summary_prompt(results_json):
    return f"""
You are a helpful assistant.

Your job is to summarize the following MongoDB result in plain, concise, and readable English.

Guidelines:
- Give one short line per document or grouped item in the result.
- Keep the order of results as shown.
- Do not use any Markdown or special formatting.
- Keep it clean, well spaced, and easy to read.
- Avoid unnecessary explanations—focus only on what's asked.
- Use line breaks for each item. No bullets, no headers.



- Only use operators available in MongoDB 6.0 or lower. Avoid "$sortArray", $function, or uncommon aggregation helpers.


Data:
{results_json}

Summary:
"""




# Cell 3: Gemini API call
def ask_gemini(prompt):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    try:
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        print("❌ Gemini error:", r.text)
        return None






# Cell 4: Operation Execution


# Cell 4: Operation Execution
def run_operation(query_text, collection):
    if "db.list_collection_names()" in query_text.replace(" ", ""):
        return {"collections": db.list_collection_names()}

    
    # Special command: drop a collection
    if ".drop()" in query_text.replace(" ", ""):
        db[collection].drop()
        return [{"dropped": collection}]

    # Clean markdown and whitespace
    query_text = query_text.replace("```python", "").replace("```", "").strip()

    
    # Detect operation
    operations = [
        "find", "aggregate", "insert_one", "insert_many","find_one",
        "update_one", "update_many", "delete_one", "delete_many"
    ]
    op = next((o for o in operations if f".{o}(" in query_text), None)
    if not op:
        raise ValueError("❌ Unsupported MongoDB operation.")

    # Extract arguments using regex
    # match = re.search(rf"db\.{collection}\.{op}\((.*)\)", query_text, re.DOTALL)
    match = re.search(rf"db\.{collection}\.{op}\(([\s\S]*?)\)", query_text.strip())

    if not match:
        raise ValueError("❌ Could not extract arguments from the query.")

    args_raw = match.group(1).strip().replace("\n", "")

    # Define expected arg type per operation
    op_arg_types = {
        "aggregate": "list",
        "insert_many": "list",
        "insert_one": "single",
        "delete_one": "single",
        "delete_many": "single",
        "update_one": "pair",
        "update_many": "pair",
        "find": "pair"
    }

    arg_type = op_arg_types.get(op, "single")

    # Parse arguments based on operation type
    try:
        if arg_type == "list":
            args_list = [ast.literal_eval(args_raw)]
        elif arg_type == "single":
            args_list = [ast.literal_eval(args_raw)]
        elif arg_type == "pair":
            split_args = re.split(r",(?![^{]*})", args_raw, maxsplit=1)
            args_list = [ast.literal_eval(arg.strip()) for arg in split_args]
        else:
            raise ValueError("❌ Unknown argument type")
    except Exception as e:
        raise ValueError(f"❌ Argument parsing error: {e}")

    # Run the MongoDB operation
    if op == "find":
        return list(db[collection].find(*args_list).limit(10))
    elif op == "find_one":
        return [db[collection].find_one(*args_list)]
    elif op == "aggregate":
        return list(db[collection].aggregate(*args_list))
    elif op == "insert_one":
        result = db[collection].insert_one(*args_list)
        return [{"inserted_id": str(result.inserted_id)}]
    elif op == "insert_many":
        result = db[collection].insert_many(*args_list)
        return [{"inserted_ids": [str(i) for i in result.inserted_ids]}]
    elif op == "update_one":
        result = db[collection].update_one(*args_list)
        return [{"matched": result.matched_count, "modified": result.modified_count}]
    elif op == "update_many":
        result = db[collection].update_many(*args_list)
        return [{"matched": result.matched_count, "modified": result.modified_count}]
    elif op == "delete_one":
        result = db[collection].delete_one(*args_list)
        return [{"deleted": result.deleted_count}]
    elif op == "delete_many":
        result = db[collection].delete_many(*args_list)
        return [{"deleted": result.deleted_count}]








# Cell 5: Main Chatbot
def chatbot():
    while True:
        user_input = input("🧠 Ask your MongoDB (or type 'exit'): ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Bye!")
            break

        print(f"\n🕒 [{datetime.datetime.now().strftime('%H:%M:%S')}] User: {user_input}")

        # Step 1: Generate query from Gemini
        prompt1 = create_query_prompt(user_input)
        query_text = ask_gemini(prompt1)
        if not query_text:
            continue

        query_text = query_text.replace("```python", "").replace("```", "").strip()
        print(f"\n🔎 MongoDB Query:\n{query_text}\n")

        # Step 2: Handle special command (list collections)
        if "db.list_collection_names()" in query_text.replace(" ", ""):
            collection = "special"  # dummy value for run_operation
        else:
            # Step 2a: Detect collection name using regex (even if not yet created)
            match = re.search(r"db\.(\w+)\.", query_text)
            collection = match.group(1) if match else None
            if not collection:
                print("❌ Could not detect collection.")
                continue

        # Step 3: Run the MongoDB operation
        try:
            results = run_operation(query_text, collection)
            results_json = json.dumps(results, indent=2, default=str)
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            continue

        # Step 4: Summarize the results with Gemini
        prompt2 = create_summary_prompt(results_json)
        answer = ask_gemini(prompt2)
        print(f"🗣️ Answer:\n{answer.strip()}\n")


# Cell 6: Run the chatbot
# chatbot()