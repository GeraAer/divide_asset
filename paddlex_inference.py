from paddlex import create_model
import os
import cv2
import numpy as np

def load_model(model_dir):
    """
    加载 PaddleX 的实例分割模型。
    """
    print(f"Loading model from {model_dir}...")
    model = create_model(model_dir)
    print("Model loaded successfully.")
    return model

def predict_image(image_path, model, output_folder):
    """
    对输入图片进行实例分割，并保存结果
    """
    print(f"Running prediction on image: {image_path}")
    results = list(model.predict(image_path))

    if not results:
        raise ValueError("No segmentation results returned from the model.")

    output_files = []
    for idx, result in enumerate(results):
        result_img_path = os.path.join(output_folder, f"result_{idx}.png")
        result.save_to_img(result_img_path)
        output_files.append(result_img_path)

    return output_files

def process_instances_with_masks(image_path, model, output_folder):
    """
    处理图片，生成整张透明背景的抠图图片，以及每个实例独立的透明背景图片。
    :param image_path: 输入图片路径
    :param model: 已加载的 PaddleX 模型
    :param output_folder: 保存结果的目录
    :return: 包含整张透明背景图片路径和每个实例独立图片路径的字典
    """
    print(f"Running prediction on image: {image_path}")
    results = list(model.predict(image_path))

    if not results:
        raise ValueError("No segmentation results returned from the model.")

    # 打印结果结构
    print("Results structure:")
    for idx, result in enumerate(results):
        print(f"Result {idx}: {result}")

    # 读取原始图片
    image = cv2.imread(image_path)
    h, w, _ = image.shape  # 原图尺寸

    # 创建整张透明背景图片
    transparent_full = np.zeros((h, w, 4), dtype=np.uint8)
    for c in range(3):  # RGB 通道
        transparent_full[:, :, c] = image[:, :, c]

    # 遍历所有掩码，将非实例部分透明化
    masks = results[0]["masks"]
    combined_mask = np.zeros((h, w), dtype=np.uint8)
    for mask in masks:
        resized_mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
        combined_mask = np.maximum(combined_mask, resized_mask)

    # 将非实例部分设置为透明
    transparent_full[:, :, 3] = combined_mask * 255

    # 保存整张透明背景图片
    transparent_full_path = os.path.join(output_folder, "transparent_full.png")
    cv2.imwrite(transparent_full_path, transparent_full)

    # 生成每个实例的独立透明背景图片
    transparent_files = []
    for idx, (bbox, mask) in enumerate(zip(results[0]["boxes"], results[0]["masks"])):
        # 获取边界框坐标
        x_min, y_min, x_max, y_max = map(int, bbox["coordinate"])

        # 根据边界框裁剪原图
        cropped_image = image[y_min:y_max, x_min:x_max]
        cropped_mask = cv2.resize(mask, (x_max - x_min, y_max - y_min), interpolation=cv2.INTER_NEAREST)

        # 创建透明背景图片
        cropped_instance = np.zeros((y_max - y_min, x_max - x_min, 4), dtype=np.uint8)
        for c in range(3):  # RGB 通道
            cropped_instance[:, :, c] = cropped_image[:, :, c] * cropped_mask
        cropped_instance[:, :, 3] = cropped_mask * 255

        # 保存每个实例的透明背景图片
        instance_path = os.path.join(output_folder, f"instance_{idx}.png")
        cv2.imwrite(instance_path, cropped_instance)
        transparent_files.append(instance_path)

    print(f"Transparent full image saved: {transparent_full_path}")
    print(f"Transparent instance images saved: {transparent_files}")

    return {
        "transparent_full": transparent_full_path,
        "instances": transparent_files
    }

