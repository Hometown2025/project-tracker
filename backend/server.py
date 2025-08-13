from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, date
import json
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

# Models
class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    color: str = "#8B5CF6"  # Purple default
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_date: datetime = Field(default_factory=datetime.utcnow)
    task_count: Optional[int] = 0
    completed_tasks: Optional[int] = 0

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#8B5CF6"

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    due_date: Optional[date] = None
    order_date: Optional[date] = None
    delivery_date: Optional[date] = None
    status: TaskStatus = TaskStatus.TODO
    completed: bool = False
    created_date: datetime = Field(default_factory=datetime.utcnow)
    completed_date: Optional[datetime] = None

class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    due_date: Optional[date] = None
    order_date: Optional[date] = None
    delivery_date: Optional[date] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    due_date: Optional[date] = None
    order_date: Optional[date] = None
    delivery_date: Optional[date] = None
    status: Optional[TaskStatus] = None
    completed: Optional[bool] = None

class Idea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    title: str
    description: Optional[str] = None
    image_data: Optional[str] = None  # Base64 encoded image
    pinterest_url: Optional[str] = None
    tags: List[str] = []
    created_date: datetime = Field(default_factory=datetime.utcnow)

class IdeaCreate(BaseModel):
    project_id: str
    title: str
    description: Optional[str] = None
    image_data: Optional[str] = None
    pinterest_url: Optional[str] = None
    tags: List[str] = []

# Dashboard Stats Model
class DashboardStats(BaseModel):
    total_projects: int
    active_projects: int
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    today_tasks: int
    ideas_count: int

# Project Routes
@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    project_dict = project.dict()
    project_obj = Project(**project_dict)
    await db.projects.insert_one(project_obj.dict())
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().to_list(1000)
    
    # Calculate task counts for each project
    for project in projects:
        project_id = project['id']
        total_tasks = await db.tasks.count_documents({"project_id": project_id})
        completed_tasks = await db.tasks.count_documents({"project_id": project_id, "completed": True})
        
        project['task_count'] = total_tasks
        project['completed_tasks'] = completed_tasks
    
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate task counts
    total_tasks = await db.tasks.count_documents({"project_id": project_id})
    completed_tasks = await db.tasks.count_documents({"project_id": project_id, "completed": True})
    
    project['task_count'] = total_tasks
    project['completed_tasks'] = completed_tasks
    
    return Project(**project)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, updates: ProjectCreate):
    result = await db.projects.update_one(
        {"id": project_id},
        {"$set": updates.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_project = await db.projects.find_one({"id": project_id})
    return Project(**updated_project)

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    # Delete all tasks and ideas associated with the project
    await db.tasks.delete_many({"project_id": project_id})
    await db.ideas.delete_many({"project_id": project_id})
    
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Project deleted successfully"}

# Helper function to serialize dates
def serialize_dates(data):
    """Convert date objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, date) and not isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, datetime):
                result[key] = value
            elif isinstance(value, dict):
                result[key] = serialize_dates(value)
            else:
                result[key] = value
        return result
    return data

def deserialize_dates(data, date_fields=['due_date', 'order_date', 'delivery_date']):
    """Convert ISO date strings back to date objects"""
    if isinstance(data, dict):
        for field in date_fields:
            if field in data and isinstance(data[field], str):
                try:
                    # Parse ISO date string to date object
                    data[field] = datetime.fromisoformat(data[field]).date()
                except (ValueError, TypeError):
                    pass
    return data
# Task Routes
@api_router.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    task_dict = task.dict()
    task_obj = Task(**task_dict)
    
    # Serialize dates for MongoDB storage
    task_data = serialize_dates(task_obj.dict())
    
    await db.tasks.insert_one(task_data)
    return task_obj

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(project_id: Optional[str] = None, status: Optional[TaskStatus] = None):
    query = {}
    if project_id:
        query["project_id"] = project_id
    if status:
        query["status"] = status
    
    tasks = await db.tasks.find(query).to_list(1000)
    
    # Deserialize dates for response
    for task in tasks:
        deserialize_dates(task)
    
    return [Task(**task) for task in tasks]

@api_router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Deserialize dates for response
    deserialize_dates(task)
    
    return Task(**task)

@api_router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, updates: TaskUpdate):
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    
    # Handle task completion
    if updates.completed is True:
        update_dict["completed_date"] = datetime.utcnow()
        update_dict["status"] = TaskStatus.COMPLETED
    elif updates.completed is False:
        update_dict["completed_date"] = None
        if update_dict.get("status") == TaskStatus.COMPLETED:
            update_dict["status"] = TaskStatus.TODO
    
    # Serialize dates for MongoDB storage
    update_dict = serialize_dates(update_dict)
    
    result = await db.tasks.update_one(
        {"id": task_id},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated_task = await db.tasks.find_one({"id": task_id})
    deserialize_dates(updated_task)
    
    return Task(**updated_task)

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    result = await db.tasks.delete_one({"id": task_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}

# Ideas Routes
@api_router.post("/ideas", response_model=Idea)
async def create_idea(idea: IdeaCreate):
    idea_dict = idea.dict()
    idea_obj = Idea(**idea_dict)
    await db.ideas.insert_one(idea_obj.dict())
    return idea_obj

@api_router.get("/ideas", response_model=List[Idea])
async def get_ideas(project_id: Optional[str] = None):
    query = {}
    if project_id:
        query["project_id"] = project_id
    
    ideas = await db.ideas.find(query).to_list(1000)
    return [Idea(**idea) for idea in ideas]

@api_router.get("/ideas/{idea_id}", response_model=Idea)
async def get_idea(idea_id: str):
    idea = await db.ideas.find_one({"id": idea_id})
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return Idea(**idea)

@api_router.put("/ideas/{idea_id}", response_model=Idea)
async def update_idea(idea_id: str, updates: IdeaCreate):
    result = await db.ideas.update_one(
        {"id": idea_id},
        {"$set": updates.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    updated_idea = await db.ideas.find_one({"id": idea_id})
    return Idea(**updated_idea)

@api_router.delete("/ideas/{idea_id}")
async def delete_idea(idea_id: str):
    result = await db.ideas.delete_one({"id": idea_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return {"message": "Idea deleted successfully"}

# Dashboard Route
@api_router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats():
    today = datetime.utcnow().date()
    
    total_projects = await db.projects.count_documents({})
    active_projects = await db.projects.count_documents({"status": ProjectStatus.ACTIVE})
    total_tasks = await db.tasks.count_documents({})
    completed_tasks = await db.tasks.count_documents({"completed": True})
    
    # Count overdue tasks
    overdue_tasks = await db.tasks.count_documents({
        "due_date": {"$lt": today},
        "completed": False
    })
    
    # Count tasks due today
    today_tasks = await db.tasks.count_documents({
        "due_date": today,
        "completed": False
    })
    
    ideas_count = await db.ideas.count_documents({})
    
    return DashboardStats(
        total_projects=total_projects,
        active_projects=active_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks,
        today_tasks=today_tasks,
        ideas_count=ideas_count
    )

# Calendar data endpoint
@api_router.get("/calendar")
async def get_calendar_data():
    tasks_with_dates = await db.tasks.find({
        "$or": [
            {"due_date": {"$exists": True, "$ne": None}},
            {"order_date": {"$exists": True, "$ne": None}},
            {"delivery_date": {"$exists": True, "$ne": None}}
        ]
    }).to_list(1000)
    
    calendar_events = []
    for task in tasks_with_dates:
        # Deserialize dates
        deserialize_dates(task)
        
        # Create events for each date type
        if task.get("due_date"):
            calendar_events.append({
                "id": f"{task['id']}_due",
                "task_id": task["id"],
                "title": f"📋 {task['title']}",
                "date": task["due_date"].isoformat(),
                "priority": task["priority"],
                "status": task["status"],
                "project_id": task["project_id"],
                "event_type": "due_date",
                "event_label": "Due"
            })
        
        if task.get("order_date"):
            calendar_events.append({
                "id": f"{task['id']}_order",
                "task_id": task["id"],
                "title": f"📦 Order: {task['title']}",
                "date": task["order_date"].isoformat(),
                "priority": task["priority"],
                "status": task["status"],
                "project_id": task["project_id"],
                "event_type": "order_date",
                "event_label": "Order"
            })
        
        if task.get("delivery_date"):
            calendar_events.append({
                "id": f"{task['id']}_delivery",
                "task_id": task["id"],
                "title": f"🚚 Delivery: {task['title']}",
                "date": task["delivery_date"].isoformat(),
                "priority": task["priority"],
                "status": task["status"],
                "project_id": task["project_id"],
                "event_type": "delivery_date",
                "event_label": "Delivery"
            })
    
    # Sort events by date
    calendar_events.sort(key=lambda x: x["date"])
    
    return calendar_events

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()