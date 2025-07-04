
# Dummy skill database per role
JOB_ROLE_SKILLS = {
    "data scientist": ["python", "pandas", "numpy", "sql", "machine learning", "statistics", "matplotlib", "data visualization", "feature engineering"],
    "machine learning engineer": ["python", "tensorflow", "pytorch", "scikit-learn", "deep learning", "data preprocessing", "model deployment", "mlops"],
    "ai researcher": ["python", "deep learning", "neural networks", "tensorflow", "pytorch", "nlp", "computer vision", "reinforcement learning"],
    "data analyst": ["excel", "sql", "python", "pandas", "power bi", "tableau", "data cleaning", "statistical analysis"],
    
    "cloud engineer": ["aws", "azure", "gcp", "terraform", "docker", "kubernetes", "ci/cd", "cloud architecture", "serverless"],
    "devops engineer": ["linux", "aws", "docker", "kubernetes", "jenkins", "ansible", "terraform", "monitoring", "ci/cd pipelines"],
    "cloud architect": ["aws", "azure", "gcp", "cloud security", "architecture design", "terraform", "serverless", "microservices"],
    
    "nlp engineer": ["python", "nlp", "spacy", "nltk", "transformers", "bert", "gpt", "text mining", "deep learning"],
    "computer vision engineer": ["python", "opencv", "tensorflow", "pytorch", "image processing", "cnn", "object detection", "deep learning"],
    
    "big data engineer": ["hadoop", "spark", "kafka", "python", "scala", "java", "aws", "data pipelines", "etl"],
    "ai engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "mlops", "model optimization", "cloud ai services"],
    
    "robotics engineer": ["c++", "python", "ros", "control systems", "embedded systems", "simulation"],
    "quantitative analyst": ["python", "r", "statistics", "mathematics", "machine learning", "financial modeling", "data analysis"],
    
    "cloud security engineer": ["aws", "azure", "gcp", "network security", "identity management", "compliance", "cloud security tools"],
    "mlops engineer": ["docker", "kubernetes", "tensorflow", "pytorch", "ci/cd", "model monitoring", "automation", "cloud"],
    
    "software engineer": ["python", "java", "c++", "data structures", "algorithms", "rest api", "git"],
    "frontend developer": ["html", "css", "javascript", "react", "responsive design", "redux"],
    "backend developer": ["python", "django", "rest api", "postgresql", "docker", "celery"],
    "full stack developer": ["html", "css", "javascript", "react", "node.js", "express", "mongodb", "python", "django"],
    
    "android developer": ["java", "kotlin", "android sdk", "firebase", "jetpack"],
    "ios developer": ["swift", "objective-c", "xcode", "cocoapods", "ui design"],
    
    "qa engineer": ["automation testing", "selenium", "pytest", "performance testing", "bug tracking"],
    "product manager": ["agile", "scrum", "roadmap planning", "stakeholder management", "user research"],
    
    "data engineer": ["python", "sql", "hadoop", "spark", "airflow", "etl", "data warehousing"],
    "security analyst": ["network security", "penetration testing", "incident response", "firewalls", "compliance"],
    
    "business analyst": ["requirement gathering", "process modeling", "sql", "communication", "stakeholder management"],
    "systems administrator": ["linux", "windows server", "networking", "virtualization", "backup strategies"],
    
    "game developer": ["c++", "unity", "unreal engine", "graphics programming", "physics engines"],
    "blockchain developer": ["solidity", "ethereum", "smart contracts", "cryptography", "web3.js"],
    
    "iot engineer": ["embedded systems", "c", "python", "mqtt", "sensor networks", "edge computing"],
    "database administrator": ["mysql", "postgresql", "performance tuning", "backup recovery", "security"],
    
    "technical writer": ["documentation", "api writing", "markdown", "communication", "editing"],
}


def get_skills_for_role(role):
    return JOB_ROLE_SKILLS.get(role.lower())


def analyze_skill_gap(current_skills, required_skills):
    current_set = set(skill.lower().strip() for skill in current_skills)
    required_set = set(skill.lower().strip() for skill in required_skills)
    return list(required_set - current_set)
