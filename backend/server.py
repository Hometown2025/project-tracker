from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, date, timedelta
import json
from enum import Enum
import hashlib
import secrets
import aiofiles
import shutil
from PIL import Image

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# File storage configuration
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# File size limit (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Supported file types
ALLOWED_EXTENSIONS = {
    # Images
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico',
    # Documents
    'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'pages',
    # Spreadsheets
    'xls', 'xlsx', 'csv', 'ods', 'numbers',
    # Presentations
    'ppt', 'pptx', 'odp', 'key',
    # Archives
    'zip', 'rar', '7z', 'tar', 'gz', 'bz2',
    # Audio
    'mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg',
    # Video
    'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv',
    # Code
    'js', 'ts', 'py', 'html', 'css', 'json', 'xml', 'yaml', 'yml',
    'php', 'cpp', 'c', 'java', 'go', 'rs', 'rb', 'swift', 'kt',
    # Other
    'md', 'log', 'sql', 'sh', 'bat', 'ps1'
}

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

# File Models
class FileAttachment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    mime_type: str
    file_path: str
    thumbnail_path: Optional[str] = None
    project_id: Optional[str] = None
    task_id: Optional[str] = None
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    is_image: bool = False

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_size: int
    file_type: str
    upload_url: Optional[str] = None



# Notification Models
class NotificationType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    MESSAGE_RECEIVED = "message_received"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: NotificationType
    title: str
    message: str
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    task_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Message Models
class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    sender_id: str
    sender_name: str
    sender_role: UserRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False

class MessageCreate(BaseModel):
    content: str
    recipient_type: str = "admin"  # "admin" or "user"
    recipient_id: Optional[str] = None

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    participants: List[str]  # List of user IDs
    title: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: datetime = Field(default_factory=datetime.utcnow)
    unread_count: Dict[str, int] = {}  # user_id -> unread count

# Helper function to send notifications to project members (polling-based)
async def send_notification_to_project_members(notification_type: NotificationType, title: str, message: str, project_id: str):
    """Send notification to project members and admins via database storage"""
    # Get users assigned to this project
    users = await db.users.find({"assigned_projects": project_id, "is_active": True}).to_list(1000)
    
    # Get all admin users
    admin_users = await db.users.find({"role": "admin", "is_active": True}).to_list(1000)
    
    # Combine and deduplicate user IDs
    all_user_ids = list(set([user["id"] for user in users] + [admin["id"] for admin in admin_users]))
    
    # Create notification for each user
    for user_id in all_user_ids:
        await create_notification(notification_type, title, message, user_id)

# Helper function to send notifications to all admins (polling-based)
async def send_notification_to_admins(notification_type: NotificationType, title: str, message: str):
    """Send notification to all admin users via database storage"""
    admin_users = await db.users.find({"role": "admin", "is_active": True}).to_list(1000)
    
    for admin in admin_users:
        await create_notification(notification_type, title, message, admin["id"])

# Helper function to create notifications in database (for polling)
async def create_notification(notification_type: NotificationType, title: str, message: str, user_id: str):
    """Create a notification in the database for polling-based system"""
    notification = Notification(
        type=notification_type,
        title=title,
        message=message,
        user_id=user_id
    )
    
    # Add is_read field for database storage
    notification_dict = notification.dict()
    notification_dict["is_read"] = False
    
    await db.notifications.insert_one(notification_dict)

# File utility functions
def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.split('.')[-1].lower() if '.' in filename else ''

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    extension = get_file_extension(filename)
    return extension in ALLOWED_EXTENSIONS

def is_image_file(filename: str) -> bool:
    """Check if file is an image"""
    extension = get_file_extension(filename)
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico'}
    return extension in image_extensions

def get_file_type_category(filename: str) -> str:
    """Get file type category for display purposes"""
    extension = get_file_extension(filename)
    
    if extension in {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico'}:
        return 'image'
    elif extension in {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'pages'}:
        return 'document'
    elif extension in {'xls', 'xlsx', 'csv', 'ods', 'numbers'}:
        return 'spreadsheet'
    elif extension in {'ppt', 'pptx', 'odp', 'key'}:
        return 'presentation'
    elif extension in {'zip', 'rar', '7z', 'tar', 'gz', 'bz2'}:
        return 'archive'
    elif extension in {'mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg'}:
        return 'audio'
    elif extension in {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}:
        return 'video'
    elif extension in {'js', 'ts', 'py', 'html', 'css', 'json', 'xml', 'yaml', 'yml', 'php', 'cpp', 'c', 'java', 'go', 'rs', 'rb', 'swift', 'kt'}:
        return 'code'
    else:
        return 'other'

async def create_thumbnail(file_path: str, thumbnail_path: str) -> bool:
    """Create thumbnail for image files"""
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail (200x200)
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=85)
            return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False

def get_safe_filename(filename: str) -> str:
    """Generate safe filename for storage"""
    # Remove dangerous characters and limit length
    safe_chars = "-_.abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    name, ext = os.path.splitext(filename)
    safe_name = ''.join(c for c in name if c in safe_chars)[:50]
    return f"{safe_name}{ext}" if safe_name else f"file{ext}"

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

# Polling endpoints for notifications
@api_router.get("/notifications/poll")
async def poll_notifications(current_user: User = Depends(get_current_user)):
    """Poll for new notifications"""
    notifications = await db.notifications.find({
        "user_id": current_user.id,
        "is_read": False
    }).sort("created_at", -1).to_list(50)
    
    # Clean up MongoDB ObjectIds
    for notification in notifications:
        if "_id" in notification:
            del notification["_id"]
    
    return notifications

@api_router.post("/notifications/mark-read")
async def mark_notifications_read(current_user: User = Depends(get_current_user)):
    """Mark all notifications as read for current user"""
    await db.notifications.update_many(
        {"user_id": current_user.id, "is_read": False},
        {"$set": {"is_read": True}}
    )
    return {"message": "Notifications marked as read"}

@api_router.get("/messages/poll")
async def poll_unread_messages(current_user: User = Depends(get_current_user)):
    """Poll for unread message count"""
    # Count unread messages in conversations where user is participant
    conversations = await db.conversations.find({
        "participants": current_user.id
    }).to_list(1000)
    
    total_unread = 0
    for conv in conversations:
        unread_count = conv.get("unread_count", {}).get(current_user.id, 0)
        total_unread += unread_count
    
    return {"unread_count": total_unread}

# WebSocket functionality removed - using polling-based notifications instead

# File Upload Routes
@api_router.post("/files/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    task_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Upload a file attachment"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Reset file pointer
    await file.seek(0)
    
    # Validate project/task permissions
    if project_id:
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check permissions
        if current_user.role != UserRole.ADMIN and project_id not in current_user.assigned_projects:
            raise HTTPException(status_code=403, detail="Access denied")
    
    if task_id:
        task = await db.tasks.find_one({"id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Check task permissions
        if current_user.role != UserRole.ADMIN:
            task_project_id = task.get("project_id")
            if task_project_id and task_project_id not in current_user.assigned_projects:
                raise HTTPException(status_code=403, detail="Access denied")
            elif not task_project_id and task.get("owner_id") != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
    
    # Generate file paths
    file_id = str(uuid.uuid4())
    file_extension = get_file_extension(file.filename)
    safe_filename = f"{file_id}.{file_extension}"
    
    # Create directory structure
    if project_id:
        file_dir = UPLOAD_DIR / "projects" / project_id
    elif task_id:
        file_dir = UPLOAD_DIR / "tasks" / task_id
    else:
        file_dir = UPLOAD_DIR / "general"
    
    file_dir.mkdir(parents=True, exist_ok=True)
    file_path = file_dir / safe_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    # Create thumbnail for images
    thumbnail_path = None
    if is_image_file(file.filename):
        thumbnail_filename = f"{file_id}_thumb.jpg"
        thumbnail_path = file_dir / thumbnail_filename
        await create_thumbnail(str(file_path), str(thumbnail_path))
    
    # Create file record
    file_attachment = FileAttachment(
        id=file_id,
        filename=safe_filename,
        original_filename=file.filename,
        file_size=len(file_content),
        file_type=get_file_type_category(file.filename),
        mime_type=file.content_type or 'application/octet-stream',
        file_path=str(file_path),
        thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
        project_id=project_id,
        task_id=task_id,
        uploaded_by=current_user.id,
        is_image=is_image_file(file.filename)
    )
    
    await db.file_attachments.insert_one(file_attachment.dict())
    
    # Send notification
    if project_id:
        await send_notification_to_project_members(
            NotificationType.PROJECT_UPDATED,
            "File Uploaded",
            f"File '{file.filename}' has been uploaded to project by {current_user.username}",
            project_id
        )
    elif task_id:
        task = await db.tasks.find_one({"id": task_id})
        task_project_id = task.get("project_id") if task else None
        
        if task_project_id:
            await send_notification_to_project_members(
                NotificationType.TASK_UPDATED,
                "File Uploaded",
                f"File '{file.filename}' has been uploaded to task '{task['title']}' by {current_user.username}",
                task_project_id
            )
        else:
            await send_notification_to_admins(
                NotificationType.TASK_UPDATED,
                "File Uploaded",
                f"File '{file.filename}' has been uploaded to task by {current_user.username}"
            )
    
    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename,
        file_size=len(file_content),
        file_type=get_file_type_category(file.filename)
    )

@api_router.get("/files/project/{project_id}")
async def get_project_files(project_id: str, current_user: User = Depends(get_current_user)):
    """Get all files for a project"""
    # Check permissions
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user.role != UserRole.ADMIN and project_id not in current_user.assigned_projects:
        raise HTTPException(status_code=403, detail="Access denied")
    
    files = await db.file_attachments.find({"project_id": project_id}).to_list(1000)
    
    # Clean up MongoDB ObjectIds
    for file_obj in files:
        if "_id" in file_obj:
            del file_obj["_id"]
    
    return files

@api_router.get("/files/task/{task_id}")
async def get_task_files(task_id: str, current_user: User = Depends(get_current_user)):
    """Get all files for a task"""
    # Check permissions
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if current_user.role != UserRole.ADMIN:
        task_project_id = task.get("project_id")
        if task_project_id and task_project_id not in current_user.assigned_projects:
            raise HTTPException(status_code=403, detail="Access denied")
        elif not task_project_id and task.get("owner_id") != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    files = await db.file_attachments.find({"task_id": task_id}).to_list(1000)
    
    # Clean up MongoDB ObjectIds
    for file_obj in files:
        if "_id" in file_obj:
            del file_obj["_id"]
    
    return files

@api_router.get("/files/download/{file_id}")
async def download_file(file_id: str, current_user: User = Depends(get_current_user)):
    """Download a file"""
    file_record = await db.file_attachments.find_one({"id": file_id})
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check permissions based on project/task
    if file_record.get("project_id"):
        project_id = file_record["project_id"]
        if current_user.role != UserRole.ADMIN and project_id not in current_user.assigned_projects:
            raise HTTPException(status_code=403, detail="Access denied")
    elif file_record.get("task_id"):
        task = await db.tasks.find_one({"id": file_record["task_id"]})
        if task and current_user.role != UserRole.ADMIN:
            task_project_id = task.get("project_id")
            if task_project_id and task_project_id not in current_user.assigned_projects:
                raise HTTPException(status_code=403, detail="Access denied")
            elif not task_project_id and task.get("owner_id") != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
    
    file_path = file_record["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=file_record["original_filename"],
        media_type=file_record["mime_type"]
    )

@api_router.get("/files/thumbnail/{file_id}")
async def get_thumbnail(file_id: str, current_user: User = Depends(get_current_user)):
    """Get thumbnail for an image file"""
    file_record = await db.file_attachments.find_one({"id": file_id})
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not file_record.get("thumbnail_path"):
        raise HTTPException(status_code=404, detail="Thumbnail not available")
    
    # Check permissions (same as download)
    if file_record.get("project_id"):
        project_id = file_record["project_id"]
        if current_user.role != UserRole.ADMIN and project_id not in current_user.assigned_projects:
            raise HTTPException(status_code=403, detail="Access denied")
    elif file_record.get("task_id"):
        task = await db.tasks.find_one({"id": file_record["task_id"]})
        if task and current_user.role != UserRole.ADMIN:
            task_project_id = task.get("project_id")
            if task_project_id and task_project_id not in current_user.assigned_projects:
                raise HTTPException(status_code=403, detail="Access denied")
            elif not task_project_id and task.get("owner_id") != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
    
    thumbnail_path = file_record["thumbnail_path"]
    if not os.path.exists(thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found on disk")
    
    return FileResponse(
        path=thumbnail_path,
        media_type="image/jpeg"
    )

@api_router.delete("/files/{file_id}")
async def delete_file(file_id: str, current_user: User = Depends(get_current_user)):
    """Delete a file"""
    file_record = await db.file_attachments.find_one({"id": file_id})
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check permissions - only admin or file uploader can delete
    if current_user.role != UserRole.ADMIN and file_record["uploaded_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete from database
    await db.file_attachments.delete_one({"id": file_id})
    
    # Delete file from disk
    try:
        if os.path.exists(file_record["file_path"]):
            os.remove(file_record["file_path"])
        
        # Delete thumbnail if exists
        if file_record.get("thumbnail_path") and os.path.exists(file_record["thumbnail_path"]):
            os.remove(file_record["thumbnail_path"])
    except Exception as e:
        print(f"Error deleting file from disk: {e}")
    
    return {"message": "File deleted successfully"}

# Message Routes
@api_router.post("/messages")
async def send_message(message_data: MessageCreate, current_user: User = Depends(get_current_user)):
    """Send a message"""
    # Find or create conversation
    if message_data.recipient_type == "admin":
        # User messaging admin - find existing conversation or create new one
        existing_conv = await db.conversations.find_one({
            "participants": {"$all": [current_user.id]},
            "title": {"$regex": f"^Support.*{current_user.username}"}
        })
        
        if not existing_conv:
            # Create new conversation with admins
            admin_users = await db.users.find({"role": "admin", "is_active": True}).to_list(1000)
            admin_ids = [admin["id"] for admin in admin_users if admin.get("id")]  # Filter out None values
            participants = [current_user.id] + admin_ids
            
            # Initialize unread count for all participants
            unread_count = {current_user.id: 0}
            for admin_id in admin_ids:
                unread_count[admin_id] = 0
            
            conversation = Conversation(
                participants=participants,
                title=f"Support Request - {current_user.username}",
                created_by=current_user.id,
                unread_count=unread_count
            )
            
            await db.conversations.insert_one(conversation.dict())
            conversation_id = conversation.id
        else:
            conversation_id = existing_conv["id"]
    else:
        # Admin messaging specific user
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Only admins can message specific users")
        
        # Find conversation between admin and user
        existing_conv = await db.conversations.find_one({
            "participants": {"$all": [current_user.id, message_data.recipient_id]}
        })
        
        if not existing_conv:
            # Ensure recipient_id is valid
            recipient = await db.users.find_one({"id": message_data.recipient_id, "is_active": True})
            if not recipient:
                raise HTTPException(status_code=404, detail="Recipient user not found")
            
            conversation = Conversation(
                participants=[current_user.id, message_data.recipient_id],
                title=f"Admin Message - {current_user.username}",
                created_by=current_user.id,
                unread_count={current_user.id: 0, message_data.recipient_id: 0}
            )
            await db.conversations.insert_one(conversation.dict())
            conversation_id = conversation.id
        else:
            conversation_id = existing_conv["id"]
    
    # Create message
    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        sender_name=current_user.username,
        sender_role=current_user.role,
        content=message_data.content
    )
    
    await db.messages.insert_one(message.dict())
    
    # Update conversation last message time and unread counts
    conversation = await db.conversations.find_one({"id": conversation_id})
    unread_count = conversation.get("unread_count", {})
    for participant_id in conversation["participants"]:
        if participant_id != current_user.id:
            unread_count[participant_id] = unread_count.get(participant_id, 0) + 1
    
    await db.conversations.update_one(
        {"id": conversation_id},
        {
            "$set": {
                "last_message_at": datetime.utcnow(),
                "unread_count": unread_count
            }
        }
    )
    
    # Send real-time notification via database (for polling)
    for participant_id in conversation["participants"]:
        if participant_id != current_user.id:
            await create_notification(
                NotificationType.MESSAGE_RECEIVED,
                "New Message",
                f"New message in {conversation['title']}",
                participant_id
            )
    
    return message

@api_router.get("/conversations")
async def get_conversations(current_user: User = Depends(get_current_user)):
    """Get user's conversations"""
    conversations = await db.conversations.find({
        "participants": current_user.id
    }).sort("last_message_at", -1).to_list(1000)
    
    # Add last message to each conversation and clean up data
    for conv in conversations:
        # Remove MongoDB ObjectId if present
        if "_id" in conv:
            del conv["_id"]
            
        last_message = await db.messages.find_one(
            {"conversation_id": conv["id"]},
            sort=[("created_at", -1)]
        )
        
        if last_message:
            # Remove MongoDB ObjectId from message if present
            if "_id" in last_message:
                del last_message["_id"]
            conv["last_message"] = last_message
        else:
            conv["last_message"] = None
            
        conv["unread_count_for_user"] = conv.get("unread_count", {}).get(current_user.id, 0)
    
    return conversations

@api_router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, current_user: User = Depends(get_current_user)):
    """Get messages in a conversation"""
    # Verify user is participant
    conversation = await db.conversations.find_one({"id": conversation_id})
    if not conversation or current_user.id not in conversation["participants"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    messages = await db.messages.find({
        "conversation_id": conversation_id
    }).sort("created_at", 1).to_list(1000)
    
    # Clean up MongoDB ObjectIds from messages
    for message in messages:
        if "_id" in message:
            del message["_id"]
    
    # Mark messages as read for current user
    await db.conversations.update_one(
        {"id": conversation_id},
        {"$set": {f"unread_count.{current_user.id}": 0}}
    )
    
    return messages

@api_router.post("/conversations/{conversation_id}/mark-read")
async def mark_conversation_read(conversation_id: str, current_user: User = Depends(get_current_user)):
    """Mark conversation as read"""
    result = await db.conversations.update_one(
        {"id": conversation_id, "participants": current_user.id},
        {"$set": {f"unread_count.{current_user.id}": 0}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"message": "Marked as read"}

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
    file_count: int = 0  # Computed field

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
    file_count: int = 0  # Computed field

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
    
    # Send notification to project members and admins
    await send_notification_to_project_members(
        NotificationType.PROJECT_CREATED,
        "New Project Created",
        f"Project '{project_obj.name}' has been created by {current_user.username}",
        project_obj.id
    )
    
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects(current_user: User = Depends(get_current_user)):
    """Get projects - Admin sees all, Users see assigned only"""
    if current_user.role == UserRole.ADMIN:
        projects = await db.projects.find().to_list(1000)
    else:
        # Users only see projects they're assigned to
        projects = await db.projects.find({"id": {"$in": current_user.assigned_projects}}).to_list(1000)
    
    # Calculate task counts and file counts for each project
    for project in projects:
        project_id = project['id']
        total_tasks = await db.tasks.count_documents({"project_id": project_id})
        completed_tasks = await db.tasks.count_documents({"project_id": project_id, "completed": True})
        file_count = await db.file_attachments.count_documents({"project_id": project_id})
        
        project['task_count'] = total_tasks
        project['completed_tasks'] = completed_tasks
        project['file_count'] = file_count
    
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
    
    # Calculate task counts and file counts
    total_tasks = await db.tasks.count_documents({"project_id": project_id})
    completed_tasks = await db.tasks.count_documents({"project_id": project_id, "completed": True})
    file_count = await db.file_attachments.count_documents({"project_id": project_id})
    
    project['task_count'] = total_tasks
    project['completed_tasks'] = completed_tasks
    project['file_count'] = file_count
    
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
    
    # Send notification
    await send_notification_to_project_members(
        NotificationType.PROJECT_UPDATED,
        "Project Updated",
        f"Project '{updated_project['name']}' has been updated by {current_user.username}",
        project_id
    )
    
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
    
    # Send notification
    project_name = "Unassigned"
    if task_obj.project_id:
        project = await db.projects.find_one({"id": task_obj.project_id})
        if project:
            project_name = project["name"]
    
    if task_obj.project_id:
        await send_notification_to_project_members(
            NotificationType.TASK_CREATED,
            "New Task Created",
            f"Task '{task_obj.title}' has been created in {project_name} by {current_user.username}",
            task_obj.project_id
        )
    else:
        await send_notification_to_admins(
            NotificationType.TASK_CREATED,
            "New Task Created",
            f"Task '{task_obj.title}' has been created in {project_name} by {current_user.username}"
        )
    
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
    
    # Get the existing task first
    existing_task = await db.tasks.find_one({"id": task_id})
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    
    # Handle task completion
    task_completed = False
    if updates.completed is True and not existing_task.get("completed", False):
        update_dict["completed_date"] = datetime.utcnow()
        update_dict["status"] = TaskStatus.COMPLETED
        task_completed = True
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
    
    # Send notification
    project_name = "Unassigned"
    if updated_task.get("project_id"):
        project = await db.projects.find_one({"id": updated_task["project_id"]})
        if project:
            project_name = project["name"]
    
    if task_completed:
        if updated_task.get("project_id"):
            await send_notification_to_project_members(
                NotificationType.TASK_COMPLETED,
                "Task Completed",
                f"Task '{updated_task['title']}' in {project_name} has been completed by {current_user.username}",
                updated_task["project_id"]
            )
        else:
            await send_notification_to_admins(
                NotificationType.TASK_COMPLETED,
                "Task Completed",
                f"Task '{updated_task['title']}' in {project_name} has been completed by {current_user.username}"
            )
    else:
        if updated_task.get("project_id"):
            await send_notification_to_project_members(
                NotificationType.TASK_UPDATED,
                "Task Updated",
                f"Task '{updated_task['title']}' in {project_name} has been updated by {current_user.username}",
                updated_task["project_id"]
            )
        else:
            await send_notification_to_admins(
                NotificationType.TASK_UPDATED,
                "Task Updated",
                f"Task '{updated_task['title']}' in {project_name} has been updated by {current_user.username}"
            )
    
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

@app.on_event("startup")
async def startup_event():
    """Initialize default data on startup"""
    await initialize_default_data()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()