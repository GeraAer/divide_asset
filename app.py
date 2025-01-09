from flask import Flask, request, jsonify, render_template
import os
import uuid  # 用于生成唯一文件名
from paddlex_inference import load_model, predict_image, process_instances_with_masks  # 自定义推理逻辑

# 创建 Flask 应用实例
app = Flask(__name__)

# 定义图片上传和结果保存的目录
UPLOAD_FOLDER = 'uploads'  # 上传图片目录
OUTPUT_FOLDER = 'static/split_images'  # 分割结果目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 加载 PaddleX 模型
print("Loading PaddleX model...")
model = load_model(model_dir="./models/Mask-RT-DETR-H")  # 确保路径正确
print("Model loaded successfully.")

# 主页面路由，返回前端页面
@app.route('/')
def index():
    """
    加载前端 HTML 页面。
    """
    return render_template('index.html')  # templates 目录下的 index.html 页面

# 上传图片并调用实例分割
@app.route('/process_image', methods=['POST'])
def process_image_route():
    """
    上传图片并调用 PaddleX 模型进行实例分割。
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image part'})

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})

    # 保存上传图片
    filename = str(uuid.uuid4()) + ".png"  # 为图片生成唯一文件名
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        # 调用分割逻辑
        output_files = predict_image(file_path, model, OUTPUT_FOLDER)
        return jsonify({'success': True, 'files': output_files})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# 上传图片并生成透明素材图片
@app.route('/process_image_with_masks', methods=['POST'])
def process_image_with_masks_route():
    """
    上传图片并调用 PaddleX 模型生成透明背景图片和每个实例的独立透明背景图片。
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image part'})

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})

    # 保存上传图片
    filename = str(uuid.uuid4()) + ".png"  # 为图片生成唯一文件名
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        # 调用生成透明背景和实例图片的逻辑
        results = process_instances_with_masks(file_path, model, OUTPUT_FOLDER)
        return jsonify({'success': True, 'transparent_full': results["transparent_full"], 'instances': results["instances"]})
    except Exception as e:
        print(f"Error during processing: {e}")
        return jsonify({'success': False, 'message': str(e)})

# 启动 Flask 应用
if __name__ == '__main__':
    app.run(debug=True)
