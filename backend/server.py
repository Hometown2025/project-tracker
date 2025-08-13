from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, date, timedelta
import json
from enum import Enum
import hashlib
import secrets

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

# Security
security = HTTPBearer()

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

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: Optional[str] = None
    role: UserRole = UserRole.USER
    assigned_projects: List[str] = []  # List of project IDs user can access
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    role: UserRole = UserRole.USER

class UserLogin(BaseModel):
    username: str
    password: str

class UserSession(BaseModel):
    user_id: str
    username: str
    role: UserRole
    session_token: str
    expires_at: datetime

class UserAssignment(BaseModel):
    user_id: str
    project_ids: List[str]

# Helper Functions
def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwd_hash.hex()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    salt = hashed[:32]
    stored_hash = hashed[32:]
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwd_hash.hex() == stored_hash

def generate_session_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from session token"""
    session_token = credentials.credentials
    
    # Find active session
    session = await db.sessions.find_one({
        "session_token": session_token,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    # Get user
    user = await db.users.find_one({"id": session["user_id"], "is_active": True})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return User(**user)

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def initialize_default_data():
    """Initialize default admin and demo user"""
    # Check if admin already exists
    admin_exists = await db.users.find_one({"username": "admin"})
    if not admin_exists:
        admin_user = User(
            username="admin",
            role=UserRole.ADMIN,
            email="admin@taskflow.com"
        )
        admin_password = hash_password("admin")
        
        await db.users.insert_one(admin_user.dict())
        await db.user_passwords.insert_one({
            "user_id": admin_user.id,
            "password_hash": admin_password
        })
        print("✅ Default admin user created (admin/admin)")
    
    # Check if demo user exists
    demo_exists = await db.users.find_one({"username": "demo"})
    if not demo_exists:
        demo_user = User(
            username="demo",
            role=UserRole.USER,
            email="demo@taskflow.com"
        )
        demo_password = hash_password("demo")
        
        await db.users.insert_one(demo_user.dict())
        await db.user_passwords.insert_one({
            "user_id": demo_user.id,
            "password_hash": demo_password
        })
        
        # Assign existing projects to demo user
        existing_projects = await db.projects.find({}).to_list(1000)
        project_ids = [p["id"] for p in existing_projects]
        
        if project_ids:
            # Update demo user with project assignments
            await db.users.update_one(
                {"id": demo_user.id},
                {"$set": {"assigned_projects": project_ids}}
            )
            
            # Add owner field to existing projects
            for project in existing_projects:
                await db.projects.update_one(
                    {"id": project["id"]},
                    {"$set": {"owner_id": demo_user.id}}
                )
            
            # Add owner field to existing tasks
            existing_tasks = await db.tasks.find({}).to_list(1000)
            for task in existing_tasks:
                await db.tasks.update_one(
                    {"id": task["id"]},
                    {"$set": {"owner_id": demo_user.id}}
                )
            
            # Add owner field to existing ideas
            existing_ideas = await db.ideas.find({}).to_list(1000)
            for idea in existing_ideas:
                await db.ideas.update_one(
                    {"id": idea["id"]},
                    {"$set": {"owner_id": demo_user.id}}
                )
        
        print("✅ Demo user created and assigned existing projects")

# Authentication Routes
@api_router.post("/auth/login")
async def login(login_data: UserLogin):
    """User login"""
    # Find user
    user = await db.users.find_one({"username": login_data.username, "is_active": True})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # Check password
    password_record = await db.user_passwords.find_one({"user_id": user["id"]})
    if not password_record or not verify_password(login_data.password, password_record["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # Create session
    session_token = generate_session_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)  # 24 hour sessions
    
    session = UserSession(
        user_id=user["id"],
        username=user["username"],
        role=user["role"],
        session_token=session_token,
        expires_at=expires_at
    )
    
    # Clean up old sessions for this user
    await db.sessions.delete_many({"user_id": user["id"]})
    
    # Store new session
    await db.sessions.insert_one(session.dict())
    
    # Update last login
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    return {
        "session_token": session_token,
        "user": User(**user).dict(),
        "expires_at": expires_at
    }

@api_router.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """User logout"""
    # Delete all sessions for this user
    await db.sessions.delete_many({"user_id": current_user.id})
    return {"message": "Logged out successfully"}

@api_router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Admin User Management Routes
@api_router.post("/admin/users", response_model=User)
async def create_user(user_data: UserCreate, admin_user: User = Depends(require_admin)):
    """Admin: Create new user"""
    # Check if username already exists
    existing = await db.users.find_one({"username": user_data.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        role=user_data.role
    )
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Store user and password
    await db.users.insert_one(user.dict())
    await db.user_passwords.insert_one({
        "user_id": user.id,
        "password_hash": password_hash
    })
    
    return user

@api_router.get("/admin/users", response_model=List[User])
async def get_all_users(admin_user: User = Depends(require_admin)):
    """Admin: Get all users"""
    users = await db.users.find({"is_active": True}).to_list(1000)
    return [User(**user) for user in users]

@api_router.put("/admin/users/{user_id}/assign-projects")
async def assign_projects_to_user(
    user_id: str, 
    assignment: UserAssignment, 
    admin_user: User = Depends(require_admin)
):
    """Admin: Assign projects to user"""
    # Verify user exists
    user = await db.users.find_one({"id": user_id, "is_active": True})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify all projects exist
    for project_id in assignment.project_ids:
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Update user's assigned projects
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"assigned_projects": assignment.project_ids}}
    )
    
    return {"message": "Projects assigned successfully"}

@api_router.delete("/admin/users/{user_id}")
async def deactivate_user(user_id: str, admin_user: User = Depends(require_admin)):
    """Admin: Deactivate user"""
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete user's sessions
    await db.sessions.delete_many({"user_id": user_id})
    
    return {"message": "User deactivated successfully"}

# Models
class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    color: str = "#8B5CF6"  # Purple default
    status: ProjectStatus = ProjectStatus.ACTIVE
    owner_id: Optional[str] = None  # User who owns this project
    created_date: datetime = Field(default_factory=datetime.utcnow)
    task_count: Optional[int] = 0
    completed_tasks: Optional[int] = 0

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#8B5CF6"

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[str] = None
    owner_id: Optional[str] = None  # User who owns this task
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
    project_id: Optional[str] = None
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
    owner_id: Optional[str] = None  # User who owns this idea
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
async def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user)):
    """Create project (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can create projects")
    
    project_dict = project.dict()
    project_obj = Project(**project_dict, owner_id=current_user.id)
    await db.projects.insert_one(project_obj.dict())
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects(current_user: User = Depends(get_current_user)):
    """Get projects - Admin sees all, Users see assigned only"""
    if current_user.role == UserRole.ADMIN:
        projects = await db.projects.find().to_list(1000)
    else:
        # Users only see projects they're assigned to
        projects = await db.projects.find({"id": {"$in": current_user.assigned_projects}}).to_list(1000)
    
    # Calculate task counts for each project
    for project in projects:
        project_id = project['id']
        total_tasks = await db.tasks.count_documents({"project_id": project_id})
        completed_tasks = await db.tasks.count_documents({"project_id": project_id, "completed": True})
        
        project['task_count'] = total_tasks
        project['completed_tasks'] = completed_tasks
    
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Get single project"""
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permissions
    if current_user.role != UserRole.ADMIN and project_id not in current_user.assigned_projects:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Calculate task counts
    total_tasks = await db.tasks.count_documents({"project_id": project_id})
    completed_tasks = await db.tasks.count_documents({"project_id": project_id, "completed": True})
    
    project['task_count'] = total_tasks
    project['completed_tasks'] = completed_tasks
    
    return Project(**project)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, updates: ProjectCreate, current_user: User = Depends(get_current_user)):
    """Update project (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can edit projects")
    
    result = await db.projects.update_one(
        {"id": project_id},
        {"$set": updates.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_project = await db.projects.find_one({"id": project_id})
    return Project(**updated_project)

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Delete project (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can delete projects")
    
    # Delete all tasks and ideas associated with the project
    await db.tasks.delete_many({"project_id": project_id})
    await db.ideas.delete_many({"project_id": project_id})
    
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Remove project from all users' assigned projects
    await db.users.update_many(
        {"assigned_projects": project_id},
        {"$pull": {"assigned_projects": project_id}}
    )
    
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
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    """Create task (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can create tasks")
    
    task_dict = task.dict()
    task_obj = Task(**task_dict, owner_id=current_user.id)
    
    # Serialize dates for MongoDB storage
    task_data = serialize_dates(task_obj.dict())
    
    await db.tasks.insert_one(task_data)
    return task_obj

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(project_id: Optional[str] = None, status: Optional[TaskStatus] = None, current_user: User = Depends(get_current_user)):
    """Get tasks - Admin sees all, Users see tasks from assigned projects only"""
    query = {}
    if project_id:
        # Check if user has access to this project
        if current_user.role != UserRole.ADMIN and project_id not in current_user.assigned_projects:
            raise HTTPException(status_code=403, detail="Access denied")
        query["project_id"] = project_id
    if status:
        query["status"] = status
    
    # Apply user-specific filtering
    if current_user.role != UserRole.ADMIN:
        # Users only see tasks from projects they're assigned to or unassigned tasks they own
        query["$or"] = [
            {"project_id": {"$in": current_user.assigned_projects}},
            {"project_id": None, "owner_id": current_user.id}
        ]
    
    tasks = await db.tasks.find(query).to_list(1000)
    
    # Deserialize dates for response
    for task in tasks:
        deserialize_dates(task)
    
    return [Task(**task) for task in tasks]

@api_router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str, current_user: User = Depends(get_current_user)):
    """Get single task"""
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    if current_user.role != UserRole.ADMIN:
        project_id = task.get("project_id")
        if project_id and project_id not in current_user.assigned_projects:
            raise HTTPException(status_code=403, detail="Access denied")
        elif not project_id and task.get("owner_id") != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Deserialize dates for response
    deserialize_dates(task)
    
    return Task(**task)

@api_router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, updates: TaskUpdate, current_user: User = Depends(get_current_user)):
    """Update task (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can edit tasks")
    
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
async def delete_task(task_id: str, current_user: User = Depends(get_current_user)):
    """Delete task (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can delete tasks")
    
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
    today = date.today()
    today_str = today.isoformat()
    
    total_projects = await db.projects.count_documents({})
    active_projects = await db.projects.count_documents({"status": ProjectStatus.ACTIVE})
    total_tasks = await db.tasks.count_documents({})
    completed_tasks = await db.tasks.count_documents({"completed": True})
    
    # Count overdue tasks (check all date fields)
    overdue_tasks = await db.tasks.count_documents({
        "$or": [
            {"due_date": {"$lt": today_str}, "completed": False},
            {"delivery_date": {"$lt": today_str}, "completed": False}
        ]
    })
    
    # Count tasks due today (check all date fields)
    today_tasks = await db.tasks.count_documents({
        "$or": [
            {"due_date": today_str, "completed": False},
            {"order_date": today_str},
            {"delivery_date": today_str, "completed": False}
        ]
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