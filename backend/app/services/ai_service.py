from groq import Groq
import os
import json
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class AIService:
    """Service to interact with Groq API for skill extraction and roadmap generation"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
    
    async def extract_skills_from_resume(self, resume_text: str) -> Dict:
        """Extract skills and experience from resume text using AI"""
        prompt = f"""
        Analyze the following resume and extract structured information.
        
        Resume Text:
        {resume_text}
        
        Extract and return ONLY a JSON object with the following structure:
        {{
            "skills": ["skill1", "skill2", ...],
            "experience_years": <number>,
            "education": "highest degree",
            "job_titles": ["title1", "title2", ...]
        }}
        
        Focus on technical skills, frameworks, programming languages, and tools.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Error in AI skill extraction: {e}")
            return {
                "skills": [],
                "experience_years": 0,
                "education": "",
                "job_titles": []
            }
    
    async def analyze_skill_gap(self, current_skills: List[str], target_role: str, required_skills: List[str]) -> Dict:
        """Analyze skill gaps for a target role"""
        prompt = f"""
        Analyze the skill gap for a student targeting the role: {target_role}
        
        Current Skills: {', '.join(current_skills) if current_skills else 'None'}
        Required Skills for {target_role}: {', '.join(required_skills)}
        
        For each missing skill, determine the current level, required level, gap severity, and learning priority.
        
        Return ONLY a JSON object with this EXACT structure:
        {{
            "skill_gaps": [
                {{
                    "skill": "skill name",
                    "current_level": "None" or "Beginner" or "Intermediate" or "Advanced",
                    "required_level": "Beginner" or "Intermediate" or "Advanced" or "Expert",
                    "gap_severity": "High" or "Medium" or "Low",
                    "learning_priority": "High" or "Medium" or "Low"
                }}
            ],
            "matching_skills": ["skill1", "skill2"],
            "match_percentage": <number 0-100>,
            "priority_skills": ["most important skill to learn first"],
            "recommendations": ["recommendation 1", "recommendation 2"]
        }}
        
        gap_severity should be:
        - High: Critical skill for the role, student has no knowledge
        - Medium: Important skill, student has basic knowledge or skill is moderately important
        - Low: Nice to have skill, or student already has some experience
        
        learning_priority should be based on:
        - High: Must learn first, foundational for other skills
        - Medium: Important but can be learned after high priority skills
        - Low: Can be learned later, or nice to have
        """
        
        try:
            print(f"\n🤖 [AI SKILL GAP] Calling Groq API...")
            print(f"   Current skills: {current_skills}")
            print(f"   Required skills: {required_skills}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"✅ [AI SKILL GAP] Response received:")
            print(f"   Skill gaps: {len(result.get('skill_gaps', []))}")
            print(f"   Sample: {result.get('skill_gaps', [])[0] if result.get('skill_gaps') else 'None'}")
            
            return result
        except Exception as e:
            print(f"❌ [AI SKILL GAP] Error: {e}")
            print(f"   Using fallback data...")
            # Return structured fallback data
            missing_skills = list(set(required_skills) - set(current_skills))
            fallback = {
                "skill_gaps": [
                    {
                        "skill": skill,
                        "current_level": "None",
                        "required_level": "Intermediate",
                        "gap_severity": "Medium",
                        "learning_priority": "Medium"
                    }
                    for skill in missing_skills
                ],
                "matching_skills": list(set(required_skills) & set(current_skills)),
                "match_percentage": 0,
                "priority_skills": missing_skills[:3] if len(missing_skills) >= 3 else missing_skills,
                "recommendations": [
                    "Focus on foundational skills first",
                    "Practice with hands-on projects",
                    "Join online communities for support"
                ]
            }
            print(f"   Fallback skill gaps: {len(fallback['skill_gaps'])}")
            return fallback
    
    async def generate_learning_roadmap(
        self, 
        skill_gaps: List, 
        target_role: str, 
        available_hours_per_week: int,
        deadline_weeks: int,
        difficulty_level: str = "intermediate"
    ) -> Dict:
        """Generate a personalized learning roadmap"""
        # Ensure we have valid values for calculation
        if available_hours_per_week is None:
            available_hours_per_week = 10
        if deadline_weeks is None:
            deadline_weeks = 12
            
        total_hours = available_hours_per_week * deadline_weeks
        
        # Extract skill names from skill gap objects
        if skill_gaps and isinstance(skill_gaps[0], dict):
            skill_names = [gap['skill'] for gap in skill_gaps]
        else:
            skill_names = skill_gaps
        
        print(f"\n🤖 [AI ROADMAP] Generating roadmap...")
        print(f"   Skills to learn: {skill_names}")
        print(f"   Available hours: {total_hours}")
        print(f"   Duration: {deadline_weeks} weeks")
        print(f"   Difficulty: {difficulty_level}")
        
        # Calculate appropriate number of modules based on duration
        # Aim for roughly 2-4 weeks per module depending on duration
        if deadline_weeks <= 4:
            num_modules = "2-3"
            module_duration = "1-2 weeks"
        elif deadline_weeks <= 8:
            num_modules = "3-4"
            module_duration = "2 weeks"
        elif deadline_weeks <= 12:
            num_modules = "4-6"
            module_duration = "2-3 weeks"
        elif deadline_weeks <= 16:
            num_modules = "6-8"
            module_duration = "2-3 weeks"
        else:  # 24+ weeks
            num_modules = "8-12"
            module_duration = "2-3 weeks"
        
        # Adjust guidance based on difficulty level
        difficulty_guidance = {
            "beginner": "Focus on fundamentals and step-by-step tutorials. Include more introductory content, basic concepts, and foundational knowledge. Use beginner-friendly resources with detailed explanations. Start with absolute basics.",
            "intermediate": "Balance between theory and practice. Include intermediate tutorials and hands-on projects. Assume basic programming knowledge. Cover standard industry practices and common patterns.",
            "advanced": "Focus on advanced concepts, best practices, and complex projects. Include deep-dive content, architecture patterns, production-ready implementations, and cutting-edge techniques. Assume strong foundation."
        }
        
        guidance = difficulty_guidance.get(difficulty_level, difficulty_guidance["intermediate"])
        
        prompt = f"""
        Create a detailed learning roadmap for someone targeting: {target_role}
        
        PARAMETERS:
        - Skills to learn: {', '.join(skill_names)}
        - Total Duration: {deadline_weeks} WEEKS
        - Study Time: {available_hours_per_week} hours/week (Total: {total_hours} hours)
        - Difficulty Level: {difficulty_level.upper()}
        
        DIFFICULTY LEVEL REQUIREMENTS ({difficulty_level.upper()}):
        {guidance}
        
        Generate a structured learning plan with modules and resources.
        Return ONLY a JSON object:
        {{
            "modules": [
                {{
                    "title": "Module name",
                    "description": "What student will learn",
                    "skills_covered": ["skill1", "skill2"],
                    "estimated_hours": <number>,
                    "order": <number>,
                    "resources": [
                        {{
                            "title": "Resource name",
                            "url": "https://example.com/resource",
                            "description": "Brief description",
                            "estimated_hours": <number>,
                            "resource_type": "video|article|course|practice",
                            "order": <number>
                        }}
                    ]
                }}
            ]
        }}
        
        CRITICAL REQUIREMENTS:
        - Create EXACTLY {num_modules} modules to cover {deadline_weeks} weeks (each module ~{module_duration})
        - Distribute the {total_hours} total hours across ALL modules evenly
        - Each module should have 3-5 high-quality resources appropriate for {difficulty_level} level
        - For YouTube videos: Use ONLY popular channels with recent uploads (2023-2025)
          Examples: freeCodeCamp.org, Traversy Media, Fireship, Programming with Mosh, The Net Ninja, Corey Schafer
        - For articles: Use official documentation and reputable sites (MDN, W3Schools, Real Python, official docs)
        - For courses: Use free platforms (freeCodeCamp, Codecademy free tier, Coursera audit mode)
        - Avoid outdated resources or broken links
        - Use generic search-friendly URLs (e.g., "https://www.youtube.com/results?search_query=Python+Tutorial+2024")
        - Total hours should not exceed {total_hours}
        - Order modules logically: basics → intermediate → advanced → practical projects
        - Include at least one hands-on project or practice exercise per module
        """
        
        try:
            print(f"   Calling Groq API for roadmap generation...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"✅ [AI ROADMAP] Generated {len(result.get('modules', []))} modules")
            
            # Validate we got modules
            if not result.get("modules"):
                raise ValueError("AI did not return any modules")
                
            return result
        except Exception as e:
            print(f"❌ [AI ROADMAP] Error: {e}")
            print(f"   Using fallback modules...")
            # Return a basic fallback structure
            return {
                "modules": [
                    {
                        "title": f"Learn {skill_names[0] if skill_names else 'Fundamentals'}",
                        "description": "Get started with the basics",
                        "skills_covered": skill_names[:2] if len(skill_names) >= 2 else skill_names,
                        "estimated_hours": 20,
                        "order": 0,
                        "resources": [
                            {
                                "title": "Getting Started Guide",
                                "url": "https://www.example.com",
                                "description": "Beginner-friendly introduction",
                                "estimated_hours": 10,
                                "resource_type": "course",
                                "order": 0
                            }
                        ]
                    }
                ]
            }
    
    async def generate_module_summary(self, module_data: Dict, user_progress: Dict) -> str:
        """Generate a summary when a module is completed"""
        prompt = f"""
        Generate a motivational summary for a student who just completed a learning module.
        
        Module: {module_data.get('title')}
        Skills Covered: {', '.join(module_data.get('skills_covered', []))}
        Time Spent: {user_progress.get('time_spent_hours', 0)} hours
        Resources Completed: {user_progress.get('resources_completed', 0)}
        Resources Skipped: {user_progress.get('resources_skipped', 0)}
        
        Create a brief, encouraging summary (3-4 sentences) highlighting:
        - What they've accomplished
        - Skills they've gained
        - What's next
        
        Return only the summary text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Great job completing this module! Keep up the excellent work on your learning journey."
