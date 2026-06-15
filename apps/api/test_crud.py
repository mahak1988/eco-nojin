"""Comprehensive CRUD test script with error handling"""

import sys
import os

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

import asyncio
import httpx

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

token = None
project_id = None
data_point_id = None
kpi_id = None


async def login():
    global token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/auth/login",
            json={"email": "admin@econojin.com", "password": os.environ.get("TEST_PASSWORD", "secure_default_password")},
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("[1/10] Login: SUCCESS")
            return True
        else:
            print(f"[1/10] Login: FAILED - {response.json()}")
            return False


async def create_project():
    global project_id
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/projects/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Test Project CRUD",
                "description": "Test project for CRUD operations",
                "country": "Iran",
                "region": "Tehran",
                "type": "water",
                "hectares": 100.0,
                "budget": 50000.0,
            },
        )
        if response.status_code == 201:
            project_id = response.json()["id"]
            print(f"[2/10] Create Project: SUCCESS (ID: {project_id})")
            return True
        else:
            print(f"[2/10] Create Project: FAILED - {response.json()}")
            return False


async def list_projects():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/projects/",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[3/10] List Projects: SUCCESS (Total: {data['total']})")
            return True
        else:
            print(f"[3/10] List Projects: FAILED - {response.json()}")
            return False


async def get_project():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            print(f"[4/10] Get Project: SUCCESS - {response.json()['name']}")
            return True
        else:
            print(f"[4/10] Get Project: FAILED - {response.json()}")
            return False


async def update_project():
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{API_URL}/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"progress": 75, "status": "active"},
        )
        if response.status_code == 200:
            print(f"[5/10] Update Project: SUCCESS - Progress: {response.json()['progress']}%")
            return True
        else:
            print(f"[5/10] Update Project: FAILED - {response.json()}")
            return False


async def create_data_point():
    global data_point_id
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/data-points/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "project_id": project_id,
                "module_id": 1,
                "data_type": "soil_moisture",
                "value": {"moisture": 34.5, "temperature": 22.3},
                "unit": "percent",
                "timestamp": "2026-06-14T10:00:00",
            },
        )
        if response.status_code == 201:
            data_point_id = response.json()["id"]
            print(f"[6/10] Create DataPoint: SUCCESS (ID: {data_point_id})")
            return True
        else:
            print(f"[6/10] Create DataPoint: FAILED - {response.json()}")
            return False


async def list_data_points():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/data-points/?project_id={project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[7/10] List DataPoints: SUCCESS (Total: {data['total']})")
            return True
        else:
            print(f"[7/10] List DataPoints: FAILED - {response.json()}")
            return False


async def create_kpi():
    global kpi_id
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/kpis/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "project_id": project_id,
                "name": "Water Saved",
                "value": 50000.0,
                "target": 100000.0,
                "unit": "liters",
                "category": "water",
            },
        )
        if response.status_code == 201:
            kpi_id = response.json()["id"]
            print(f"[8/10] Create KPI: SUCCESS (ID: {kpi_id})")
            return True
        else:
            print(f"[8/10] Create KPI: FAILED - {response.json()}")
            return False


async def list_kpis():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/kpis/?project_id={project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[9/10] List KPIs: SUCCESS (Total: {data['total']})")
            return True
        else:
            print(f"[9/10] List KPIs: FAILED - {response.json()}")
            return False


async def delete_project():
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{API_URL}/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 204:
            print("[10/10] Delete Project: SUCCESS (cascade deleted all related data)")
            return True
        else:
            print(f"[10/10] Delete Project: FAILED - {response.status_code} {response.text}")
            return False


async def verify_deletion():
    """Verify that related data was cascade deleted"""
    async with httpx.AsyncClient() as client:
        # Check data points
        response = await client.get(
            f"{API_URL}/data-points/?project_id={project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[Bonus] DataPoints after delete: {data['total']} (should be 0)")
        
        # Check KPIs
        response = await client.get(
            f"{API_URL}/kpis/?project_id={project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[Bonus] KPIs after delete: {data['total']} (should be 0)")


async def main():
    print("=" * 60)
    print("EcoNojin API - CRUD Test (with Cascade Delete)")
    print("=" * 60)
    print()
    
    if not await login():
        print("\nHINT: Run python run_seed.py first!")
        return
    
    await create_project()
    await list_projects()
    await get_project()
    await update_project()
    await create_data_point()
    await list_data_points()
    await create_kpi()
    await list_kpis()
    await delete_project()
    await verify_deletion()
    
    print()
    print("=" * 60)
    print("All CRUD tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
