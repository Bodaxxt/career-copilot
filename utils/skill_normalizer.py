"""
محرك توحيد وتنقية المهارات التقنية (Skill Normalizer Engine)
يحتوي على قاموس شامل لأكثر من 150 مهارة برمجية وتقنية شائعة مع معالجة المترادفات والصيغ المختلفة.
"""

import re
from typing import Dict, List, Optional, Set


class SkillNormalizer:
    """
    محرك توحيد المهارات التقنية بالاعتماد على مطابقة المترادفات والـ Normalization الذكي.
    """

    # قاموس المترادفات والتنسيقات القياسية (150+ مهارة وتقنية معتمدة)
    CANONICAL_SKILLS_MAP: Dict[str, str] = {
        # ================= Languages =================
        "python": "Python",
        "python3": "Python",
        "python2": "Python",
        "py": "Python",
        "javascript": "JavaScript",
        "js": "JavaScript",
        "ecmascript": "JavaScript",
        "es6": "JavaScript",
        "es6+": "JavaScript",
        "typescript": "TypeScript",
        "ts": "TypeScript",
        "golang": "Go",
        "go": "Go",
        "c++": "C++",
        "cpp": "C++",
        "c/c++": "C++",
        "c#": "C#",
        "csharp": "C#",
        "c sharp": "C#",
        "java": "Java",
        "java8": "Java",
        "java11": "Java",
        "java17": "Java",
        "ruby": "Ruby",
        "php": "PHP",
        "php7": "PHP",
        "php8": "PHP",
        "rust": "Rust",
        "rustlang": "Rust",
        "swift": "Swift",
        "kotlin": "Kotlin",
        "dart": "Dart",
        "scala": "Scala",
        "r": "R",
        "rlang": "R",
        "julia": "Julia",
        "sql": "SQL",
        "pl/sql": "PL/SQL",
        "t-sql": "T-SQL",
        "tsql": "T-SQL",
        "bash": "Bash",
        "shell": "Shell Scripting",
        "powershell": "PowerShell",
        "c": "C",

        # ================= Frontend Frameworks & Web =================
        "react": "React",
        "react.js": "React",
        "reactjs": "React",
        "react native": "React Native",
        "react-native": "React Native",
        "next.js": "Next.js",
        "nextjs": "Next.js",
        "next": "Next.js",
        "vue": "Vue.js",
        "vue.js": "Vue.js",
        "vuejs": "Vue.js",
        "vue3": "Vue.js",
        "nuxt": "Nuxt.js",
        "nuxtjs": "Nuxt.js",
        "nuxt.js": "Nuxt.js",
        "angular": "Angular",
        "angular.js": "Angular",
        "angularjs": "Angular",
        "angular2+": "Angular",
        "svelte": "Svelte",
        "sveltekit": "SvelteKit",
        "tailwind": "Tailwind CSS",
        "tailwindcss": "Tailwind CSS",
        "tailwind css": "Tailwind CSS",
        "bootstrap": "Bootstrap",
        "bootstrap5": "Bootstrap",
        "html": "HTML5",
        "html5": "HTML5",
        "css": "CSS3",
        "css3": "CSS3",
        "sass": "Sass",
        "scss": "Sass",
        "less": "Less",
        "redux": "Redux",
        "redux toolkit": "Redux Toolkit",
        "rtk": "Redux Toolkit",
        "zustand": "Zustand",
        "mobx": "MobX",
        "jquery": "jQuery",
        "webpack": "Webpack",
        "vite": "Vite",

        # ================= Backend & APIs =================
        "fastapi": "FastAPI",
        "fast api": "FastAPI",
        "django": "Django",
        "django rest framework": "Django REST Framework",
        "drf": "Django REST Framework",
        "flask": "Flask",
        "express": "Express.js",
        "express.js": "Express.js",
        "expressjs": "Express.js",
        "nestjs": "NestJS",
        "nest.js": "NestJS",
        "nest": "NestJS",
        "node": "Node.js",
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "spring": "Spring Boot",
        "springboot": "Spring Boot",
        "spring boot": "Spring Boot",
        "spring framework": "Spring Boot",
        ".net": ".NET",
        ".net core": ".NET Core",
        "asp.net": "ASP.NET",
        "asp.net core": "ASP.NET Core",
        "dotnet": ".NET",
        "laravel": "Laravel",
        "ruby on rails": "Ruby on Rails",
        "rails": "Ruby on Rails",
        "gin": "Gin",
        "fiber": "Fiber",
        "graphql": "GraphQL",
        "rest": "REST API",
        "rest api": "REST API",
        "restful api": "REST API",
        "restful apis": "REST API",
        "grpc": "gRPC",
        "websockets": "WebSockets",
        "websocket": "WebSockets",
        "celery": "Celery",
        "kafka": "Apache Kafka",
        "apache kafka": "Apache Kafka",
        "rabbitmq": "RabbitMQ",

        # ================= Databases & Storage =================
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "psql": "PostgreSQL",
        "mysql": "MySQL",
        "mongodb": "MongoDB",
        "mongo": "MongoDB",
        "redis": "Redis",
        "elasticsearch": "Elasticsearch",
        "elastic search": "Elasticsearch",
        "sqlite": "SQLite",
        "sqlite3": "SQLite",
        "mariadb": "MariaDB",
        "cassandra": "Apache Cassandra",
        "dynamodb": "DynamoDB",
        "amazon dynamodb": "DynamoDB",
        "oracle": "Oracle Database",
        "oracle db": "Oracle Database",
        "ms sql": "Microsoft SQL Server",
        "sql server": "Microsoft SQL Server",
        "mssql": "Microsoft SQL Server",
        "couchdb": "CouchDB",
        "neo4j": "Neo4j",
        "supabase": "Supabase",
        "firebase": "Firebase",
        "firestore": "Firestore",
        "snowflake": "Snowflake",
        "bigquery": "BigQuery",
        "google bigquery": "BigQuery",
        "chroma": "ChromaDB",
        "chromadb": "ChromaDB",
        "pinecone": "Pinecone",
        "qdrant": "Qdrant",
        "weaviate": "Weaviate",
        "milvus": "Milvus",

        # ================= DevOps, Cloud & Infra =================
        "docker": "Docker",
        "docker compose": "Docker Compose",
        "docker-compose": "Docker Compose",
        "kubernetes": "Kubernetes",
        "k8s": "Kubernetes",
        "aws": "AWS",
        "amazon web services": "AWS",
        "gcp": "Google Cloud",
        "google cloud": "Google Cloud",
        "google cloud platform": "Google Cloud",
        "azure": "Microsoft Azure",
        "ms azure": "Microsoft Azure",
        "microsoft azure": "Microsoft Azure",
        "terraform": "Terraform",
        "ansible": "Ansible",
        "ci/cd": "CI/CD",
        "cicd": "CI/CD",
        "continuous integration": "CI/CD",
        "github actions": "GitHub Actions",
        "gh actions": "GitHub Actions",
        "gitlab ci": "GitLab CI",
        "gitlab-ci": "GitLab CI",
        "jenkins": "Jenkins",
        "linux": "Linux",
        "ubuntu": "Ubuntu",
        "nginx": "Nginx",
        "apache": "Apache HTTP Server",
        "helm": "Helm",
        "prometheus": "Prometheus",
        "grafana": "Grafana",
        "datadog": "Datadog",

        # ================= AI, Machine Learning & Data =================
        "pytorch": "PyTorch",
        "torch": "PyTorch",
        "tensorflow": "TensorFlow",
        "tf": "TensorFlow",
        "keras": "Keras",
        "scikit-learn": "Scikit-Learn",
        "sklearn": "Scikit-Learn",
        "scikit learn": "Scikit-Learn",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "scipy": "SciPy",
        "matplotlib": "Matplotlib",
        "seaborn": "Seaborn",
        "langchain": "LangChain",
        "llamaindex": "LlamaIndex",
        "llama-index": "LlamaIndex",
        "huggingface": "Hugging Face",
        "hugging face": "Hugging Face",
        "transformers": "Transformers",
        "rag": "RAG",
        "retrieval-augmented generation": "RAG",
        "nlp": "NLP",
        "natural language processing": "NLP",
        "llm": "LLMs",
        "llms": "LLMs",
        "large language models": "LLMs",
        "computer vision": "Computer Vision",
        "cv": "Computer Vision",
        "opencv": "OpenCV",
        "spark": "Apache Spark",
        "apache spark": "Apache Spark",
        "pyspark": "PySpark",
        "airflow": "Apache Airflow",
        "apache airflow": "Apache Airflow",
        "dbt": "dbt",
        "tableau": "Tableau",
        "power bi": "Power BI",
        "powerbi": "Power BI",
        "xgboost": "XGBoost",
        "lightgbm": "LightGBM",
        "gemini api": "Gemini API",
        "openai api": "OpenAI API",

        # ================= Methodologies & Tools =================
        "git": "Git",
        "github": "GitHub",
        "gitlab": "GitLab",
        "bitbucket": "Bitbucket",
        "jira": "Jira",
        "confluence": "Confluence",
        "postman": "Postman",
        "swagger": "Swagger",
        "openapi": "OpenAPI",
        "agile": "Agile",
        "scrum": "Scrum",
        "kanban": "Kanban",
        "microservices": "Microservices",
        "system design": "System Design",
        "oop": "OOP",
        "object-oriented programming": "OOP",
        "tdd": "TDD",
        "test driven development": "TDD",
        "unit testing": "Unit Testing",
        "pytest": "Pytest",
        "jest": "Jest",
        "cypress": "Cypress",
        "playwright": "Playwright",
        "selenium": "Selenium",
    }

    @classmethod
    def clean_raw_string(cls, raw: str) -> str:
        """تنظيف السلسلة النصية من الرموز الزائدة والفواصل والمسافات."""
        if not raw:
            return ""
        # إزالة الفواصل والنقاط الزائدة من الأطراف
        cleaned = raw.strip().strip(".,;:|•-–_")
        # استبدال المسافات والشرطات السفلية المتعددة
        cleaned = re.sub(r"[\s_]+", " ", cleaned)
        return cleaned.strip()

    @classmethod
    def normalize_single_skill(cls, skill: str) -> Optional[str]:
        """
        توحيد مهارة واحدة:
        1. تنظيف النص.
        2. مطابقة الـ Case-insensitive مع القاموس المعتمد.
        3. إن لم توجد في القاموس: تنسيقها بنمط Title Case أنيق.
        """
        cleaned = cls.clean_raw_string(skill)
        if not cleaned:
            return None

        lookup_key = cleaned.lower()

        # 1. مطابقة مباشرة في القاموس
        if lookup_key in cls.CANONICAL_SKILLS_MAP:
            return cls.CANONICAL_SKILLS_MAP[lookup_key]

        # 2. إزالة فواصل إضافية وتجربة المطابقة (مثل "react-js" -> "react js")
        alt_key = re.sub(r"[-_.]+", " ", lookup_key).strip()
        if alt_key in cls.CANONICAL_SKILLS_MAP:
            return cls.CANONICAL_SKILLS_MAP[alt_key]

        alt_key_no_space = re.sub(r"[-_.\s]+", "", lookup_key)
        if alt_key_no_space in cls.CANONICAL_SKILLS_MAP:
            return cls.CANONICAL_SKILLS_MAP[alt_key_no_space]

        # 3. Fallback ذكي: الحفاظ على الحروف الكبيرة للكلمات الإنجليزية (Title Case)
        # إذا كانت عربية أو مختلطة تظل كما هي، وإذا كانت إنجليزية تصبح Title Case
        if cleaned.isascii():
            # معالجة الكلمات الفردية لتنسيق Title Case
            words = cleaned.split(" ")
            formatted_words = [w.capitalize() if not w.isupper() else w for w in words]
            return " ".join(formatted_words)

        return cleaned

    @classmethod
    def normalize_skills_list(cls, skills: List[str]) -> List[str]:
        """
        توحيد مصفوفة مهارات مع إزالة التكرارات والحفاظ على ترتيب الإدخال.
        """
        if not skills:
            return []

        normalized_list: List[str] = []
        seen: Set[str] = set()

        for s in skills:
            if not isinstance(s, str):
                continue
            norm = cls.normalize_single_skill(s)
            if norm:
                lower_norm = norm.lower()
                if lower_norm not in seen:
                    seen.add(lower_norm)
                    normalized_list.append(norm)

        return normalized_list


def normalize_skills(skills_list: List[str]) -> List[str]:
    """
    دالة مستقلة وسريعة لتوحيد قائمة المهارات.
    
    مثال:
        normalize_skills(["python3", "reactjs", "K8s", "DOCKER", "FASTAPI", "custom_skill"])
        -> ["Python", "React", "Kubernetes", "Docker", "FastAPI", "Custom Skill"]
    """
    return SkillNormalizer.normalize_skills_list(skills_list)
