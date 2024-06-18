from flask import Blueprint, render_template, request, jsonify, url_for
import os
import json
import re

# 创建一个Blueprint实例
main = Blueprint('main', __name__)

@main.route('/')
def index():
    print("----------Current Working Directory:", os.getcwd())
    # 假设HTML和PDF文件存放在static/data目录下
    html_directory = os.path.join('data', 'htmls')
    files = os.listdir(html_directory)
    files = [file for file in files if file.endswith('.html')]
    return render_template('index.html', files=files)

@main.route('/review/<filename>')
def review(filename):
    # 根据文件名构造HTML和PDF的路径
    html_file = f"data/htmls/{filename}"
    pdf_file = f"data/pdfs/{filename.replace('html', 'pdf')}"
    page_number = '1'  # 这里简化处理，实际使用时可能需要更复杂的逻辑来确定页码
    return render_template('review.html', html_file=html_file, pdf_file=pdf_file, page_number=page_number)

@main.route('/mark/<action>', methods=['POST'])
def mark(action):
    data = request.get_json()
    filename = data['filename']
    # 这里可以添加将标记结果保存到数据库或文件的逻辑
    response = {
        'status': 'success',
        'action': action,
        'filename': filename
    }
    return jsonify(response)

@main.route('/load_file', methods=['POST'])
def load_file():
    data = request.get_json()
    print("Request received:", data)  # 输出接收到的数据

    filename = data['filename']
    # 使用正则表达式匹配页面号
    match = re.search(r'_p(\d+)f\d+\.html$', filename)
    page_number = match.group(1) if match else '1'  # 如果没有匹配到，默认为第一页

    # 构造 HTML 和 PDF 的路径
    html_path = url_for('static', filename=f'data/htmls/{filename}')
    # 假设 PDF 文件名是基于 HTML 文件名的第一个下划线前的部分
    pdf_base_filename = filename.split('_')[0]
    pdf_path = url_for('static', filename=f'data/pdfs/{pdf_base_filename}_datasheet.pdf') + f'#page={page_number}'

    return jsonify({'html_path': html_path, 'pdf_path': pdf_path})

