import os
from dotenv import load_dotenv
from openai import OpenAI as openai
from supabase import create_client, Client

class retrieval_app:
    def __init__(self, url, key, openai_key):
        self.supabase: Client = create_client(url, key)
        self.client = openai(api_key=openai_key)
    
    def get_embedding(self, text):
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def retrieve_documents(self, query, user_name=None):
        query_vector = self.get_embedding(query)

        if user_name == None:
            return 

        params = {
            "query_embedding": query_vector,
            "match_threshold": 0.25,
            "match_count": 5,
            "filter_user_name": user_name
        }

        response = self.supabase.rpc(fn = "match_documents", params = params).execute()
        return response.data

    def response(self, query, user_name):
        data = self.retrieve_documents(query, user_name)

        # DEBUG: See what the database actually found
        print(f"DEBUG: Found {len(data)} matches.")
        if not data:
            return f"Try again, try to enter the correct username :("
        
        # joining string from data into a single context
        context = ""
        for i in data:
            context += str(i['metadata']) + "\n\n---\n\n"
        context += "\n" 

        # Improved Prompting: Give the AI a specific role
        system_instruction = """
        You are a financial analyst assistant. 
        1. Use the provided Context (which contains JSON bank statement data) to answer the User Query.
        2. If the context contains multiple transactions for a merchant, sum them up accurately.
        3. Be concise and professional.
        4. Also list the proofs from the data so customer can manually verify too.
        5. Verify everything twice to make sure results aren't random.
        """

        prompt = f"""
        context: {context}


        user query: {query}"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content


if __name__ == "__main__":
    # loading vars from .env file
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    openai_key = os.getenv("OPENAI_KEY")
    
    app = retrieval_app(url, key, openai_key)
    print(app.response("how much money did I spend on winco foods?", "rohit narwal"))