# 🏗️ Multi-Store Lumber Yard System with Customer-Focused Experience

## 🌟 Overview
Your lumber yard task management system now provides a **customer-focused experience** with hierarchical administration! The system has three levels of access:
- **Super Admin**: Manages all stores and creates store admins
- **Store Admin**: Manages their own store and creates customers
- **Customer**: Views assigned projects, budgets, and communicates with lumber yard staff

## 🔐 Login Credentials

### 👑 **SUPER ADMIN** (Store ID: `GLOBAL`)
- **Username**: `superadmin` | **Password**: `superadmin123`
- **Capabilities**: Can manage ALL stores, create store admins, create customers for any store

### 🏢 **Downtown Lumberyard** (Store ID: `STORE_001`)
- **🏪 Store Admin**: Username: `admin` | Password: `admin`
- **🛒 Customer**: Username: `demo` | Password: `demo`  
- **🛒 Customer**: Username: `john` | Password: `john123`

### 🏢 **Northside Lumber Co** (Store ID: `STORE_002`)
- **🏪 Store Admin**: Username: `manager` | Password: `manager123`
- **🛒 Customer**: Username: `sarah` | Password: `sarah123`
- **🛒 Customer**: Username: `mike` | Password: `mike123`

### 🏢 **Westend Building Supply** (Store ID: `STORE_003`)
- **🏪 Store Admin**: Username: `supervisor` | Password: `super123`
- **🛒 Customer**: Username: `emma` | Password: `emma123`

## 🔧 How to Login

1. **Store ID**: Enter store ID (e.g., `GLOBAL` for super admin, `STORE_001` for store users)
2. **Username**: Enter your username
3. **Password**: Enter your password
4. **Click Sign In**

## ✨ Hierarchical User Management

### 👑 **Super Admin Powers**
- **View All Stores**: See data from all lumber yards
- **Create Store Admins**: Set up administrators for new locations  
- **Create Users for Any Store**: Add users to any lumber yard
- **Delete Any User**: Can permanently delete or deactivate any user/admin across all stores
- **Cross-Store Management**: Assign projects across different stores

### 🏪 **Store Admin Powers**  
- **Manage Their Store Only**: Full control within their lumber yard
- **Create Regular Users**: Add employees to their store only
- **Create Store Admins**: Can now create other administrators for their store
- **Store-Specific Data**: See only their store's projects, tasks, and users

### 🛒 **Customer Experience**
- **View Projects & Quotes**: See assigned house building projects
- **Budget Transparency**: View estimated costs, actual spending, and remaining budget
- **Progress Tracking**: Monitor project progress and timelines
- **Communication**: Message lumber yard staff and administrators
- **Read-Only Access**: Cannot edit projects but can view all details

### 👤 **Customer Dashboard Features**
- **Budget Overview**: See total estimated costs vs actual spending
- **Project Progress**: Track completion status of assigned projects
- **Cost Breakdown**: Detailed view of materials, labor, equipment, and permit costs
- **Spending Alerts**: Visual indicators if projects are over budget
- **Clean Interface**: Simplified, customer-focused navigation and layout

## 🧪 Testing the Hierarchical System

### Test Super Admin Capabilities:
1. **Login as Super Admin** (`GLOBAL` / `superadmin` / `superadmin123`)
2. **Go to Admin Panel** and click "Add User"
3. **Create Store Admin**: Choose role "Store Administrator" and set Store ID to `STORE_004`
4. **Create Regular User**: Choose role "Regular User" for any store
5. **View All Users**: See users from all stores in the user list

### Test Store Admin Capabilities:
1. **Login as Store Admin** (`STORE_001` / `admin` / `admin`)
2. **Go to Admin Panel** - notice you can now create "Store Administrator" role
3. **Create Store Admin**: Choose role "Store Administrator" for your store
4. **Store ID is Fixed**: Cannot change store ID (locked to your store)
5. **User List**: See only users from your store (STORE_001)
6. **Test Restriction**: Cannot create super admins (option not available)

### Test Regular User Restrictions:
1. **Login as Regular User** (`STORE_001` / `demo` / `demo`)
2. **No Admin Panel**: Admin panel not accessible
3. **No Edit Buttons**: Cannot edit house rooms or projects
4. **Limited Dashboard**: See only assigned project statistics

## 🎯 Perfect For:
- **Multi-location lumber yard chains**
- **Franchise operations with central management**
- **Regional building supply networks**
- **Corporate structures with store-level management**

## 🚀 User Creation Workflow

### For New Lumber Yard Locations:
1. **Super Admin** creates a Store Admin for the new location
2. **Store Admin** logs in and creates Regular Users for their employees
3. **Store Admin** creates projects and assigns users to them
4. **Regular Users** log in and see only their assigned work

### Role Hierarchy:
```
Super Admin (GLOBAL)
    ├── Store Admin (STORE_001) → Regular Users (STORE_001)
    ├── Store Admin (STORE_002) → Regular Users (STORE_002)  
    └── Store Admin (STORE_003) → Regular Users (STORE_003)
```

Your system now provides enterprise-level user management with complete security and proper delegation of authority! 🏗️✨