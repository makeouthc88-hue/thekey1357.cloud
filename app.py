@app.route('/api/content/<location>/<person>')
def get_content(location, person):
    person_path = os.path.join(BASE_DIR, location, person)
    
    # 🚨 偵錯日誌強化：如果路徑不存在，將實際尋找的路徑打印到伺服器日誌中
    if not os.path.exists(person_path):
        print(f"🚨 CONTENT FOLDER NOT FOUND: Trying path {person_path}")
        return jsonify({'text': {'preview': '尚無文字簡介', 'full': '尚無文字簡介', 'has_doc': False}, 'images': [], 'videos': []})

    content = {'images': [], 'videos': [], 'text': {'preview': '尚無文字簡介', 'full': '尚無文字簡介', 'has_doc': False}}
    try:
        for file in os.listdir(person_path):
            ext = os.path.splitext(file)[1].lower()
            url = f"/files/{location}/{person}/{file}"
            
            if ext in ALLOWED_EXTENSIONS['image']:
                content['images'].append({'name': file, 'url': url})
            elif ext in ALLOWED_EXTENSIONS['video']:
                content['videos'].append({'name': file, 'url': url})
            elif ext in ALLOWED_EXTENSIONS['text']:
                # 讀取 .txt 檔案
                content['text'] = read_full_docx(os.path.join(person_path, file))
    except Exception as e: 
        print(f"🚨 Error reading content in {person_path}: {e}")
        pass
    return jsonify(content)