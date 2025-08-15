#!/usr/bin/env python3
"""
Create sample budget data for testing the customer budget functionality
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DATABASE_NAME = 'taskflow_db'

async def create_sample_budgets():
    """Create sample budget data for existing projects"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    print("Creating sample budget data...")
    
    # Get existing projects
    projects = await db.projects.find().to_list(100)
    
    if not projects:
        print("❌ No projects found. Please create some projects first.")
        return
    
    budget_items_data = [
        # Materials
        {"category": "Materials", "items": [
            {"name": "2x4 Lumber", "unit": "board feet", "estimated_cost": 3.50, "quantity": 200},
            {"name": "Plywood Sheets", "unit": "sheets", "estimated_cost": 45.00, "quantity": 15},
            {"name": "Drywall", "unit": "sheets", "estimated_cost": 12.00, "quantity": 25},
            {"name": "Insulation", "unit": "rolls", "estimated_cost": 35.00, "quantity": 20},
            {"name": "Roofing Shingles", "unit": "bundles", "estimated_cost": 85.00, "quantity": 12},
            {"name": "Paint", "unit": "gallons", "estimated_cost": 55.00, "quantity": 8},
        ]},
        # Labor
        {"category": "Labor", "items": [
            {"name": "Framing Labor", "unit": "hours", "estimated_cost": 45.00, "quantity": 40},
            {"name": "Electrical Work", "unit": "hours", "estimated_cost": 65.00, "quantity": 20},
            {"name": "Plumbing", "unit": "hours", "estimated_cost": 60.00, "quantity": 25},
            {"name": "Drywall Installation", "unit": "hours", "estimated_cost": 40.00, "quantity": 16},
            {"name": "Painting", "unit": "hours", "estimated_cost": 35.00, "quantity": 12},
        ]},
        # Equipment
        {"category": "Equipment", "items": [
            {"name": "Tool Rental", "unit": "days", "estimated_cost": 125.00, "quantity": 5},
            {"name": "Excavator Rental", "unit": "days", "estimated_cost": 450.00, "quantity": 2},
            {"name": "Concrete Mixer", "unit": "days", "estimated_cost": 85.00, "quantity": 3},
        ]},
        # Permits
        {"category": "Permits", "items": [
            {"name": "Building Permit", "unit": "each", "estimated_cost": 1200.00, "quantity": 1},
            {"name": "Electrical Permit", "unit": "each", "estimated_cost": 350.00, "quantity": 1},
            {"name": "Plumbing Permit", "unit": "each", "estimated_cost": 285.00, "quantity": 1},
        ]}
    ]
    
    total_created = 0
    
    for project in projects[:3]:  # Create budgets for first 3 projects
        project_id = project['id']
        project_name = project['name']
        
        print(f"\n📊 Creating budget for: {project_name}")
        
        project_total_estimated = 0
        project_actual_cost = 0
        
        # Create budget items for this project
        for category_group in budget_items_data:
            category = category_group["category"]
            
            # Select random items from this category (2-4 items per category)
            import random
            selected_items = random.sample(category_group["items"], min(random.randint(2, 4), len(category_group["items"])))
            
            for item_data in selected_items:
                # Add some randomness to quantities and costs
                quantity_multiplier = random.uniform(0.7, 1.3)
                cost_multiplier = random.uniform(0.9, 1.1)
                
                adjusted_quantity = max(1, int(item_data["quantity"] * quantity_multiplier))
                adjusted_cost = round(item_data["estimated_cost"] * cost_multiplier, 2)
                
                # Sometimes add actual costs (simulate work progress)
                actual_cost = None
                if random.random() < 0.4:  # 40% chance of having actual costs
                    actual_cost = round(adjusted_cost * random.uniform(0.85, 1.15), 2)
                
                budget_item = {
                    "id": str(uuid.uuid4()),
                    "project_id": project_id,
                    "task_id": None,  # Not linked to specific task
                    "item_name": item_data["name"],
                    "description": f"{category} item for {project_name}",
                    "category": category,
                    "estimated_cost": adjusted_cost,
                    "actual_cost": actual_cost,
                    "quantity": adjusted_quantity,
                    "unit": item_data["unit"],
                    "created_date": datetime.utcnow()
                }
                
                await db.budget_items.insert_one(budget_item)
                
                item_total_estimated = adjusted_cost * adjusted_quantity
                item_total_actual = (actual_cost or 0) * adjusted_quantity
                
                project_total_estimated += item_total_estimated
                project_actual_cost += item_total_actual
                
                total_created += 1
                
                print(f"  ✅ {item_data['name']}: {adjusted_quantity} {item_data['unit']} × ${adjusted_cost} = ${item_total_estimated:.2f}")
        
        # Update project with budget totals
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {
                "estimated_budget": round(project_total_estimated, 2),
                "actual_cost": round(project_actual_cost, 2)
            }}
        )
        
        print(f"  💰 Project Budget: ${project_total_estimated:.2f} estimated, ${project_actual_cost:.2f} spent")
    
    print(f"\n🎉 Created {total_created} budget items for {min(len(projects), 3)} projects!")
    print("\n💡 Customer Features:")
    print("• Customers can now view project budgets")
    print("• See estimated costs vs actual spending")
    print("• Track budget progress and remaining funds")
    print("• View detailed cost breakdowns by category")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_sample_budgets())