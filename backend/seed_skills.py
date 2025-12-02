"""Script to seed basic skills into the database."""

import asyncio
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.repositories.skill_repository import SkillRepository
from app.services.skill_service import SkillService
from app.schemas.skill import SkillCreate


async def seed_skills():
    """Seed basic skills into the database."""
    db: Session = SessionLocal()

    try:
        skill_repository = SkillRepository(db)
        skill_service = SkillService(skill_repository)

        # Define basic skills by category
        skills_data = [
            # Programming Languages
            {"name": "Python", "category": "Programming Language"},
            {"name": "JavaScript", "category": "Programming Language"},
            {"name": "TypeScript", "category": "Programming Language"},
            {"name": "Java", "category": "Programming Language"},
            {"name": "C#", "category": "Programming Language"},
            {"name": "Go", "category": "Programming Language"},
            {"name": "Rust", "category": "Programming Language"},
            {"name": "PHP", "category": "Programming Language"},
            {"name": "Ruby", "category": "Programming Language"},
            {"name": "Swift", "category": "Programming Language"},
            {"name": "Kotlin", "category": "Programming Language"},

            # Frontend Frameworks & Libraries
            {"name": "React", "category": "Frontend"},
            {"name": "Vue.js", "category": "Frontend"},
            {"name": "Angular", "category": "Frontend"},
            {"name": "Next.js", "category": "Frontend"},
            {"name": "Svelte", "category": "Frontend"},
            {"name": "Tailwind CSS", "category": "Frontend"},
            {"name": "Bootstrap", "category": "Frontend"},
            {"name": "Material-UI", "category": "Frontend"},

            # Backend Frameworks
            {"name": "Node.js", "category": "Backend"},
            {"name": "Express.js", "category": "Backend"},
            {"name": "FastAPI", "category": "Backend"},
            {"name": "Django", "category": "Backend"},
            {"name": "Flask", "category": "Backend"},
            {"name": "Spring Boot", "category": "Backend"},
            {"name": "ASP.NET Core", "category": "Backend"},
            {"name": "Ruby on Rails", "category": "Backend"},
            {"name": "Laravel", "category": "Backend"},

            # Databases
            {"name": "PostgreSQL", "category": "Database"},
            {"name": "MySQL", "category": "Database"},
            {"name": "MongoDB", "category": "Database"},
            {"name": "Redis", "category": "Database"},
            {"name": "SQLite", "category": "Database"},
            {"name": "Oracle", "category": "Database"},
            {"name": "Cassandra", "category": "Database"},
            {"name": "Elasticsearch", "category": "Database"},

            # DevOps & Cloud
            {"name": "Docker", "category": "DevOps"},
            {"name": "Kubernetes", "category": "DevOps"},
            {"name": "AWS", "category": "Cloud"},
            {"name": "Azure", "category": "Cloud"},
            {"name": "Google Cloud", "category": "Cloud"},
            {"name": "CI/CD", "category": "DevOps"},
            {"name": "Jenkins", "category": "DevOps"},
            {"name": "GitHub Actions", "category": "DevOps"},
            {"name": "Terraform", "category": "DevOps"},

            # Tools & Platforms
            {"name": "Git", "category": "Tools"},
            {"name": "Linux", "category": "Tools"},
            {"name": "Nginx", "category": "Tools"},
            {"name": "Apache", "category": "Tools"},
            {"name": "Postman", "category": "Tools"},

            # Mobile Development
            {"name": "React Native", "category": "Mobile"},
            {"name": "Flutter", "category": "Mobile"},
            {"name": "iOS Development", "category": "Mobile"},
            {"name": "Android Development", "category": "Mobile"},

            # Data Science & AI
            {"name": "Machine Learning", "category": "AI/ML"},
            {"name": "Deep Learning", "category": "AI/ML"},
            {"name": "TensorFlow", "category": "AI/ML"},
            {"name": "PyTorch", "category": "AI/ML"},
            {"name": "Data Analysis", "category": "Data Science"},
            {"name": "Pandas", "category": "Data Science"},
            {"name": "NumPy", "category": "Data Science"},

            # Soft Skills
            {"name": "Project Management", "category": "Soft Skills"},
            {"name": "Agile/Scrum", "category": "Soft Skills"},
            {"name": "Leadership", "category": "Soft Skills"},
            {"name": "Communication", "category": "Soft Skills"},
            {"name": "Problem Solving", "category": "Soft Skills"},
        ]

        created_count = 0
        skipped_count = 0

        for skill_data in skills_data:
            try:
                skill_create = SkillCreate(**skill_data)
                await skill_service.create_skill(skill_create)
                created_count += 1
                print(f"✓ Created: {skill_data['name']} ({skill_data['category']})")
            except ValueError as e:
                # Skill already exists
                skipped_count += 1
                print(f"⊘ Skipped: {skill_data['name']} (already exists)")
            except Exception as e:
                print(f"✗ Error creating {skill_data['name']}: {str(e)}")

        print(f"\n✓ Seeding completed!")
        print(f"  - Created: {created_count} skills")
        print(f"  - Skipped: {skipped_count} skills")

    except Exception as e:
        print(f"✗ Error during seeding: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting skills seeding...")
    asyncio.run(seed_skills())
