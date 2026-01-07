import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("issue with the key or url")
    exit()

try:
    supabase: Client = create_client(url, key)
    print("client created successfully")

    response = supabase.table('documents').select("*").limit(1).execute()

    print(f"Connection created to db response: {response.data}")
except Exception as e:
    print(e)