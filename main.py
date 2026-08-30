from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI(title="AI Smart Residential Platform")

# Frontend & Backend தொடர்புகொள்ள CORS அனுமதி
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "smart_residential.db"

# Database & Table Setup
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            bedrooms INT,
            bathrooms INT,
            parking TEXT,
            balcony TEXT,
            garden TEXT,
            pooja TEXT,
            study TEXT,
            status TEXT DEFAULT 'Completed',
            summary TEXT,
            features TEXT,
            image_2d TEXT,
            image_3d TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Input Structure for Room Selection
class RoomSelectionRequest(BaseModel):
    project_name: Optional[str] = "Modern Villa"
    bedroom: Optional[int] = 2
    bathrooms: Optional[int] = 2
    parking: Optional[str] = "Yes"
    balcony: Optional[str] = "Yes"
    garden: Optional[str] = "Yes"
    pooja: Optional[str] = "Yes"
    study: Optional[str] = "Yes"

# 1. 🏠 Room Selection Backend API (POST)
@app.post("/api/select-rooms")
def select_rooms(data: RoomSelectionRequest):
    try:
        summary_text = f"{data.bedroom} BHK House ({data.bedroom} Bedrooms, {data.bathrooms} Bathrooms)"
        
        features = []
        if data.parking == "Yes": features.append("Parking")
        if data.balcony == "Yes": features.append("Balcony")
        if data.garden == "Yes": features.append("Garden")
        if data.pooja == "Yes": features.append("Pooja Room")
        if data.study == "Yes": features.append("Study Room")
        
        feature_text = ", ".join(features) if features else "Standard Features"
        blueprint_2d = "https://i.ibb.co/L8y6b7T/hd-blueprint-plan.jpg"
        blueprint_3d = "https://i.ibb.co/L8y6b7T/hd-blueprint-plan.jpg"

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (project_name, bedrooms, bathrooms, parking, balcony, garden, pooja, study, status, summary, features, image_2d, image_3d)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Completed', ?, ?, ?, ?)
        ''', (data.project_name, data.bedroom, data.bathrooms, data.parking, data.balcony, data.garden, data.pooja, data.study, summary_text, feature_text, blueprint_2d, blueprint_3d))
        
        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": "Blueprint Generated & Saved Successfully!",
            "data": {
                "project_name": data.project_name,
                "summary": summary_text,
                "features": feature_text,
                "image_2d": blueprint_2d,
                "image_3d": blueprint_3d
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 2. 📂 My Projects Page Backend API (GET)
@app.get("/api/my-projects")
def get_my_projects():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        completed = []
        in_progress = []

        for row in rows:
            p = {
                "id": row["id"],
                "project_name": row["project_name"],
                "status": row["status"],
                "summary": row["summary"],
                "features": row["features"],
                "image_2d": row["image_2d"],
                "image_3d": row["image_3d"]
            }
            if row["status"] == "Completed":
                completed.append(p)
            else:
                in_progress.append(p)

        return {
            "status": "success",
            "completed": completed,
            "in_progress": in_progress
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 3. 🖼 Saved Blueprints Backend API (GET)
@app.get("/api/get-saved-blueprints")
def get_saved_blueprints():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, project_name, summary, features, image_2d, image_3d FROM projects ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        projects = []
        for row in rows:
            projects.append({
                "id": row[0],
                "project_name": row[1],
                "summary": row[2],
                "features": row[3],
                "image_2d": row[4],
                "image_3d": row[5]
            })
        return {"status": "success", "data": projects}
    except Exception as e:
        return {"status": "error", "message": str(e), "data": []}

# 4. 🗑 Delete Project Backend API (DELETE)
@app.delete("/api/delete-project/{project_id}")
def delete_project(project_id: int):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Project deleted successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
