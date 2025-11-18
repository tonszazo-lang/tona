from flask import Flask, render_template, request, jsonify, send_from_directory
from config import Config
from models import db, Post, Video
import os
import openai

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

openai.api_key = Config.OPENAI_API_KEY

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "videos")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/get_posts", methods=["POST"])
def get_posts():
    section = request.json.get("section")
    posts = Post.query.filter_by(section=section).order_by(Post.created_at.desc()).all()
    return jsonify({"posts": [{"id": p.id, "text": p.content} for p in posts]})

@app.route("/api/add_post", methods=["POST"])
def add_post():
    data = request.json
    section = data.get("section")
    content = data.get("content")
    if not content:
        return jsonify({"status": "error", "message": "Content empty"})
    post = Post(section=section, content=content)
    db.session.add(post)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/api/get_videos", methods=["POST"])
def get_videos():
    section = request.json.get("section")
    videos = Video.query.filter_by(section=section).order_by(Video.uploaded_at.desc()).all()
    return jsonify({"videos": [{"id": v.id, "src": f"/static/videos/{v.filename}"} for v in videos]})

@app.route("/api/upload_video", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file part"})
    file = request.files["file"]
    section = request.form.get("section")
    if file.filename == "":
        return jsonify({"status": "error", "message": "No selected file"})
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    video = Video(section=section, filename=filename)
    db.session.add(video)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/api/ai/generate", methods=["POST"])
def generate_ai():
    section = request.json.get("section")
    prompt = f"اكتب محتوى نسائي جميل لقسم {section}"
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        text = response.choices[0].text.strip()
    except Exception as e:
        text = "💖 لم يصل رد من الخادم"
    return jsonify({"text": text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
