import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()  # Forces loading .env file

# Import our custom classes (we will define these next)
from core.retrieval import HybridRetriever

# Global State
resources = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the Heavy Models ONCE
    print("🚀 Loading RAG Artifacts...")
    resources['retriever'] = HybridRetriever(artifact_dir="./artifacts")
    
    # Configure Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ WARNING: GEMINI_API_KEY not set!")
    else:
        genai.configure(api_key=api_key)
        resources['llm'] = genai.GenerativeModel('gemini-2.5-flash')
    
    print("✅ System Ready.")
    yield
    # Shutdown logic (if any)
    resources.clear()

app = FastAPI(title="Legal RAG API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class QueryRequest(BaseModel):
    query: str
    k: int = 5

class AnswerRequest(BaseModel):
    query: str

# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": 'retriever' in resources}

@app.post("/retrieve")
def search_documents(req: QueryRequest):
    """Returns raw chunks/sections (RAG + CAG)"""
    start = time.time()
    results = resources['retriever'].search(req.query, k=req.k)
    return {
        "latency_ms": (time.time() - start) * 1000,
        "results": results
    }

@app.post("/ask")
def ask_legal_assistant(req: AnswerRequest):
    """End-to-End RAG: Retrieves context -> Calls Gemini -> Returns Answer"""
    if 'llm' not in resources:
        raise HTTPException(status_code=503, detail="LLM service not configured")
    
    # 1. Retrieve MORE documents for comprehensive context
    retriever = resources['retriever']
    docs = retriever.search(req.query, k=10)  # Increased from 5 to 10
    
    # 2. Format Context with clear structure
    context_text = ""
    citations = []
    for i, d in enumerate(docs, 1):
        context_text += f"""
═══════════════════════════════════════════════════════════════
REFERENCE #{i}
DOCUMENT ID: {d.get('doc_id', 'Unknown')}
SOURCE TYPE: {d.get('source', 'Unknown')}
RELEVANCE: {d.get('type', 'Unknown')} (Score: {d.get('score', 'N/A')})

FULL CONTENT:
{d['text']}
═══════════════════════════════════════════════════════════════

"""
        citations.append(d.get('doc_id'))
        
    # 3. ENHANCED Prompt Engineering for Longer, More Detailed Responses
    prompt = f"""
You are PrismX AI, an expert Indian Legal Assistant specializing in comprehensive legal analysis.

🎯 YOUR PRIMARY MISSION:
Provide DETAILED, COMPREHENSIVE, and THOROUGH explanations based EXCLUSIVELY on the retrieved context below. Your responses should be extensive and informative.

📋 MANDATORY RESPONSE STRUCTURE:
1. **Direct Answer** (2-3 paragraphs minimum):
   - Provide the complete legal definition/explanation
   - Include ALL relevant details from the retrieved documents
   - Quote exact legal text when available

2. **Detailed Analysis** (3-4 paragraphs):
   - Break down each component of the law/section
   - Explain the implications and scope
   - Discuss key elements, conditions, and exceptions
   - Elaborate on penalties, procedures, or requirements

3. **Case Law Context** (if available):
   - Name the full case title with petitioner and respondent
   - Provide the date of judgment
   - Summarize the case facts in detail
   - Explain the court's reasoning and findings
   - Highlight the key legal principles established

4. **Practical Application** (2-3 paragraphs):
   - Explain how this law applies in real situations
   - Provide examples or scenarios from the case law
   - Discuss practical implications for legal practitioners

5. **Citations**:
   - Explicitly cite all document IDs used: [DOCUMENT ID: XYZ]
   - Reference specific sections, subsections, and clauses

⚠️ CRITICAL RULES:
✓ USE ONLY THE INFORMATION PROVIDED IN THE CONTEXT BELOW
✓ Generate responses of AT LEAST 300-500 words (aim for comprehensiveness)
✓ Write in clear, professional paragraphs (avoid bullet points for main content)
✓ Include ALL relevant information from retrieved documents
✓ Cite every piece of information with its [DOCUMENT ID]
✓ If multiple references exist, synthesize them into a cohesive response
✓ Trust the [DOCUMENT ID] labels - they are accurate
✗ DO NOT invent information not present in the context
✗ DO NOT provide brief or minimal answers
✗ ONLY if absolutely NO relevant information exists in context, state: "Based on the available legal database, I don't have sufficient information about [topic]. The retrieved documents do not contain relevant details."

═══════════════════════════════════════════════════════════════
📚 RETRIEVED LEGAL CONTEXT:
═══════════════════════════════════════════════════════════════
{context_text}

═══════════════════════════════════════════════════════════════
❓ USER QUESTION:
═══════════════════════════════════════════════════════════════
{req.query}

═══════════════════════════════════════════════════════════════
💬 YOUR COMPREHENSIVE RESPONSE:
═══════════════════════════════════════════════════════════════
"""
    
    # 4. Generate with specific configuration for longer outputs
    try:
        # Configure generation to encourage longer responses
        generation_config = {
            'temperature': 0.3,  # Lower temperature for factual accuracy
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 8192,  # Allow long responses
        }
        
        response = resources['llm'].generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return {
            "answer": response.text,
            "citations": citations,
            "context_used": len(docs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)