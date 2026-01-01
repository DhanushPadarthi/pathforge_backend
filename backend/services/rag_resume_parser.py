"""
RAG-Enhanced Resume Skills Extraction
Combines retrieval from skill database with LLM generation for better accuracy
"""

from groq import Groq
import os
from typing import List, Dict
from dotenv import load_dotenv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

class RAGResumeParser:
    """Enhanced resume parser using Retrieval Augmented Generation"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),  # Unigrams and bigrams
            stop_words='english'
        )
    
    async def extract_skills_with_rag(
        self, 
        resume_text: str, 
        skill_database: List[Dict]
    ) -> Dict:
        """
        Extract skills using RAG approach:
        1. Retrieve relevant skills from database using TF-IDF similarity
        2. Augment LLM prompt with retrieved skills
        3. Generate structured extraction
        """
        
        # Step 1: Retrieve relevant skills from database
        relevant_skills = self._retrieve_relevant_skills(resume_text, skill_database)
        
        # Step 2: Create augmented prompt
        skill_names = [s['name'] for s in relevant_skills]
        skill_descriptions = [f"{s['name']}: {s.get('description', '')}" for s in relevant_skills]
        
        prompt = f"""
        You are an expert resume analyzer. Extract skills from the resume below.
        
        RESUME TEXT:
        {resume_text}
        
        RELEVANT SKILLS FROM OUR DATABASE:
        {chr(10).join(skill_descriptions[:20])}  # Top 20 most relevant
        
        INSTRUCTIONS:
        1. Identify which skills from our database are mentioned in the resume
        2. Include variations and synonyms (e.g., "React.js" for "React")
        3. Also extract skills NOT in our database if they're clearly technical skills
        4. Determine proficiency level based on context (projects, years, role)
        
        Return ONLY a JSON object:
        {{
            "matched_skills": [
                {{
                    "name": "skill name from our database",
                    "proficiency": "Beginner|Intermediate|Advanced|Expert",
                    "confidence": 0.0-1.0,
                    "evidence": "brief quote from resume showing this skill"
                }}
            ],
            "additional_skills": ["skill1", "skill2"],  // Not in our database
            "experience_years": <number>,
            "education": "highest degree",
            "job_titles": ["title1", "title2"]
        }}
        """
        
        try:
            # Step 3: Generate with LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  # Lower temperature for more consistent extraction
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            # Add metadata
            result['retrieval_count'] = len(relevant_skills)
            result['method'] = 'RAG'
            
            return result
            
        except Exception as e:
            print(f"❌ [RAG EXTRACTION] Error: {e}")
            return self._fallback_extraction(resume_text, skill_database)
    
    def _retrieve_relevant_skills(
        self, 
        resume_text: str, 
        skill_database: List[Dict],
        top_k: int = 30
    ) -> List[Dict]:
        """
        Retrieve most relevant skills from database using TF-IDF similarity
        """
        if not skill_database:
            return []
        
        try:
            # Create corpus: [resume_text, skill1_text, skill2_text, ...]
            skill_texts = []
            for skill in skill_database:
                # Combine name, category, and description for better matching
                skill_text = f"{skill['name']} {skill.get('category', '')} {skill.get('description', '')}"
                skill_texts.append(skill_text)
            
            # Fit TF-IDF on all documents
            corpus = [resume_text] + skill_texts
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            
            # Calculate cosine similarity between resume and each skill
            resume_vector = tfidf_matrix[0:1]
            skill_vectors = tfidf_matrix[1:]
            similarities = cosine_similarity(resume_vector, skill_vectors)[0]
            
            # Get top-k most similar skills
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            relevant_skills = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include if there's some similarity
                    skill = skill_database[idx].copy()
                    skill['similarity_score'] = float(similarities[idx])
                    relevant_skills.append(skill)
            
            print(f"✅ [RETRIEVAL] Found {len(relevant_skills)} relevant skills")
            if relevant_skills:
                print(f"   Top skill: {relevant_skills[0]['name']} (score: {relevant_skills[0]['similarity_score']:.3f})")
            
            return relevant_skills
            
        except Exception as e:
            print(f"⚠️ [RETRIEVAL] Error: {e}, using all skills")
            return skill_database[:30]  # Fallback to first 30
    
    def _fallback_extraction(self, resume_text: str, skill_database: List[Dict]) -> Dict:
        """Fallback to simple keyword matching if RAG fails"""
        resume_lower = resume_text.lower()
        matched_skills = []
        
        for skill in skill_database:
            if skill['name'].lower() in resume_lower:
                matched_skills.append({
                    "name": skill['name'],
                    "proficiency": "Intermediate",
                    "confidence": 0.7,
                    "evidence": "keyword match"
                })
        
        return {
            "matched_skills": matched_skills,
            "additional_skills": [],
            "experience_years": 0,
            "education": "",
            "job_titles": [],
            "retrieval_count": 0,
            "method": "fallback"
        }


class NLPResumeParser:
    """Traditional NLP approach using keyword extraction and pattern matching"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 3),
            stop_words='english'
        )
    
    def extract_skills_nlp(self, resume_text: str, skill_database: List[Dict]) -> Dict:
        """
        Extract skills using traditional NLP:
        1. TF-IDF keyword extraction
        2. Pattern matching
        3. Fuzzy string matching
        """
        
        # Extract keywords
        try:
            tfidf_matrix = self.vectorizer.fit_transform([resume_text])
            feature_names = self.vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            top_indices = np.argsort(scores)[-50:][::-1]
            keywords = [feature_names[i] for i in top_indices if scores[i] > 0]
            
        except:
            keywords = resume_text.lower().split()
        
        # Match keywords with skill database
        matched_skills = []
        resume_lower = resume_text.lower()
        
        for skill in skill_database:
            skill_name_lower = skill['name'].lower()
            
            # Exact match
            if skill_name_lower in resume_lower:
                matched_skills.append({
                    "name": skill['name'],
                    "proficiency": self._estimate_proficiency(resume_text, skill_name_lower),
                    "match_type": "exact"
                })
            # Keyword match
            elif any(skill_name_lower in keyword or keyword in skill_name_lower for keyword in keywords):
                matched_skills.append({
                    "name": skill['name'],
                    "proficiency": "Beginner",
                    "match_type": "keyword"
                })
        
        return {
            "skills": [s['name'] for s in matched_skills],
            "matched_skills": matched_skills,
            "keywords_found": keywords[:20],
            "method": "NLP"
        }
    
    def _estimate_proficiency(self, text: str, skill: str) -> str:
        """Estimate proficiency based on context keywords"""
        text_lower = text.lower()
        
        expert_keywords = ['expert', 'senior', 'lead', 'architect', 'advanced']
        intermediate_keywords = ['experience', 'proficient', 'worked with', 'developed']
        beginner_keywords = ['learning', 'basic', 'familiar', 'introduced']
        
        # Count occurrences near the skill mention
        skill_contexts = []
        for i, word in enumerate(text_lower.split()):
            if skill in word:
                # Get 10 words before and after
                start = max(0, i - 10)
                end = min(len(text_lower.split()), i + 10)
                context = ' '.join(text_lower.split()[start:end])
                skill_contexts.append(context)
        
        combined_context = ' '.join(skill_contexts)
        
        if any(kw in combined_context for kw in expert_keywords):
            return "Expert"
        elif any(kw in combined_context for kw in intermediate_keywords):
            return "Advanced"
        elif any(kw in combined_context for kw in beginner_keywords):
            return "Beginner"
        else:
            return "Intermediate"
