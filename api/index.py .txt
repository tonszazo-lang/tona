from wsgi import application
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os

# إعداد التطبيق
app = application

# مجلد التخزين المؤقت
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Endpoint لرفع الملفات
@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    download_url = f"/files/{filename}"
    
    return jsonify({
        "message": "File uploaded successfully",
        "filename": filename,
        "download_url": download_url
    })

# Endpoint لتحميل الملفات بعد رفعها
@app.route("/files/<filename>", methods=["GET"])
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Endpoint للذكاء الاصطناعي
@app.route("/ai", methods=["POST"])
def ai_response():
    import openai
    prompt = request.json.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        answer = response['choices'][0]['message']['content']
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# وظيفة handler الخاصة بـ Vercel
def handler(event, context):
    return app(event, context)
