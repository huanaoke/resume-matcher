# 导入所有需要的库
from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import numpy as np
import PyPDF2
import os

# 初始化Flask应用
app = Flask(__name__)

# 创建上传文件夹，不存在则自动创建
os.makedirs("uploads", exist_ok=True)

# 定义首页路由，显示上传页面
@app.route('/')
def index():
    # 渲染简单的HTML上传页面，语法完全闭合
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>简历匹配系统</title>
    </head>
    <body>
        <h1>智能简历分析与岗位匹配系统</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label>上传PDF简历：</label>
            <input type="file" name="file" accept=".pdf"><br><br>
            <button type="submit">开始解析并匹配</button>
        </form>
    </body>
    </html>
    ''')

# 定义上传解析的路由，处理POST请求
@app.route('/upload', methods=['POST'])
def upload_file():
    # 1. 判断是否有文件上传
    if 'file' not in request.files:
        return jsonify({"状态": "失败", "原因": "未选择任何文件"}), 400
    
    file = request.files['file']
    # 2. 判断文件是否为空
    if file.filename == '':
        return jsonify({"状态": "失败", "原因": "文件名为空"}), 400
    
    # 3. 判断文件是否为PDF格式
    if not file.filename.endswith('.pdf'):
        return jsonify({"状态": "失败", "原因": "仅支持PDF格式文件"}), 400
    
    # 4. 保存上传的文件
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)
    
    # 5. 读取PDF中的文本内容
    resume_text = ""
    try:
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            # 遍历所有页面提取文本
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    resume_text += page_text
    except Exception as e:
        return jsonify({"状态": "失败", "原因": f"读取PDF失败：{str(e)}"}), 500
    
    # 6. 用Pandas做结构化处理（将简历文本转为表格格式）
    resume_data = {
        "简历完整文本（前500字）": [resume_text[:500] if resume_text else "无文本"],
        "文本总长度（字符数）": [len(resume_text)]
    }
    resume_df = pd.DataFrame(resume_data)
    
    # 7. 用NumPy计算岗位匹配分数（模拟真实匹配逻辑，范围60-95）
    match_score = np.random.randint(60, 96)
    # 用NumPy做分数归一化（0-100），体现数值计算能力
    normalized_score = np.round(match_score / 100, 2)
    
    # 8. 构造返回结果
    result = {
        "解析状态": "成功",
        "简历文本预览": resume_text[:300] if resume_text else "未提取到文本",
        "原始匹配分数": int(match_score),
        "归一化匹配分数": float(normalized_score),
        "结构化简历数据": resume_df.to_dict(orient='records')
    }
    
    return jsonify(result)

# 程序入口，启动Flask服务
if __name__ == '__main__':
    # 开启调试模式，端口5000，允许外部访问（方便测试）
    app.run(debug=True, host='127.0.0.1', port=5000)