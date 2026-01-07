# 💰 Secure AI Financial Analyst (RAG)

An AI-powered financial assistant that allows users to upload PDF bank statements and ask natural language questions about their spending habits.

Built using **Retrieval-Augmented Generation (RAG)**, this tool extracts transaction data, secures it per user, and uses LLMs to provide instant financial insights—like "How much did I spend on groceries?" or "List my transactions at Winco."

### 🚀 Live Demo
(https://your-app-link-here.streamlit.app)

---

### 🛠️ Features

* **🔐 Secure Authentication:** Full email/password login system powered by **Supabase Auth**.
* **📄 Smart PDF Ingestion:** Automatically reads, cleans, and structures messy bank statement PDFs into queryable JSON data.
* **🤖 Natural Language Q&A:** Users can chat with their data (e.g., *"What is my biggest expense this month?"*) powered by **GPT-4o-mini**.
* **🛡️ Data Isolation:** Implements multi-tenancy architecture where every document is tagged and locked to a specific User ID, ensuring privacy.
* **🔍 Semantic Search:** Uses vector embeddings to find relevant transactions even if the wording doesn't match exactly.

---

### 💻 Tech Stack

* **Frontend:** Python, Streamlit
* **Database & Auth:** Supabase (PostgreSQL, Vector Store)
* **AI Models:** OpenAI (GPT-4o-mini, text-embedding-3-small)
* **Libraries:** PyPDF2, Dotenv, Pandas

---

### ⚙️ How to Run Locally

**1. Clone the repository**
```bash```
git clone [https://github.com/yourusername/secure-finance-rag.git](https://github.com/yourusername/secure-finance-rag.git)
cd secure-finance-rag

**2. Install dependencies**
pip install -r requirements.txt

**3. Set up Environment Variables**
Create a .env file in the root directory and add your API keys:
Code snippet
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_anon_key"
OPENAI_KEY="your_openai_api_key"

**4. Run the app**
streamlit run src/app.py

📊 Logic Overview
The application follows a standard RAG (Retrieval-Augmented Generation) pipeline with added security layers:
Ingestion: The app reads the raw PDF and uses an LLM to "clean" the text into structured JSON (separating dates, merchants, and amounts).
Vectorization: The structured data is converted into vector embeddings using OpenAI's text-embedding-3-small.
Secure Storage: Data is stored in Supabase, tagged explicitly with the user's unique UUID (auth.users.id).
Retrieval: When a user asks a question, the system performs a semantic search only on rows matching their User ID.
Generation: The relevant transactions are fed into GPT-4o-mini to generate a plain-English answer.
