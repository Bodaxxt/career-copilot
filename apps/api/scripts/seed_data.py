"""
Seed script to populate development database with initial data.
إضافة بيانات أولية (جامعات، مهارات، بنك أسئلة، منصات وظائف).
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure apps/api is in sys.path
api_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

load_dotenv(os.path.join(api_dir, ".env"))
load_dotenv(os.path.join(api_dir, ".env.development"))

from app.database import AsyncSessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    University,
    SkillTaxonomy,
    SkillAlias,
    JobBoardSource,
    InterviewQuestion,
    User,
)

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


async def seed():
    print("[INFO] Starting database seed...")

    async with AsyncSessionLocal() as session:
        # 1. Universities
        cu = University(
            name="Cairo University",
            domain="cu.edu.eg",
            country="Egypt",
            is_verified=True,
        )
        asu = University(
            name="Ain Shams University",
            domain="asu.edu.eg",
            country="Egypt",
            is_verified=True,
        )
        auc = University(
            name="American University in Cairo",
            domain="aucegypt.edu",
            country="Egypt",
            is_verified=True,
        )
        session.add_all([cu, asu, auc])
        await session.flush()
        print("[OK] Added 3 Universities")

        # 2. Skill Taxonomy & Aliases
        skills_data = [
            ("Python", "Backend", ["py", "python3"]),
            ("FastAPI", "Backend", ["fast-api"]),
            ("PostgreSQL", "Database", ["postgres", "pgsql"]),
            ("React", "Frontend", ["reactjs", "react.js"]),
            ("Next.js", "Frontend", ["nextjs"]),
            ("Docker", "DevOps", ["docker-container"]),
            ("TypeScript", "Frontend", ["ts"]),
            ("Machine Learning", "AI/ML", ["ml", "deep-learning"]),
        ]

        for name, category, aliases in skills_data:
            skill = SkillTaxonomy(name=name, category=category)
            session.add(skill)
            await session.flush()
            for alias_name in aliases:
                alias = SkillAlias(skill_id=skill.id, alias_name=alias_name)
                session.add(alias)
        print("[OK] Added Skill Taxonomy & Aliases")

        # 3. Job Board Sources
        sources = [
            JobBoardSource(name="LinkedIn", base_url="https://www.linkedin.com/jobs"),
            JobBoardSource(name="Wuzzuf", base_url="https://wuzzuf.net/jobs"),
            JobBoardSource(name="Indeed", base_url="https://indeed.com"),
        ]
        session.add_all(sources)
        print("[OK] Added Job Board Sources")

        # 4. Interview Questions Bank
        questions = [
            InterviewQuestion(
                category="Python",
                difficulty="medium",
                question_text=(
                    "Explain the difference between mutable and immutable"
                    " types in Python, and provide examples."
                ),
                expected_answer=(
                    "Mutable types (lists, dicts, sets) can be modified in place."
                    " Immutable types (int, float, str, tuple) cannot be changed."
                ),
            ),
            InterviewQuestion(
                category="PostgreSQL",
                difficulty="medium",
                question_text=(
                    "How does an index work in PostgreSQL and when should you"
                    " use a composite index vs single-column index?"
                ),
                expected_answer=(
                    "PostgreSQL uses B-tree indexes by default. Composite indexes"
                    " are useful when queries filter or sort on multiple columns."
                ),
            ),
            InterviewQuestion(
                category="Behavioral",
                difficulty="easy",
                question_text=(
                    "Tell me about a time you faced a difficult technical"
                    " challenge and how you solved it."
                ),
                expected_answer="Use the STAR method: Situation, Task, Action, and Result.",
            ),
        ]
        session.add_all(questions)
        print("[OK] Added Interview Questions")

        # 5. Demo Admin / Student User
        demo_user = User(
            clerk_id="user_demo_career_copilot_123",
            email="demo@student.cu.edu.eg",
            name="Ahmed Demo",
            role="student",
            university_id=cu.id,
            profile_completed=True,
        )
        session.add(demo_user)

        await session.commit()
        print("[SUCCESS] Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
