from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import requests
import io
import urllib.parse
import random

app = Flask(__name__)
CORS(app)

# Database Setup - v7
def init_db():
    conn = sqlite3.connect('blueprints_v7.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_blueprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary TEXT NOT NULL,
            features TEXT NOT NULL,
            image_2d TEXT NOT NULL,
            image_3d TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Precision Architectural Blueprint Active!"})

@app.route('/api/select-rooms', methods=['POST'])
def select_rooms():
    data = request.get_json() or {}
    
    bedrooms = int(data.get('bedroom') or data.get('bedrooms') or 1)
    bathrooms = data.get('bathrooms') or data.get('bathroom') or 1
    hall = data.get('hall', 1)
    kitchen = data.get('kitchen', 1)
    
    parking = data.get('parking', 'No')
    balcony = data.get('balcony', 'No')
    garden = data.get('garden', 'No')
    pooja_room = data.get('pooja', 'No')
    study_room = data.get('study', 'No')

    summary = f"{bedrooms} Bedrooms, {hall} Hall, {kitchen} Kitchen, {bathrooms} Bathrooms"
    
    selected_features = []
    if parking == 'Yes': selected_features.append("Car Parking Garage")
    if balcony == 'Yes': selected_features.append("Balcony Terrace")
    if garden == 'Yes': selected_features.append("Front Lawn Garden")
    if pooja_room == 'Yes': selected_features.append("Pooja Prayer Room")
    if study_room == 'Yes': selected_features.append("Study Room")

    feature_text = ", ".join(selected_features) if selected_features else "Standard Layout"

    # Strict architectural prompts with labeled layout structure
    prompt_2d = (
        f"architectural 2d floor plan schematic layout grid, top-down cad blueprint, white background, black walls, "
        f"labeled rooms: {bedrooms} Bedroom, Living Room, Kitchen, Bathrooms, {feature_text}. "
        f"clear room text labels, doors, wall measurements, architectural blueprint floorplan, clean high resolution 2d drawing"
    )
    
    prompt_3d = (
        f"3d architectural cutaway floor plan render, top view isometric house layout, "
        f"full modern home showing {bedrooms} Bedrooms, Living Room, Kitchen, Bathrooms, and separate zones for {feature_text}. "
        f"labeled architectural visualization, detailed interior layout, car parked in garage, green garden, bright lighting, high quality 8k"
    )

    encoded_2d = urllib.parse.quote(prompt_2d)
    encoded_3d = urllib.parse.quote(prompt_3d)

    seed_2d = random.randint(100000, 999999)
    seed_3d = random.randint(100000, 999999)

    # Pollinations AI high clarity URL
    img_2d = f"https://image.pollinations.ai/prompt/{encoded_2d}?width=1200&height=900&seed={seed_2d}&nologo=true"
    img_3d = f"https://image.pollinations.ai/prompt/{encoded_3d}?width=1200&height=900&seed={seed_3d}&nologo=true"

    try:
        conn = sqlite3.connect('blueprints_v7.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO saved_blueprints (summary, features, image_2d, image_3d) VALUES (?, ?, ?, ?)',
            (summary, feature_text, img_2d, img_3d)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("Database Error:", e)

    return jsonify({
        "status": "success",
        "message": "Blueprint Generated Successfully!",
        "data": {
            "summary": summary,
            "features": feature_text,
            "image_2d": img_2d,
            "image_3d": img_3d
        }
    })

@app.route('/api/get-saved-blueprints', methods=['GET'])
def get_saved_blueprints():
    try:
        conn = sqlite3.connect('blueprints_v7.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, summary, features, image_2d, image_3d, created_at FROM saved_blueprints ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()

        saved_list = []
        for row in rows:
            saved_list.append({
                "id": row[0],
                "summary": row[1],
                "features": row[2],
                "image_2d": row[3],
                "image_3d": row[4],
                "created_at": row[5]
            })

        return jsonify({"status": "success", "data": saved_list})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/download-image', methods=['GET'])
def download_image():
    img_url = request.args.get('url')
    filename = request.args.get('filename', 'ai_blueprint.jpg')
    if not img_url:
        return "Image URL missing", 400
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(img_url, headers=headers, timeout=25)
        return send_file(
            io.BytesIO(response.content),
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)