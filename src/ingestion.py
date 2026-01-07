# 1. Setup
import os
import json
import PyPDF2
from openai import OpenAI as openai
from dotenv import load_dotenv
from supabase import create_client, Client

# Initialize the Ollama embedding model
class ingest_pdf:
    def __init__(self, url, key, openai_key):
        # Create a Supabase client connection
        self.supabase: Client = create_client(url, key)
        self.client = openai(api_key=openai_key)

    def get_embedding(self, text):
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def smart_clean_with_llm(self, page_text, page_num):
        """
        Extracts BOTH the transactions AND the account metadata (Name, Address, etc.)
        """
        print(f" AI is extracting full data from Page {page_num + 1}...")
        
        prompt = f"""
        Analyze the text from a bank statement page and output a JSON object containing both account details and transactions.

        JSON STRUCTURE:
        {{
            "metadata": {{
                "account_holder": "Name found (or null)",
                "account_number": "Account number found (or null)",
                "statement_period": "Dates found (or null)",
                "bank_name": "Bank Name (or null)"
            }},
            "transactions": [
                {{ 
                    "date": "MM/DD", 
                    "merchant": "Name", 
                    "amount": "-50.00", 
                    "type": "spending",
                    "running_balance": "450.00" 
                }}
            ]
        }}

        RULES:
        1. TRANSACTIONS: Extract every line item.
        2. AMOUNT vs BALANCE: 
           - The transaction amount is usually the smaller number (negative for spending).
           - The running balance is usually the larger number at the end of the row.
           - STORE THEM IN SEPARATE FIELDS. Do not confuse them.
        3. SPENDING: Ensure spending amounts are negative (e.g., -4.10).
        4. IF NO BALANCE FOUND: Set "running_balance" to null for that row.
        
        RAW PAGE TEXT:
        {page_text}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful financial assistant. Output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={'type':'json_object'}
        )
        return response.choices[0].message.content
    
    def process_pdf(self, file_object, user_name):

            reader = PyPDF2.PdfReader(file_object)

            print(f"Detected {len(reader.pages)} pages.")

            for i, page in enumerate(reader.pages):
                raw_text = page.extract_text()
                if not raw_text.strip(): continue

                json_string = self.smart_clean_with_llm(raw_text, i)
                
                # 2. CONVERT TO DICT (Crucial for Supabase metadata)
                try:
                    cleaned_json = json.loads(json_string)
                except json.JSONDecodeError:
                    print(f"⚠️ Warning: Page {i+1} did not return valid JSON. Skipping.")
                    continue
                
                vector = self.get_embedding(json_string)

                data = {"content": raw_text, "metadata": cleaned_json, "embedding": vector, "customer_name": user_name}

                self.supabase.table('documents').insert(data).execute()
                print(f"Stored Page {i+1} successfully.")


if __name__ == "__main__":
    # Load environment variables (API keys)
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    openai_key = os.getenv("OPENAI_KEY")

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(root, "assets", "statement.pdf")
    ingestor = ingest_pdf(url, key, openai_key)
    with open(file_path, "rb") as pdf:
        text = ingestor.process_pdf(pdf, "rohit narwal")
    print("Data Stored Sucessfully")
