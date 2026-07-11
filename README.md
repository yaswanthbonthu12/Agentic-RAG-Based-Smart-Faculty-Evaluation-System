# Agentic RAG-Based Faculty Recommendation System

An AI-powered Faculty Secommendation System built using **Agentic AI**, **Retrieval-Augmented Generation (RAG)**, **Hybrid Search**, **SQL Query Generation**, and **Large Language Models (LLMs)**. The system enables users to interact using natural language and retrieves insights related to faculty performance, student ratings, attendance, marks, and academic analytics.

By intelligently understanding user intent, the system dynamically selects the appropriate AI tool to provide fast, accurate, and context-aware responses.

---

# Features

* Agentic AI with automatic tool selection
* Natural language to SQL query generation
* Hybrid Retrieval-Augmented Generation (Dense + Sparse Retrieval)
* Pinecone Vector Database
* BM25 Sparse Retrieval
* Cohere Reranking
* Faculty feedback search
* Sentiment analysis of student feedback
* Lecturer comparison
* Lecturer recommendation
* Conversation history storage
* Interactive Streamlit Chat Interface

---

# System Architecture

```text
                    User
                      │
                      ▼
              Streamlit Chat UI
                      │
                      ▼
        LangChain Agent (Google Gemini)
                      │
        Determines User Intent
                      │
 ┌────────────┬─────────────┬──────────────┬──────────────┐
 │            │             │              │
 ▼            ▼             ▼              ▼
SQL Tool   Search Tool  Sentiment Tool  Recommendation Tool
               │
               ▼
        Hybrid Retriever
   (Dense + Sparse Retrieval)
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
 Dense Embeddings      BM25
 (mxbai-embed-large)
      │                 │
      └────────┬────────┘
               ▼
      Pinecone Vector Database
               │
               ▼
        Cohere Reranker
               │
               ▼
      Relevant Context Retrieved
               │
               ▼
   LangChain Agent (Google Gemini)
               │
               ▼
      Final Response to User
```

---

# 📂 Project Structure

```text
.
├── app.py                 # Streamlit user interface
├── agent.py               # LangChain Agent
├── tools.py               # AI Tools
├── retriever.py           # Hybrid Retrieval Pipeline
├── ingestion.py           # Data ingestion into Pinecone
├── feedback.csv           # Faculty feedback dataset
├── bm25.json              # BM25 sparse index
├── requirements.txt
└── README.md
```

---

# ⚙️ Technologies Used

### AI & LLM

* Google Gemini
* LangChain
* LangChain Agents

### Retrieval

* Pinecone Vector Database
* BM25 Sparse Retrieval
* Hybrid Search
* Cohere Reranker

### Database

* MySQL

### Frontend

* Streamlit

### Programming Language

* Python

---

# Workflow

## 1. Data Ingestion

The dataset is processed by:

* Creating LangChain Documents
* Generating Dense Embeddings
* Building BM25 Sparse Index
* Uploading vectors into Pinecone

---

## 2. User Interaction

Users ask questions in natural language through the Streamlit interface.

Example:

> Show the top 5 lecturers based on average rating.

---

## 3. Agent Decision Making

The LangChain Agent determines which tool should answer the question.

Available tools include:

* SQL Query Tool
* Feedback Search Tool
* Sentiment Analysis Tool
* Lecturer Comparison Tool
* Lecturer Recommendation Tool

---

## 4. SQL Query Generation

For analytical questions:

* The LLM converts natural language into SQL.
* SQL is executed against the MySQL database.
* Results are returned to the user.

Example:

User:

```text
Which lecturer has the highest average rating?
```

Generated SQL:

```sql
SELECT lecture_name,
ROUND(AVG(student_rating),2) AS avg_rating
FROM feedback
GROUP BY lecture_name
ORDER BY avg_rating DESC
LIMIT 1;
```

---

## 5. Feedback Retrieval

For feedback-related questions:

* Dense embedding search
* BM25 sparse search
* Hybrid retrieval using Pinecone
* Cohere reranking
* Final context passed to Gemini

---

## 6. Response Generation

Google Gemini formats the retrieved information into a natural language response.

---

# Supported Queries

### SQL Queries

* Average rating
* Pass percentage
* Fail percentage
* Attendance statistics
* Student marks
* Lecturer rankings
* Department statistics
* Subject statistics

Examples:

* Show the top 5 lecturers based on average rating.
* What is the pass percentage?
* Which department has the highest average rating?
* Show the average attendance.
* What is the highest student mark?

---

### Feedback Search

Examples:

* What do students say about Meghana Singh?
* Show feedback for Ganesh Singh.
* What are the common complaints about Arjun Gupta?

---

### Sentiment Analysis

Examples:

* Summarize feedback for Meghana Singh.
* Analyze student opinions about Kavya Verma.

---

### Lecturer Comparison

Examples:

* Compare Meghana Singh and Ganesh Singh.

---

### Recommendation

Examples:

* Recommend the best lecturer for Database Management Systems.

---

# AI Components

* LangChain Agent
* Google Gemini LLM
* Hybrid Retrieval
* Pinecone Vector Search
* BM25 Sparse Retrieval
* Cohere Reranking
* SQL Query Generation
* Tool Calling

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/yaswanthbonthu12/Agentic-RAG-Based-Smart-Faculty-Evaluation-System.git
```

## 2. Navigate to the Project Directory

```bash
cd Agentic-RAG-Based-Smart-Faculty-Evaluation-System
```

## 3. Create a Virtual Environment (Optional)

```bash
python -m venv venv
```

### Activate the Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure Environment Variables

Create a `.env` file in the project root and add your API keys:

```env
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
COHERE_API_KEY=your_cohere_api_key
```

## 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at:

```text
http://localhost:8501
```

---

# Author

**Yaswanth**
