"""Seed script to create sample projects and data"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.core.database import AsyncSessionLocal, init_db
from app.models.project import Project, ProjectType, ProjectStatus
from app.models.module import Module, ModuleStatus
from app.models.kpi import KPI


async def seed_data():
    """Create sample data"""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # Create modules
        modules_data = [
            ("IoT Telemetry", "Real-time sensor data", "monitoring"),
            ("MRV Protocol", "Carbon verification", "monitoring"),
            ("Soil & Water", "FAO-56 irrigation", "agriculture"),
            ("Satellite Monitoring", "Earth observation", "monitoring"),
            ("Agriculture Command", "Precision farming", "agriculture"),
        ]
        
        modules = []
        for name, desc, mtype in modules_data:
            from sqlalchemy import select
            result = await db.execute(select(Module).where(Module.name == name))
            existing = result.scalar_one_or_none()
            if existing:
                modules.append(existing)
            else:
                module = Module(
                    name=name,
                    description=desc,
                    type=mtype,
                    status=ModuleStatus.LIVE,
                    version="1.0.0",
                )
                db.add(module)
                modules.append(module)
        
        await db.commit()
        for m in modules:
            await db.refresh(m)
        
        print(f"Created {len(modules)} modules")
        
        # Create projects
        projects_data = [
            (
                "Isfahan Watershed Revival",
                "Restoring ancient qanat systems in Isfahan province",
                "Iran", "Isfahan",
                ProjectType.WATER, 2400, 450000,
            ),
            (
                "Zagros Oak Rebirth",
                "Replanting 50,000 native oak seedlings",
                "Iran", "Kohgiluyeh",
                ProjectType.FOREST, 5000, 820000,
            ),
            (
                "Amazon Canopy Guardian",
                "Protecting primary rainforest",
                "Brazil", "Para",
                ProjectType.FOREST, 10000, 1500000,
            ),
            (
                "Mangrove Coast Restoration",
                "Rehabilitating coastal mangroves",
                "Singapore", "Southern Islands",
                ProjectType.MIXED, 800, 320000,
            ),
            (
                "Thar Desert Greening",
                "Combating desertification in Rajasthan",
                "India", "Rajasthan",
                ProjectType.SOIL, 3000, 420000,
            ),
        ]
        
        projects = []
        for name, desc, country, region, ptype, hectares, budget in projects_data:
            from sqlalchemy import select
            result = await db.execute(select(Project).where(Project.name == name))
            existing = result.scalar_one_or_none()
            if existing:
                projects.append(existing)
            else:
                project = Project(
                    name=name,
                    description=desc,
                    country=country,
                    region=region,
                    type=ptype,
                    status=ProjectStatus.ACTIVE,
                    hectares=hectares,
                    budget=budget,
                    spent=budget * 0.6,
                    progress=60,
                    manager_id=1,
                )
                db.add(project)
                projects.append(project)
        
        await db.commit()
        for p in projects:
            await db.refresh(p)
        
        print(f"Created {len(projects)} projects")
        
        # Create KPIs
        kpis_data = [
            (projects[0], "Water Restored", 2400000, 5000000, "liters", "water"),
            (projects[0], "Qanats Revived", 12, 20, "count", "infrastructure"),
            (projects[1], "Trees Planted", 50000, 50000, "count", "reforestation"),
            (projects[1], "Carbon Sequestered", 1200, 2000, "tCO2e", "carbon"),
            (projects[2], "Forest Protected", 10000, 10000, "hectares", "conservation"),
            (projects[3], "Mangroves Restored", 800, 800, "hectares", "coastal"),
            (projects[4], "Soil Recovered", 3000, 3000, "hectares", "soil"),
        ]
        
        kpis = []
        for project, name, value, target, unit, category in kpis_data:
            kpi = KPI(
                name=name,
                description=f"KPI for {project.name}",
                value=value,
                target=target,
                unit=unit,
                category=category,
                project_id=project.id,
            )
            db.add(kpi)
            kpis.append(kpi)
        
        await db.commit()
        
        print(f"Created {len(kpis)} KPIs")
        print("\nSUCCESS: Sample data created!")
        print(f"   Modules: {len(modules)}")
        print(f"   Projects: {len(projects)}")
        print(f"   KPIs: {len(kpis)}")


if __name__ == "__main__":
    asyncio.run(seed_data())
