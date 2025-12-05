import os
import sys
from flask import Flask, render_template, send_from_directory, jsonify

# 1. 檢查並自動提示安裝套件
try:
    from docx import Document
except ImportError:
    print("❌ 錯誤：找不到必要套件。")
    print("請在終端機執行指令: pip install -r requirements.txt")
    sys.exit(1)

app = Flask(__name__)

# ================= 設定區域 =================
# 指向你的 Google Drive G 槽 (請確認 G: 槽已經掛載)
BASE_DIR = r"G:\我的雲端硬碟\情熱天堂 每日班表\情熱天堂班表"

ALLOWED_EXTENSIONS = {
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    'video': ['.mp4', '.mov', '.webm'],
    'text': ['.docx'] 
}

# ================= 路由邏輯 =================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/locations')
def get_locations():
    if not os.path.exists(BASE_DIR):
        print(f"⚠️ 找不到路徑: {BASE_DIR}")
        return jsonify([])
    dirs = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    return jsonify(dirs)

@app.route('/api/people/<location>')
def get_people(location):
    loc_path = os.path.join(BASE_DIR, location)
    if not os.path.exists(loc_path): return jsonify([])
    
    people_dirs = [d for d in os.listdir(loc_path) if os.path.isdir(os.path.join(loc_path, d))]
    people_data = []

    for p in people_dirs:
        p_path = os.path.join(loc_path, p)
        p_info = {'name': p, 'thumbnail': None, 'preview': '尚無文字簡介'}
        
        try:
            files = sorted(os.listdir(p_path))
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if not p_info['thumbnail'] and ext in ALLOWED_EXTENSIONS['image']:
                    p_info['thumbnail'] = f"/files/{location}/{p}/{f}"
                if p_info['preview'] == '尚無文字簡介' and f.lower().endswith('.docx'):
                    p_info['preview'] = extract_preview(os.path.join(p_path, f))
                if p_info['thumbnail'] and p_info['preview'] != '尚無文字簡介': break
        except Exception: pass
        people_data.append(p_info)
    return jsonify(people_data)

@app.route('/api/content/<location>/<person>')
def get_content(location, person):
    person_path = os.path.join(BASE_DIR, location, person)
    if not os.path.exists(person_path): return jsonify({'error': 'Not found'}), 404

    content = {'images': [], 'videos': [], 'text': {'preview': '', 'full': '', 'has_doc': False}}
    try:
        for file in os.listdir(person_path):
            ext = os.path.splitext(file)[1].lower()
            url = f"/files/{location}/{person}/{file}"
            if ext in ALLOWED_EXTENSIONS['image']:
                content['images'].append({'name': file, 'url': url})
            elif ext in ALLOWED_EXTENSIONS['video']:
                content['videos'].append({'name': file, 'url': url})
            elif ext in ALLOWED_EXTENSIONS['text']:
                text_data = read_full_docx(os.path.join(person_path, file))
                if text_data: content['text'] = text_data
    except Exception: pass
    return jsonify(content)

@app.route('/files/<location>/<person>/<filename>')
def serve_file(location, person, filename):
    return send_from_directory(os.path.join(BASE_DIR, location, person), filename)

# ================= 輔助功能 =================

def extract_preview(path):
    try:
        doc = Document(path)
        txt = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return '\n'.join(txt[:3]) if txt else '尚無文字簡介'
    except: return '預覽讀取失敗'

def read_full_docx(path):
    try:
        doc = Document(path)
        full = [p.text for p in doc.paragraphs if p.text.strip()]
        return {'full': '\n'.join(full), 'preview': '\n'.join(full[:5]), 'has_doc': True}
    except: return None

if __name__ == '__main__':
    print(f"🚀 系統啟動... 讀取路徑: {BASE_DIR}")
    app.run(debug=True, port=5000)