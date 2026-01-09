from groq import Groq
import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from services.youtube_validator import YouTubeValidator

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
        except Exception:
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception:
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
        
        RESOURCE URL REQUIREMENTS (IN ORDER OF PRIORITY):
        1. **YouTube Videos (PREFERRED)**: Use real YouTube video URLs whenever possible
           - Format: https://www.youtube.com/watch?v=VIDEO_ID
           - Popular channels: freeCodeCamp.org, Traversy Media, Fireship, Programming with Mosh, The Net Ninja, Corey Schafer, Academind, Kevin Powell, Web Dev Simplified
           - Use recent videos (2023-2025) from these verified channels
           - Example: "https://www.youtube.com/watch?v=rfscVS0vtbw" (Python Full Course)
           
        2. **Interactive Coding Platforms**: 
           - freeCodeCamp.org, Codecademy, Scrimba, CodePen, CodeSandbox
           - These embed well and are interactive
           
        3. **Documentation & Articles (use sparingly)**:
           - Official docs: React docs, Python docs, MDN Web Docs
           - Only use when video tutorials don't exist
        
        - Prioritize 70% YouTube videos, 20% interactive platforms, 10% documentation
        - Each resource MUST have a valid, specific URL (no placeholders or search URLs)
        - Use actual YouTube video URLs, not search results
        - Total hours should not exceed {total_hours}
        - Order modules logically: basics → intermediate → advanced → practical projects
        - Include at least one hands-on project or practice exercise per module
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate we got modules
            if not result.get("modules"):
                raise ValueError("AI did not return any modules")
                
            return result
        except Exception as e:
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
        except Exception:
            return "Great job completing this module! Keep up the excellent work on your learning journey."
    
    async def generate_project_ideas(
        self,
        skill_level: str,
        focus_areas: List[str],
        user_skills: List[str],
        roadmaps: List[Dict],
        count: int = 3
    ) -> List[Dict]:
        """Generate resume-ready project ideas based on user's skills and goals"""
        
        # Build context from user's data
        skills_context = ", ".join(user_skills) if user_skills else "beginner level"
        focus_context = ", ".join(focus_areas) if focus_areas else "general software development"
        roadmap_context = ""
        
        if roadmaps:
            roadmap_titles = [r.get("title", "") for r in roadmaps[:3]]
            roadmap_context = f"\nActive learning paths: {', '.join(roadmap_titles)}"
        
        prompt = f"""
        Generate {count} unique, resume-ready project ideas for a {skill_level} developer.
        
        User Context:
        - Current Skills: {skills_context}
        - Focus Areas: {focus_context}{roadmap_context}
        
        For each project, provide:
        1. A catchy, professional title
        2. A detailed description (2-3 sentences)
        3. Difficulty level (Beginner/Intermediate/Advanced)
        4. List of technologies to use (5-8 technologies)
        5. Estimated duration (e.g., "2-3 weeks", "1 month")
        6. Key learning outcomes (4-5 points)
        7. Resume impact statement (how it helps career)
        
        Make projects practical, impressive for employers, and aligned with current industry trends.
        Ensure projects demonstrate real-world problem-solving.
        
        Return ONLY a JSON array with this exact structure:
        [
            {{
                "title": "Project Title",
                "description": "Detailed description...",
                "difficulty": "Intermediate",
                "technologies": ["Tech1", "Tech2", ...],
                "estimated_duration": "2-3 weeks",
                "learning_outcomes": ["Outcome1", "Outcome2", ...],
                "resume_impact": "How this project strengthens your resume..."
            }}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Handle if result is wrapped in a key or is direct array
            if isinstance(result, dict):
                # Try common keys
                projects = result.get("projects") or result.get("project_ideas") or result.get("data") or []
            else:
                projects = result
            
            return projects if isinstance(projects, list) else []
            
        except Exception:
            # Return fallback projects
            return [
                {
                    "title": f"{focus_areas[0] if focus_areas else 'Full Stack'} Portfolio Project",
                    "description": "Build a comprehensive project showcasing your skills in modern development.",
                    "difficulty": skill_level.capitalize(),
                    "technologies": user_skills[:5] if user_skills else ["React", "Node.js", "MongoDB"],
                    "estimated_duration": "3-4 weeks",
                    "learning_outcomes": [
                        "End-to-end development experience",
                        "Deployment and DevOps practices",
                        "Code quality and testing",
                        "Project documentation"
                    ],
                    "resume_impact": "Demonstrates full project lifecycle management and technical versatility"
                }
            ]

    async def validate_and_fix_roadmap_resources(self, roadmap_data: Dict) -> Dict:
        """
        Validate YouTube URLs in roadmap resources and replace unavailable ones with alternatives
        """
        youtube_validator = YouTubeValidator()
        fixed_modules = []
        
        for module_data in roadmap_data.get("modules", []):
            fixed_resources = []
            
            for resource in module_data.get("resources", []):
                # Check if it's a YouTube URL
                if "youtube.com" in resource["url"] or "youtu.be" in resource["url"]:
                    try:
                        # Validate the YouTube video
                        is_available, video_id = await youtube_validator.is_video_available(resource["url"])
                        
                        if not is_available:
                            # Ask AI to suggest an alternative resource
                            alternative = await self._get_alternative_resource(
                                resource["title"],
                                resource.get("description", ""),
                                module_data.get("description", "")
                            )
                            
                            if alternative:
                                fixed_resources.append(alternative)
                            else:
                                # Keep the original but flag it
                                fixed_resources.append(resource)
                        else:
                            # Video is available, standardize URL
                            fixed_url = f"https://www.youtube.com/watch?v={video_id}"
                            resource["url"] = fixed_url
                            fixed_resources.append(resource)
                    
                    except Exception:
                        # Keep original resource if validation fails
                        fixed_resources.append(resource)
                else:
                    # Non-YouTube resources don't need validation
                    fixed_resources.append(resource)
            
            # Update module with fixed resources
            module_data["resources"] = fixed_resources
            fixed_modules.append(module_data)
        
        roadmap_data["modules"] = fixed_modules
        return roadmap_data

    async def _get_alternative_resource(self, title: str, description: str, module_description: str) -> Dict:
        """
        Use AI to suggest an alternative resource when YouTube video is unavailable
        """
        prompt = f"""
        A YouTube video resource is unavailable. Suggest ONE alternative resource.
        
        Resource: {title}
        Resource Description: {description}
        Module Context: {module_description}
        
        Return ONLY a JSON object with this structure:
        {{
            "title": "Alternative resource title",
            "url": "https://www.example.com/resource",
            "description": "Brief description of the alternative",
            "estimated_hours": <number>,
            "resource_type": "article|course|practice|documentation"
        }}
        
        Prefer resources from:
        1. freeCodeCamp.org (has many great tutorials)
        2. Coursera (free courses with great content)
        3. Udemy (popular paid courses)
        4. Official documentation
        5. Other reputable learning platforms
        
        Return valid, real URLs only - no placeholders.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result if result.get("url") else None
        except Exception:
            return None

# Create singleton instance
ai_service = AIService()

# Export individual functions for easier imports
async def generate_project_ideas(skill_level: str, focus_areas: List[str], user_skills: List[str], roadmaps: List[Dict], count: int = 3):
    return await ai_service.generate_project_ideas(skill_level, focus_areas, user_skills, roadmaps, count)