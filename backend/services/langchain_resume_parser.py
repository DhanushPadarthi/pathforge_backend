"""
LangChain-based Resume Skills Extraction
Uses LangChain for RAG pipeline with vector embeddings and retrieval chains
"""

from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from typing import List, Dict
import os
from dotenv import load_dotenv
import json

load_dotenv()


class LangChainResumeParser:
    """Resume parser using LangChain RAG pipeline"""
    
    def __init__(self):
        # Initialize Groq LLM via LangChain
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.2
        )
        
        # Initialize embeddings (free, local model)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        self.vector_store = None
        self.retrieval_chain = None
    
    async def build_skill_knowledge_base(self, skill_database: List[Dict]):
        """
        Build vector store from skill database
        This only needs to be done once (or when skills are updated)
        """
        # Convert skills to Documents
        documents = []
        for skill in skill_database:
            # Create rich text representation of each skill
            content = f"""
            Skill: {skill['name']}
            Category: {skill.get('category', 'General')}
            Description: {skill.get('description', 'Technical skill')}
            Related Terms: {', '.join(skill.get('related_terms', [skill['name']]))}
            """
            
            metadata = {
                'skill_id': str(skill.get('_id', '')),
                'name': skill['name'],
                'category': skill.get('category', '')
            }
            
            documents.append(Document(page_content=content, metadata=metadata))
        
        # Create vector store with FAISS (fast similarity search)
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        
        return self.vector_store
    
    async def extract_skills_with_langchain(
        self, 
        resume_text: str,
        skill_database: List[Dict],
        top_k: int = 20
    ) -> Dict:
        """
        Extract skills using LangChain RAG pipeline:
        1. Build/load vector store from skill database
        2. Retrieve relevant skills based on resume similarity
        3. Use LLM to extract and validate skills with retrieved context
        """
        
        # Step 1: Build knowledge base if not exists
        if self.vector_store is None:
            await self.build_skill_knowledge_base(skill_database)
        
        # Step 2: Retrieve relevant skills using semantic search
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k}
        )
        
        relevant_docs = retriever.get_relevant_documents(resume_text)
        
        # Extract skill names from retrieved docs
        retrieved_skills = [doc.metadata['name'] for doc in relevant_docs]
        retrieved_context = "\n".join([doc.page_content for doc in relevant_docs])
        
        # Step 3: Create extraction prompt template
        extraction_prompt = PromptTemplate(
            template="""You are an expert resume analyzer. Extract technical skills from the resume.

RESUME TEXT:
{resume_text}

RELEVANT SKILLS FROM OUR DATABASE (retrieved via semantic search):
{retrieved_skills}

DETAILED SKILL INFORMATION:
{skill_context}

TASK:
1. Identify which skills from our database are mentioned in the resume
2. Look for exact matches, synonyms, and related terms
3. Estimate proficiency level based on:
   - Years of experience mentioned
   - Project complexity
   - Job titles and roles
   - Keywords like "expert", "senior", "beginner", "learning"
4. Extract evidence (brief quote showing the skill)

Return ONLY valid JSON with this structure:
{{
    "matched_skills": [
        {{
            "name": "exact skill name from our database",
            "proficiency": "Beginner|Intermediate|Advanced|Expert",
            "confidence": 0.0-1.0,
            "evidence": "brief quote from resume"
        }}
    ],
    "additional_skills": ["skills not in our database"],
    "experience_years": <number>,
    "education": "highest degree",
    "job_titles": ["title1", "title2"]
}}""",
            input_variables=["resume_text", "retrieved_skills", "skill_context"]
        )
        
        # Step 4: Create and run the chain
        try:
            chain_input = {
                "resume_text": resume_text,
                "retrieved_skills": ", ".join(retrieved_skills),
                "skill_context": retrieved_context[:4000]  # Limit context size
            }
            
            formatted_prompt = extraction_prompt.format(**chain_input)
            
            # Invoke LLM
            response = self.llm.invoke(formatted_prompt)
            
            # Parse JSON response
            result = json.loads(response.content)
            
            # Add metadata
            result['retrieval_count'] = len(relevant_docs)
            result['retrieved_skills'] = retrieved_skills
            result['method'] = 'LangChain_RAG'
            
            return result
            
        except json.JSONDecodeError:
            return self._fallback_extraction(resume_text, retrieved_skills)
        except Exception:
            return self._fallback_extraction(resume_text, retrieved_skills)
    
    async def extract_with_retrieval_qa(
        self,
        resume_text: str,
        skill_database: List[Dict]
    ) -> Dict:
        """
        Alternative approach using LangChain's RetrievalQA chain
        Simpler but less customizable
        """
        if self.vector_store is None:
            await self.build_skill_knowledge_base(skill_database)
        
        # Create RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # "stuff" puts all docs in context
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 15})
        )
        
        query = f"""
        Based on the skill database provided, extract all technical skills mentioned in this resume:
        
        {resume_text}
        
        Return JSON format with matched skills and proficiency levels.
        """
        
        try:
            result = qa_chain.invoke({"query": query})
            return json.loads(result['result'])
        except:
            return {"matched_skills": [], "method": "RetrievalQA_fallback"}
    
    def _fallback_extraction(self, resume_text: str, retrieved_skills: List[str]) -> Dict:
        """Simple keyword matching fallback"""
        resume_lower = resume_text.lower()
        matched = []
        
        for skill in retrieved_skills:
            if skill.lower() in resume_lower:
                matched.append({
                    "name": skill,
                    "proficiency": "Intermediate",
                    "confidence": 0.6,
                    "evidence": "keyword match"
                })
        
        return {
            "matched_skills": matched,
            "additional_skills": [],
            "method": "fallback"
        }
    
    def save_vector_store(self, path: str = "./skill_vectorstore"):
        """Save vector store to disk for reuse"""
        if self.vector_store:
            self.vector_store.save_local(path)
    
    def load_vector_store(self, path: str = "./skill_vectorstore"):
        """Load pre-built vector store from disk"""
        try:
            self.vector_store = FAISS.load_local(
                path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return True
        except Exception:
            return False


class LangChainAdvancedExtractor:
    """
    Advanced LangChain implementation with:
    - Multi-step chains
    - Memory for context
    - Agent-based extraction
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.2
        )
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    
    async def extract_with_multi_step_chain(
        self,
        resume_text: str,
        skill_database: List[Dict]
    ) -> Dict:
        """
        Multi-step extraction:
        1. Extract keywords
        2. Retrieve relevant skills
        3. Validate and enrich
        """
        
        # Step 1: Keyword extraction
        keyword_prompt = PromptTemplate(
            template="Extract all technical keywords and skills from this resume. Return as comma-separated list:\n\n{resume}",
            input_variables=["resume"]
        )
        
        keywords_response = self.llm.invoke(keyword_prompt.format(resume=resume_text))
        keywords = keywords_response.content
        
        # Step 2: Semantic retrieval
        vector_store = FAISS.from_documents(
            [Document(page_content=f"{s['name']} {s.get('description', '')}") 
             for s in skill_database],
            self.embeddings
        )
        
        relevant_skills = vector_store.similarity_search(keywords, k=15)
        skill_names = [doc.page_content.split()[0] for doc in relevant_skills]
        
        # Step 3: Validation and enrichment
        validation_prompt = PromptTemplate(
            template="""
Given these potential skills: {skills}

And this resume: {resume}

Which skills are ACTUALLY mentioned? Return JSON with name, proficiency, evidence.
""",
            input_variables=["skills", "resume"]
        )
        
        final_response = self.llm.invoke(
            validation_prompt.format(skills=", ".join(skill_names), resume=resume_text)
        )
        
        print(f"✅ [STEP 3] Validation complete")
        
        try:
            return json.loads(final_response.content)
        except:
            return {"matched_skills": [], "method": "multi_step_chain"}
