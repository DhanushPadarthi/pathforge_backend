"""
Seed script to populate the database with initial data
Run this script after setting up the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Sample career roles
CAREER_ROLES = [
    {
        "title": "Full Stack Developer",
        "description": "Develops both frontend and backend of web applications",
        "required_skills": [
            "HTML", "CSS", "JavaScript", "React", "Node.js", "Express.js",
            "MongoDB", "SQL", "Git", "REST APIs"
        ],
        "recommended_skills": ["TypeScript", "Docker", "AWS", "Redux", "GraphQL"],
        "average_learning_hours": 200,
        "difficulty_level": "intermediate",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Frontend Developer",
        "description": "Specializes in building user interfaces and client-side applications",
        "required_skills": [
            "HTML", "CSS", "JavaScript", "React", "Responsive Design",
            "Git", "Web Performance", "Accessibility"
        ],
        "recommended_skills": ["TypeScript", "Next.js", "Tailwind CSS", "Testing", "Webpack"],
        "average_learning_hours": 150,
        "difficulty_level": "beginner",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Backend Developer",
        "description": "Focuses on server-side logic, databases, and API development",
        "required_skills": [
            "Python", "Node.js", "SQL", "REST APIs", "Database Design",
            "Authentication", "Git", "Linux"
        ],
        "recommended_skills": ["Docker", "Microservices", "Redis", "Message Queues", "AWS"],
        "average_learning_hours": 180,
        "difficulty_level": "intermediate",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Data Scientist",
        "description": "Analyzes data and builds machine learning models",
        "required_skills": [
            "Python", "Statistics", "Machine Learning", "Pandas", "NumPy",
            "Data Visualization", "SQL", "Jupyter Notebooks"
        ],
        "recommended_skills": ["Deep Learning", "TensorFlow", "PyTorch", "Big Data", "Cloud Platforms"],
        "average_learning_hours": 250,
        "difficulty_level": "advanced",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "DevOps Engineer",
        "description": "Manages infrastructure, deployment, and automation",
        "required_skills": [
            "Linux", "Docker", "Kubernetes", "CI/CD", "Git",
            "Cloud Platforms", "Infrastructure as Code", "Monitoring"
        ],
        "recommended_skills": ["Terraform", "Ansible", "Jenkins", "Security", "Networking"],
        "average_learning_hours": 200,
        "difficulty_level": "advanced",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Mobile App Developer",
        "description": "Builds mobile applications for iOS and Android",
        "required_skills": [
            "React Native", "JavaScript", "Mobile UI/UX", "API Integration",
            "Git", "App Store Guidelines"
        ],
        "recommended_skills": ["Swift", "Kotlin", "Flutter", "Firebase", "Testing"],
        "average_learning_hours": 180,
        "difficulty_level": "intermediate",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "AWS Cloud Engineer",
        "description": "Expert in Amazon Web Services and cloud architecture",
        "required_skills": [
            "AWS", "EC2", "S3", "Lambda", "VPC", "IAM", "CloudFormation",
            "Networking", "Security", "Linux"
        ],
        "recommended_skills": ["Terraform", "Docker", "Kubernetes", "Python", "Monitoring"],
        "average_learning_hours": 200,
        "difficulty_level": "intermediate",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Software Engineer (DSA Focus)",
        "description": "Master data structures and algorithms for technical interviews",
        "required_skills": [
            "Data Structures", "Algorithms", "Problem Solving", "Python", "Java",
            "Time Complexity", "Space Complexity", "Recursion"
        ],
        "recommended_skills": ["Dynamic Programming", "Graph Algorithms", "System Design", "LeetCode"],
        "average_learning_hours": 300,
        "difficulty_level": "intermediate",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Machine Learning Engineer",
        "description": "Build and deploy ML models and AI systems",
        "required_skills": [
            "Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
            "NumPy", "Pandas", "Mathematics", "Statistics"
        ],
        "recommended_skills": ["MLOps", "Docker", "Kubernetes", "AWS", "Computer Vision", "NLP"],
        "average_learning_hours": 400,
        "difficulty_level": "advanced",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Cybersecurity Specialist",
        "description": "Protect systems and networks from security threats",
        "required_skills": [
            "Network Security", "Ethical Hacking", "Penetration Testing", "Linux",
            "Security Tools", "Cryptography", "OWASP"
        ],
        "recommended_skills": ["Kali Linux", "Burp Suite", "Metasploit", "Python", "Cloud Security"],
        "average_learning_hours": 250,
        "difficulty_level": "advanced",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "title": "Blockchain Developer",
        "description": "Develop smart contracts and decentralized applications",
        "required_skills": [
            "Solidity", "Blockchain Fundamentals", "Smart Contracts", "Web3.js",
            "Ethereum", "JavaScript", "Cryptography"
        ],
        "recommended_skills": ["React", "Node.js", "DeFi", "NFTs", "Security Auditing"],
        "average_learning_hours": 280,
        "difficulty_level": "advanced",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

# Sample skills
SKILLS = [
    {"name": "Python", "category": "programming", "description": "High-level programming language"},
    {"name": "JavaScript", "category": "programming", "description": "Web programming language"},
    {"name": "React", "category": "framework", "description": "Frontend JavaScript library"},
    {"name": "Node.js", "category": "framework", "description": "JavaScript runtime for backend"},
    {"name": "MongoDB", "category": "tool", "description": "NoSQL database"},
    {"name": "Docker", "category": "tool", "description": "Containerization platform"},
    {"name": "Git", "category": "tool", "description": "Version control system"},
    {"name": "AWS", "category": "tool", "description": "Cloud computing platform"},
    {"name": "Machine Learning", "category": "skill", "description": "AI and ML algorithms"},
    {"name": "Problem Solving", "category": "soft-skill", "description": "Critical thinking"},
]

# Sample admin user
ADMIN_USER = {
    "firebase_uid": "admin_uid_12345",
    "email": "admin@pathforge.com",
    "name": "Admin User",
    "role": "admin",
    "profile_completed": True,
    "has_resume": False,
    "current_skills": [],
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

async def seed_database():
    """Seed the database with initial data"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
        db = client[os.getenv("DATABASE_NAME", "pathforge")]
        
        print("🌱 Starting database seeding...")
        
        # Seed career roles
        roles_collection = db["career_roles"]
        existing_roles = await roles_collection.count_documents({})
        
        if existing_roles == 0:
            await roles_collection.insert_many(CAREER_ROLES)
            print(f"✓ Inserted {len(CAREER_ROLES)} career roles")
        else:
            # Update existing roles - add new ones
            for role in CAREER_ROLES:
                await roles_collection.update_one(
                    {"title": role["title"]},
                    {"$set": role},
                    upsert=True
                )
            print(f"✓ Updated/inserted {len(CAREER_ROLES)} career roles")
        
        # Seed skills
        skills_collection = db["skills"]
        existing_skills = await skills_collection.count_documents({})
        
        if existing_skills == 0:
            await skills_collection.insert_many(SKILLS)
            print(f"✓ Inserted {len(SKILLS)} skills")
        else:
            print(f"⊘ Skills already exist ({existing_skills} found)")
        
        # Seed admin user
        users_collection = db["users"]
        existing_admin = await users_collection.find_one({"email": "admin@pathforge.com"})
        
        if not existing_admin:
            await users_collection.insert_one(ADMIN_USER)
            print("✓ Created admin user")
        else:
            print("⊘ Admin user already exists")
        
        print("\n✅ Database seeding completed successfully!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")

if __name__ == "__main__":
    asyncio.run(seed_database())
