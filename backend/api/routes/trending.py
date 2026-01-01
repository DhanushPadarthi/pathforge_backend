from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import asyncio

router = APIRouter()

class TrendingSkill(BaseModel):
    skill_name: str
    category: str
    demand_score: int  # 1-100
    growth_rate: str  # e.g., "+25%", "-5%"
    average_salary: str
    job_openings: int
    trending_since: str
    related_skills: List[str]
    top_companies: List[str]
    career_paths: List[str]

class SkillCategory(BaseModel):
    category: str
    skills: List[TrendingSkill]

# Trending skills data (in production, this would come from APIs like LinkedIn, Indeed, etc.)
TRENDING_SKILLS_DATA = [
    {
        "skill_name": "Generative AI",
        "category": "AI/ML",
        "demand_score": 98,
        "growth_rate": "+156%",
        "average_salary": "$145,000 - $200,000",
        "job_openings": 45000,
        "trending_since": "2023",
        "related_skills": ["LLMs", "Prompt Engineering", "RAG", "Vector Databases", "Python"],
        "top_companies": ["OpenAI", "Google", "Microsoft", "Anthropic", "Meta"],
        "career_paths": ["AI Engineer", "ML Engineer", "AI Research Scientist", "Prompt Engineer"]
    },
    {
        "skill_name": "Kubernetes",
        "category": "DevOps",
        "demand_score": 94,
        "growth_rate": "+78%",
        "average_salary": "$130,000 - $180,000",
        "job_openings": 38000,
        "trending_since": "2020",
        "related_skills": ["Docker", "Helm", "CI/CD", "Terraform", "AWS/Azure"],
        "top_companies": ["Google", "Amazon", "Microsoft", "Netflix", "Uber"],
        "career_paths": ["DevOps Engineer", "Cloud Architect", "Site Reliability Engineer", "Platform Engineer"]
    },
    {
        "skill_name": "React & Next.js",
        "category": "Web Development",
        "demand_score": 92,
        "growth_rate": "+65%",
        "average_salary": "$110,000 - $160,000",
        "job_openings": 52000,
        "trending_since": "2019",
        "related_skills": ["TypeScript", "Tailwind CSS", "Node.js", "GraphQL", "REST APIs"],
        "top_companies": ["Meta", "Vercel", "Netflix", "Airbnb", "Shopify"],
        "career_paths": ["Frontend Engineer", "Full Stack Developer", "UI Engineer", "Web Developer"]
    },
    {
        "skill_name": "Cybersecurity",
        "category": "Security",
        "demand_score": 96,
        "growth_rate": "+89%",
        "average_salary": "$120,000 - $175,000",
        "job_openings": 41000,
        "trending_since": "2021",
        "related_skills": ["Penetration Testing", "SIEM", "Zero Trust", "Cloud Security", "Threat Intelligence"],
        "top_companies": ["Crowdstrike", "Palo Alto Networks", "Microsoft", "Google", "Cisco"],
        "career_paths": ["Security Engineer", "Penetration Tester", "Security Analyst", "CISO"]
    },
    {
        "skill_name": "Rust",
        "category": "Programming",
        "demand_score": 88,
        "growth_rate": "+112%",
        "average_salary": "$140,000 - $190,000",
        "job_openings": 15000,
        "trending_since": "2022",
        "related_skills": ["Systems Programming", "WebAssembly", "Blockchain", "Performance Optimization"],
        "top_companies": ["Amazon", "Microsoft", "Discord", "Dropbox", "Meta"],
        "career_paths": ["Systems Engineer", "Blockchain Developer", "Backend Engineer", "Performance Engineer"]
    },
    {
        "skill_name": "AWS & Cloud Architecture",
        "category": "Cloud",
        "demand_score": 95,
        "growth_rate": "+72%",
        "average_salary": "$125,000 - $185,000",
        "job_openings": 48000,
        "trending_since": "2018",
        "related_skills": ["EC2", "Lambda", "S3", "CloudFormation", "Terraform", "Azure"],
        "top_companies": ["Amazon", "Netflix", "Airbnb", "Capital One", "Spotify"],
        "career_paths": ["Cloud Engineer", "Solutions Architect", "Cloud Consultant", "DevOps Engineer"]
    },
    {
        "skill_name": "Data Engineering",
        "category": "Data",
        "demand_score": 91,
        "growth_rate": "+82%",
        "average_salary": "$130,000 - $180,000",
        "job_openings": 35000,
        "trending_since": "2021",
        "related_skills": ["Apache Spark", "Airflow", "Snowflake", "DBT", "Python", "SQL"],
        "top_companies": ["Netflix", "Uber", "Airbnb", "Spotify", "Meta"],
        "career_paths": ["Data Engineer", "Analytics Engineer", "ML Engineer", "Data Architect"]
    },
    {
        "skill_name": "Go (Golang)",
        "category": "Programming",
        "demand_score": 87,
        "growth_rate": "+68%",
        "average_salary": "$120,000 - $170,000",
        "job_openings": 22000,
        "trending_since": "2020",
        "related_skills": ["Microservices", "Docker", "Kubernetes", "gRPC", "REST APIs"],
        "top_companies": ["Google", "Uber", "Twitch", "Docker", "HashiCorp"],
        "career_paths": ["Backend Engineer", "Systems Engineer", "DevOps Engineer", "Cloud Engineer"]
    },
    {
        "skill_name": "TypeScript",
        "category": "Web Development",
        "demand_score": 90,
        "growth_rate": "+95%",
        "average_salary": "$115,000 - $165,000",
        "job_openings": 44000,
        "trending_since": "2020",
        "related_skills": ["React", "Node.js", "Angular", "Vue.js", "GraphQL"],
        "top_companies": ["Microsoft", "Google", "Meta", "Airbnb", "Slack"],
        "career_paths": ["Full Stack Developer", "Frontend Engineer", "Backend Engineer", "Software Engineer"]
    },
    {
        "skill_name": "Blockchain & Web3",
        "category": "Blockchain",
        "demand_score": 85,
        "growth_rate": "+145%",
        "average_salary": "$130,000 - $200,000",
        "job_openings": 18000,
        "trending_since": "2021",
        "related_skills": ["Solidity", "Smart Contracts", "Ethereum", "DeFi", "NFTs"],
        "top_companies": ["Coinbase", "ConsenSys", "Chainlink", "Polygon", "OpenSea"],
        "career_paths": ["Blockchain Developer", "Smart Contract Engineer", "Web3 Developer", "DeFi Engineer"]
    }
]

@router.get("/skills", response_model=List[TrendingSkill])
async def get_trending_skills(
    category: Optional[str] = None,
    limit: Optional[int] = 10
):
    """
    Get trending skills based on market demand analysis
    """
    try:
        skills = TRENDING_SKILLS_DATA.copy()
        
        # Filter by category if provided
        if category:
            skills = [s for s in skills if s["category"].lower() == category.lower()]
        
        # Sort by demand score
        skills.sort(key=lambda x: x["demand_score"], reverse=True)
        
        # Limit results
        skills = skills[:limit]
        
        return skills
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending skills: {str(e)}")

@router.get("/categories")
async def get_skill_categories():
    """
    Get all unique skill categories
    """
    try:
        categories = list(set(skill["category"] for skill in TRENDING_SKILLS_DATA))
        categories.sort()
        
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")

@router.get("/skills/{skill_name}")
async def get_skill_details(skill_name: str):
    """
    Get detailed information about a specific skill
    """
    try:
        skill = next(
            (s for s in TRENDING_SKILLS_DATA if s["skill_name"].lower() == skill_name.lower()),
            None
        )
        
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        return skill
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch skill details: {str(e)}")

@router.get("/analytics")
async def get_market_analytics():
    """
    Get overall market analytics and trends
    """
    try:
        total_openings = sum(skill["job_openings"] for skill in TRENDING_SKILLS_DATA)
        avg_growth = sum(
            int(skill["growth_rate"].replace("+", "").replace("%", "")) 
            for skill in TRENDING_SKILLS_DATA
        ) / len(TRENDING_SKILLS_DATA)
        
        # Top categories by demand
        category_demand = {}
        for skill in TRENDING_SKILLS_DATA:
            cat = skill["category"]
            if cat not in category_demand:
                category_demand[cat] = {"total_jobs": 0, "avg_score": 0, "count": 0}
            category_demand[cat]["total_jobs"] += skill["job_openings"]
            category_demand[cat]["avg_score"] += skill["demand_score"]
            category_demand[cat]["count"] += 1
        
        for cat in category_demand:
            category_demand[cat]["avg_score"] /= category_demand[cat]["count"]
        
        top_categories = sorted(
            category_demand.items(),
            key=lambda x: x[1]["avg_score"],
            reverse=True
        )[:5]
        
        return {
            "total_job_openings": total_openings,
            "average_growth_rate": f"+{avg_growth:.1f}%",
            "total_skills_tracked": len(TRENDING_SKILLS_DATA),
            "top_categories": [
                {
                    "category": cat,
                    "avg_demand_score": data["avg_score"],
                    "total_jobs": data["total_jobs"]
                }
                for cat, data in top_categories
            ],
            "fastest_growing": sorted(
                TRENDING_SKILLS_DATA,
                key=lambda x: int(x["growth_rate"].replace("+", "").replace("%", "")),
                reverse=True
            )[:5]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")
