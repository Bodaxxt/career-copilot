"""
اختبارات وحدة للتحقق من Pydantic v2 Models و SkillNormalizer
"""

import unittest
from utils.models import UserProfile, Experience, Education, Project
from utils.skill_normalizer import SkillNormalizer, normalize_skills


class TestSkillNormalizer(unittest.TestCase):

    def test_acceptance_criteria_skills(self):
        """التحقق من معيار القبول الإلزامي في المواصفات:"""
        input_skills = ["python3", "reactjs", "K8s", "DOCKER", "FASTAPI", "custom_skill"]
        expected = ["Python", "React", "Kubernetes", "Docker", "FastAPI", "Custom Skill"]
        
        result = normalize_skills(input_skills)
        self.assertEqual(result, expected)

    def test_deduplication_and_order(self):
        """التحقق من إزالة التكرارات الناتجة عن صيغ مختلفة لنفس المهارة مع الحفاظ على الترتيب:"""
        input_skills = ["python", "Python3", "PY", "React.js", "reactjs", "REACT", "docker", "DOCKER"]
        expected = ["Python", "React", "Docker"]
        
        result = normalize_skills(input_skills)
        self.assertEqual(result, expected)

    def test_programming_languages(self):
        """توحيد لغات البرمجة المختلفة:"""
        input_skills = ["js", "ts", "golang", "csharp", "c++", "cpp", "ruby", "rustlang"]
        expected = ["JavaScript", "TypeScript", "Go", "C#", "C++", "Ruby", "Rust"]
        
        result = normalize_skills(input_skills)
        self.assertEqual(result, expected)

    def test_databases_and_cloud(self):
        """توحيد قواعد البيانات والحوسبة السحابية:"""
        input_skills = ["postgres", "psql", "mongo", "k8s", "amazon web services", "gcp", "azure"]
        expected = ["PostgreSQL", "MongoDB", "Kubernetes", "AWS", "Google Cloud", "Microsoft Azure"]
        
        result = normalize_skills(input_skills)
        self.assertEqual(result, expected)

    def test_ai_ml_data_science(self):
        """توحيد أدوات الذكاء الاصطناعي ومعالجة البيانات:"""
        input_skills = ["pytorch", "tf", "scikit-learn", "sklearn", "langchain", "llamaindex", "huggingface", "rag", "llm"]
        expected = ["PyTorch", "TensorFlow", "Scikit-Learn", "LangChain", "LlamaIndex", "Hugging Face", "RAG", "LLMs"]
        
        result = normalize_skills(input_skills)
        self.assertEqual(result, expected)

    def test_custom_and_fallback_skills(self):
        """التحقق من معالجة المهارات غير الموجودة في القاموس وتنسيقها Title Case:"""
        input_skills = ["my_custom_tool", "distributed systems", "مهارة مخصصة"]
        expected = ["My Custom Tool", "Distributed Systems", "مهارة مخصصة"]
        
        result = normalize_skills(input_skills)
        self.assertEqual(result, expected)


class TestUserProfileModel(unittest.TestCase):

    def test_user_profile_creation_and_serialization(self):
        """التحقق من صحة كائن UserProfile في Pydantic v2:"""
        data = {
            "full_name": "أحمد محمود",
            "headline": "Lead Backend Developer",
            "summary": "خبرة 6 سنوات في الأنظمة الموزعة",
            "skills": ["python3", "fastapi", "k8s"],
            "experiences": [
                {
                    "company": "شركة المستقبل",
                    "title": "Senior Engineer",
                    "period": "2021 - current",
                    "achievements": ["بناء microservices"]
                }
            ],
            "education": [
                {
                    "university": "جامعة القاهرة",
                    "degree": "بكالوريوس",
                    "field": "علوم الحاسب",
                    "year": "2018"
                }
            ],
            "projects": [
                {
                    "name": "منظومة دفع",
                    "technologies": ["fastapi", "postgres"],
                    "description": "بوابة دفع إلكترونية"
                }
            ]
        }

        # إنشاء الكائن
        profile = UserProfile.from_dict(data)
        
        self.assertEqual(profile.full_name, "أحمد محمود")
        self.assertEqual(len(profile.experiences), 1)
        self.assertEqual(profile.experiences[0].company, "شركة المستقبل")
        self.assertEqual(profile.get("headline"), "Lead Backend Developer")
        self.assertEqual(profile["headline"], "Lead Backend Developer")

        # التحويل لـ Dict و JSON
        profile_dict = profile.to_dict()
        self.assertIsInstance(profile_dict, dict)
        self.assertEqual(profile_dict["full_name"], "أحمد محمود")

        profile_json = profile.to_json()
        self.assertIn("أحمد محمود", profile_json)


if __name__ == "__main__":
    unittest.main()
