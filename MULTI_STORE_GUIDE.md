# 🏗️ Multi-Store Lumber Yard System

## 🌟 Overview
Your lumber yard task management system now supports **multiple stores** with complete data isolation! Each lumber yard location operates independently with their own admins, users, projects, and data.

## 🔐 Login Credentials

### 🏢 **Downtown Lumberyard** (Store ID: `STORE_001`)
- **👑 Admin**: Username: `admin` | Password: `admin`
- **👤 User**: Username: `demo` | Password: `demo`  
- **👤 User**: Username: `john` | Password: `john123`

### 🏢 **Northside Lumber Co** (Store ID: `STORE_002`)
- **👑 Admin**: Username: `manager` | Password: `manager123`
- **👤 User**: Username: `sarah` | Password: `sarah123`
- **👤 User**: Username: `mike` | Password: `mike123`

### 🏢 **Westend Building Supply** (Store ID: `STORE_003`)
- **👑 Admin**: Username: `supervisor` | Password: `super123`
- **👤 User**: Username: `emma` | Password: `emma123`

## 🔧 How to Login

1. **Store ID**: Enter your lumber yard's store ID (e.g., `STORE_001`)
2. **Username**: Enter your username (e.g., `admin`)
3. **Password**: Enter your password (e.g., `admin`)
4. **Click Sign In**

## ✨ Key Features

### 🔒 **Complete Data Isolation**
- Each store can only see their own projects, tasks, and ideas
- Store 1 admins cannot access Store 2 data
- Users are completely separated by store

### 👥 **Role-Based Access**
- **Admins**: Full control within their store (create/edit/delete projects, manage users)
- **Users**: View-only access to assigned projects within their store

### 🚀 **Multi-Tenancy Benefits**
- Multiple lumber yards can use the same system
- Each location maintains independent operations
- Secure data separation between locations
- Individual user management per store

## 🧪 Testing Multi-Store Functionality

### Test Data Isolation:
1. **Login as Store 1 Admin** (`STORE_001` / `admin` / `admin`)
2. **Create a project** called "Store 1 Project"
3. **Logout and login as Store 2 Admin** (`STORE_002` / `manager` / `manager123`)
4. **Verify you don't see** "Store 1 Project" 
5. **Create a different project** for Store 2
6. **Switch back to Store 1** - confirm you only see Store 1 data

### Test Ideas Board:
- Each store has separate Ideas Boards
- Edit/Delete functionality works within each store
- Ideas are completely isolated between stores

### Test Calendar:
- Regular users see only events from their assigned projects
- Admin users see all events within their store only
- No cross-store calendar visibility

## 🎯 Perfect For:
- **Multi-location lumber yards**
- **Franchise operations**
- **Regional building supply chains**
- **Independent stores using shared infrastructure**

Your system now scales to support unlimited lumber yard locations while maintaining complete security and data isolation! 🏗️✨