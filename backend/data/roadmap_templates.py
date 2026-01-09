"""
Roadmap Templates
Pre-defined learning roadmaps for popular tech stacks and career paths
"""

ROADMAP_TEMPLATES = [
    {
        "title": "AWS Cloud Practitioner",
        "description": "Master Amazon Web Services fundamentals and get AWS Certified Cloud Practitioner certified",
        "category": "cloud",
        "difficulty": "beginner",
        "estimated_weeks": 8,
        "modules": [
            {
                "title": "Week 1: Cloud Computing Fundamentals",
                "description": "Understanding cloud concepts and AWS basics",
                "order": 0,
                "resources": [
                    {"title": "What is Cloud Computing?", "type": "video", "url": "https://www.youtube.com/watch?v=dH0yz-Osy54", "estimated_minutes": 15},
                    {"title": "AWS Cloud Practitioner Introduction", "type": "video", "url": "https://www.youtube.com/watch?v=3hLmDS179YE", "estimated_minutes": 120},
                    {"title": "AWS Free Tier Setup", "type": "article", "url": "https://aws.amazon.com/free/", "estimated_minutes": 30},
                ]
            },
            {
                "title": "Week 2: AWS Core Services",
                "description": "EC2, S3, and basic AWS services",
                "order": 1,
                "resources": [
                    {"title": "AWS EC2 Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=iHX-jtKIVNA", "estimated_minutes": 45},
                    {"title": "AWS S3 Complete Guide", "type": "video", "url": "https://www.youtube.com/watch?v=tfU0JEZjcsg", "estimated_minutes": 60},
                    {"title": "Practice: Launch Your First EC2 Instance", "type": "exercise", "url": "https://aws.amazon.com/getting-started/hands-on/launch-a-virtual-machine/", "estimated_minutes": 45},
                ]
            },
            {
                "title": "Week 3: Networking & Security",
                "description": "VPC, IAM, and AWS security basics",
                "order": 2,
                "resources": [
                    {"title": "AWS VPC Explained", "type": "video", "url": "https://www.youtube.com/watch?v=bGDMeD6kOz0", "estimated_minutes": 40},
                    {"title": "AWS IAM Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=iF9fs8Rw4Uo", "estimated_minutes": 35},
                ]
            },
            {
                "title": "Week 4: Databases & Storage",
                "description": "RDS, DynamoDB, and storage options",
                "order": 3,
                "resources": [
                    {"title": "AWS RDS vs DynamoDB", "type": "video", "url": "https://www.youtube.com/watch?v=sI-zciHAh-4", "estimated_minutes": 25},
                    {"title": "AWS Database Services", "type": "video", "url": "https://www.youtube.com/watch?v=eMzCI7S1P9M", "estimated_minutes": 45},
                ]
            }
        ]
    },
    {
        "title": "Data Structures & Algorithms Mastery",
        "description": "Complete guide to DSA for coding interviews and competitive programming",
        "category": "computer-science",
        "difficulty": "intermediate",
        "estimated_weeks": 12,
        "modules": [
            {
                "title": "Week 1-2: Arrays & Strings",
                "description": "Master array manipulation and string algorithms",
                "order": 0,
                "resources": [
                    {"title": "Arrays Data Structure", "type": "video", "url": "https://www.youtube.com/watch?v=QJNwK2uJyGs", "estimated_minutes": 30},
                    {"title": "Two Pointer Technique", "type": "video", "url": "https://www.youtube.com/watch?v=On03HWe2tZM", "estimated_minutes": 25},
                    {"title": "Practice: LeetCode Easy Arrays", "type": "exercise", "url": "https://leetcode.com/tag/array/", "estimated_minutes": 180},
                ]
            },
            {
                "title": "Week 3-4: Linked Lists",
                "description": "Single, double, and circular linked lists",
                "order": 1,
                "resources": [
                    {"title": "Linked Lists Explained", "type": "video", "url": "https://www.youtube.com/watch?v=njTh_OwMljA", "estimated_minutes": 45},
                    {"title": "Reverse a Linked List", "type": "video", "url": "https://www.youtube.com/watch?v=G0_I-ZF0S38", "estimated_minutes": 20},
                    {"title": "Practice: LinkedList Problems", "type": "exercise", "url": "https://leetcode.com/tag/linked-list/", "estimated_minutes": 180},
                ]
            },
            {
                "title": "Week 5-6: Stacks & Queues",
                "description": "LIFO and FIFO data structures",
                "order": 2,
                "resources": [
                    {"title": "Stack & Queue Implementation", "type": "video", "url": "https://www.youtube.com/watch?v=wjI1WNcIntg", "estimated_minutes": 40},
                    {"title": "Stack Applications", "type": "video", "url": "https://www.youtube.com/watch?v=O1KeXo8lE8A", "estimated_minutes": 30},
                ]
            },
            {
                "title": "Week 7-8: Trees & BST",
                "description": "Binary trees and binary search trees",
                "order": 3,
                "resources": [
                    {"title": "Binary Trees", "type": "video", "url": "https://www.youtube.com/watch?v=fAAZixBzIAI", "estimated_minutes": 50},
                    {"title": "Tree Traversals", "type": "video", "url": "https://www.youtube.com/watch?v=9RHO6jU--GU", "estimated_minutes": 35},
                    {"title": "Practice: Tree Problems", "type": "exercise", "url": "https://leetcode.com/tag/tree/", "estimated_minutes": 240},
                ]
            },
            {
                "title": "Week 9-10: Graphs & Graph Algorithms",
                "description": "Graph representations, BFS, DFS, and shortest paths",
                "order": 4,
                "resources": [
                    {"title": "Graph Theory Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=tWVWeAqZ0WU", "estimated_minutes": 60},
                    {"title": "BFS vs DFS", "type": "video", "url": "https://www.youtube.com/watch?v=pcKY4hjDrxk", "estimated_minutes": 25},
                    {"title": "Dijkstra's Algorithm", "type": "video", "url": "https://www.youtube.com/watch?v=pVfj6mxhdMw", "estimated_minutes": 30},
                ]
            },
            {
                "title": "Week 11-12: Dynamic Programming",
                "description": "Master DP patterns and problem solving",
                "order": 5,
                "resources": [
                    {"title": "Dynamic Programming for Beginners", "type": "video", "url": "https://www.youtube.com/watch?v=oBt53YbR9Kk", "estimated_minutes": 90},
                    {"title": "Common DP Patterns", "type": "video", "url": "https://www.youtube.com/watch?v=mBNrRy2_hVs", "estimated_minutes": 45},
                    {"title": "Practice: DP Problems", "type": "exercise", "url": "https://leetcode.com/tag/dynamic-programming/", "estimated_minutes": 300},
                ]
            }
        ]
    },
    {
        "title": "Python Full Stack Developer",
        "description": "Become a full stack developer using Python, Django/FastAPI, and React",
        "category": "web-development",
        "difficulty": "intermediate",
        "estimated_weeks": 16,
        "modules": [
            {
                "title": "Week 1-2: Python Fundamentals",
                "description": "Master Python programming basics",
                "order": 0,
                "resources": [
                    {"title": "Python Full Course", "type": "video", "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc", "estimated_minutes": 280},
                    {"title": "OOP in Python", "type": "video", "url": "https://www.youtube.com/watch?v=Ej_02ICOIgs", "estimated_minutes": 45},
                ]
            },
            {
                "title": "Week 3-5: FastAPI Backend",
                "description": "Build RESTful APIs with FastAPI",
                "order": 1,
                "resources": [
                    {"title": "FastAPI Complete Course", "type": "video", "url": "https://www.youtube.com/watch?v=0sOvCWFmrtA", "estimated_minutes": 240},
                    {"title": "FastAPI + MongoDB", "type": "video", "url": "https://www.youtube.com/watch?v=G8MsHbCHPXE", "estimated_minutes": 90},
                ]
            },
            {
                "title": "Week 6-8: React Frontend",
                "description": "Build modern UIs with React",
                "order": 2,
                "resources": [
                    {"title": "React Full Course 2024", "type": "video", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8", "estimated_minutes": 300},
                    {"title": "React Hooks Deep Dive", "type": "video", "url": "https://www.youtube.com/watch?v=LlvBzyy-558", "estimated_minutes": 120},
                ]
            },
            {
                "title": "Week 9-12: Full Stack Integration",
                "description": "Connect frontend and backend",
                "order": 3,
                "resources": [
                    {"title": "React + FastAPI Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=I0DqdRHepks", "estimated_minutes": 150},
                    {"title": "Authentication & JWT", "type": "video", "url": "https://www.youtube.com/watch?v=6Vq3hNM7Txc", "estimated_minutes": 60},
                ]
            }
        ]
    },
    {
        "title": "DevOps Engineer Path",
        "description": "Master Docker, Kubernetes, CI/CD, and cloud infrastructure",
        "category": "devops",
        "difficulty": "advanced",
        "estimated_weeks": 14,
        "modules": [
            {
                "title": "Week 1-2: Linux & Bash Scripting",
                "description": "Linux fundamentals and shell scripting",
                "order": 0,
                "resources": [
                    {"title": "Linux for DevOps", "type": "video", "url": "https://www.youtube.com/watch?v=J2zquYPJbWY", "estimated_minutes": 180},
                    {"title": "Bash Scripting Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=e7BufAVwDiM", "estimated_minutes": 90},
                ]
            },
            {
                "title": "Week 3-5: Docker & Containers",
                "description": "Containerization with Docker",
                "order": 1,
                "resources": [
                    {"title": "Docker Complete Course", "type": "video", "url": "https://www.youtube.com/watch?v=fqMOX6JJhGo", "estimated_minutes": 240},
                    {"title": "Docker Compose Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=SXwC9fSwct8", "estimated_minutes": 60},
                ]
            },
            {
                "title": "Week 6-8: Kubernetes",
                "description": "Container orchestration with K8s",
                "order": 2,
                "resources": [
                    {"title": "Kubernetes Full Course", "type": "video", "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "estimated_minutes": 240},
                    {"title": "Kubernetes Hands-On", "type": "video", "url": "https://www.youtube.com/watch?v=d6WC5n9G_sM", "estimated_minutes": 120},
                ]
            },
            {
                "title": "Week 9-11: CI/CD Pipelines",
                "description": "Jenkins, GitHub Actions, and automation",
                "order": 3,
                "resources": [
                    {"title": "CI/CD Explained", "type": "video", "url": "https://www.youtube.com/watch?v=scEDHsr3APg", "estimated_minutes": 45},
                    {"title": "GitHub Actions Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=R8_veQiYBjI", "estimated_minutes": 90},
                ]
            },
            {
                "title": "Week 12-14: Infrastructure as Code",
                "description": "Terraform and Ansible",
                "order": 4,
                "resources": [
                    {"title": "Terraform Full Course", "type": "video", "url": "https://www.youtube.com/watch?v=7xngnjfIlK4", "estimated_minutes": 120},
                    {"title": "Ansible for DevOps", "type": "video", "url": "https://www.youtube.com/watch?v=goclfp6a2IQ", "estimated_minutes": 90},
                ]
            }
        ]
    },
    {
        "title": "Machine Learning Engineer",
        "description": "From basics to deployment of ML models",
        "category": "ai-ml",
        "difficulty": "advanced",
        "estimated_weeks": 20,
        "modules": [
            {
                "title": "Week 1-3: Python for Data Science",
                "description": "NumPy, Pandas, Matplotlib",
                "order": 0,
                "resources": [
                    {"title": "Python Data Science Course", "type": "video", "url": "https://www.youtube.com/watch?v=LHBE6Q9XlzI", "estimated_minutes": 180},
                    {"title": "Pandas Complete Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=vmEHCJofslg", "estimated_minutes": 60},
                ]
            },
            {
                "title": "Week 4-7: Machine Learning Algorithms",
                "description": "Supervised and unsupervised learning",
                "order": 1,
                "resources": [
                    {"title": "Machine Learning Full Course", "type": "video", "url": "https://www.youtube.com/watch?v=Gv9_4yMHFhI", "estimated_minutes": 300},
                    {"title": "Scikit-learn Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=pqNCD_5r0IU", "estimated_minutes": 120},
                ]
            },
            {
                "title": "Week 8-12: Deep Learning",
                "description": "Neural networks with TensorFlow/PyTorch",
                "order": 2,
                "resources": [
                    {"title": "Deep Learning Fundamentals", "type": "video", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "estimated_minutes": 240},
                    {"title": "PyTorch Full Course", "type": "video", "url": "https://www.youtube.com/watch?v=V_xro1bcAuA", "estimated_minutes": 300},
                ]
            },
            {
                "title": "Week 13-16: Computer Vision & NLP",
                "description": "Advanced ML applications",
                "order": 3,
                "resources": [
                    {"title": "Computer Vision Course", "type": "video", "url": "https://www.youtube.com/watch?v=01sAkU_NvOY", "estimated_minutes": 180},
                    {"title": "NLP with Transformers", "type": "video", "url": "https://www.youtube.com/watch?v=QEaBAZQCtwE", "estimated_minutes": 120},
                ]
            },
            {
                "title": "Week 17-20: MLOps & Deployment",
                "description": "Deploy and monitor ML models",
                "order": 4,
                "resources": [
                    {"title": "MLOps Fundamentals", "type": "video", "url": "https://www.youtube.com/watch?v=sUzWL8yzsCg", "estimated_minutes": 90},
                    {"title": "Deploy ML Models", "type": "video", "url": "https://www.youtube.com/watch?v=bjsJOl8gz5k", "estimated_minutes": 75},
                ]
            }
        ]
    },
    {
        "title": "Cybersecurity Fundamentals",
        "description": "Learn ethical hacking, network security, and penetration testing",
        "category": "security",
        "difficulty": "intermediate",
        "estimated_weeks": 12,
        "modules": [
            {
                "title": "Week 1-2: Security Basics",
                "description": "Fundamentals of cybersecurity",
                "order": 0,
                "resources": [
                    {"title": "Cybersecurity Full Course", "type": "video", "url": "https://www.youtube.com/watch?v=U_P23SqJaDc", "estimated_minutes": 180},
                    {"title": "Network Security Basics", "type": "video", "url": "https://www.youtube.com/watch?v=qiQR5rTSshw", "estimated_minutes": 90},
                ]
            },
            {
                "title": "Week 3-5: Ethical Hacking",
                "description": "Penetration testing fundamentals",
                "order": 1,
                "resources": [
                    {"title": "Ethical Hacking Course", "type": "video", "url": "https://www.youtube.com/watch?v=3Kq1MIfTWCE", "estimated_minutes": 240},
                    {"title": "Kali Linux Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=lZAoFs75_cs", "estimated_minutes": 120},
                ]
            },
            {
                "title": "Week 6-8: Web Application Security",
                "description": "OWASP Top 10 and web vulnerabilities",
                "order": 2,
                "resources": [
                    {"title": "Web Security Fundamentals", "type": "video", "url": "https://www.youtube.com/watch?v=WlmKwIe9z1Q", "estimated_minutes": 90},
                    {"title": "OWASP Top 10 Explained", "type": "video", "url": "https://www.youtube.com/watch?v=avFR_Af0KGk", "estimated_minutes": 60},
                ]
            },
            {
                "title": "Week 9-12: Security Tools & Practice",
                "description": "Hands-on with security tools",
                "order": 3,
                "resources": [
                    {"title": "Burp Suite Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=h2duGBZLEek", "estimated_minutes": 75},
                    {"title": "Metasploit Framework", "type": "video", "url": "https://www.youtube.com/watch?v=8lR27r8Y_ik", "estimated_minutes": 90},
                ]
            }
        ]
    },
    {
        "title": "Blockchain & Web3 Development",
        "description": "Smart contracts, DApps, and blockchain fundamentals",
        "category": "blockchain",
        "difficulty": "advanced",
        "estimated_weeks": 14,
        "modules": [
            {
                "title": "Week 1-2: Blockchain Basics",
                "description": "Understanding blockchain technology",
                "order": 0,
                "resources": [
                    {"title": "Blockchain Explained", "type": "video", "url": "https://www.youtube.com/watch?v=qOVAbKKSH10", "estimated_minutes": 120},
                    {"title": "Cryptocurrency Fundamentals", "type": "video", "url": "https://www.youtube.com/watch?v=1YyAzVmP9xQ", "estimated_minutes": 60},
                ]
            },
            {
                "title": "Week 3-6: Solidity & Smart Contracts",
                "description": "Learn Solidity programming",
                "order": 1,
                "resources": [
                    {"title": "Solidity Full Course", "type": "video", "url": "https://www.youtube.com/watch?v=gyMwXuJrbJQ", "estimated_minutes": 240},
                    {"title": "Smart Contract Security", "type": "video", "url": "https://www.youtube.com/watch?v=TmZ8gH-toX0", "estimated_minutes": 90},
                ]
            },
            {
                "title": "Week 7-10: DApp Development",
                "description": "Build decentralized applications",
                "order": 2,
                "resources": [
                    {"title": "Web3 JavaScript Tutorial", "type": "video", "url": "https://www.youtube.com/watch?v=t3wM5903ty0", "estimated_minutes": 150},
                    {"title": "Build a Full Stack DApp", "type": "video", "url": "https://www.youtube.com/watch?v=coQ5dg8wM2o", "estimated_minutes": 180},
                ]
            },
            {
                "title": "Week 11-14: Advanced Topics",
                "description": "DeFi, NFTs, and deployment",
                "order": 3,
                "resources": [
                    {"title": "DeFi Explained", "type": "video", "url": "https://www.youtube.com/watch?v=k9HYC0EJU6E", "estimated_minutes": 60},
                    {"title": "NFT Smart Contracts", "type": "video", "url": "https://www.youtube.com/watch?v=YPbgjPPC1d0", "estimated_minutes": 90},
                ]
            }
        ]
    }
]
