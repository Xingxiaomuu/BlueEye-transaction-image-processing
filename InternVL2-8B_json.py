# main.py

import os
import re
import json
import base64
from datetime import datetime
from openai import OpenAI
from tqdm import tqdm
from config import API_KEY, API_URL, MODEL_NAME, IMAGE_FOLDER, OUTPUT_FOLDER, json_namee, PROMPT

def ensure_output_dir():
    """确保输出目录存在"""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def save_json(data, filename):
    """保存 JSON 文件"""
    path = os.path.join(OUTPUT_FOLDER, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 已保存: {filename}")

def parse_response(raw_data):
    """解析 API 返回的 JSON"""
    try:
        if not raw_data or not raw_data.strip():
            print("❌ API 返回数据为空")
            return None
        
        # 可能存在 ```json ``` 代码块，去掉它
        match = re.search(r'```json\s*(.*?)\s*```', raw_data, re.DOTALL)
        if match:
            raw_data = match.group(1)  # 取出 JSON 内容
        
        # 去除可能的前后空格和换行符
        raw_data = raw_data.strip()
        
        # 解析 JSON
        return json.loads(raw_data)
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {str(e)}")
        return None

def process_single_image(img_file, all_data):
    """处理单张图片"""
    image_path = os.path.join(IMAGE_FOLDER, img_file)
    if not os.path.exists(image_path):
        print(f"❌ 图片不存在: {img_file}")
        return

    try:
        # 读取图片并编码
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        # 调用 API
        client = OpenAI(api_key=API_KEY, base_url=API_URL)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }],
            max_tokens=1024,
            temperature=0.7,
            top_p=0.7,
            frequency_penalty=0.0
        )

        # 获取 API 返回的 JSON
        raw_data = response.choices[0].message.content
        

        # 解析 JSON
        data = parse_response(raw_data)
        if not data:
            print("❌ API 返回回答：", raw_data)
            print(f"❌ 解析失败，跳过 {img_file}")
            return

        # 统一转换为列表处理（适配单条数据和多条数据）
        orders = data if isinstance(data, list) else [data]
        
        # 为每个订单添加图片名称
        for order in orders:
            # 手动加入订单信息字段
            order["图片名称"] = img_file
            # 确保订单信息字段存在
            #if "订单信息" not in order:
                #order["订单信息"] = {}
            #order["订单信息"]["图片名称"] = img_file
        
        # 将处理后的订单添加到总列表
        all_data.extend(orders)
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")

def process_batch_images():
    """批量处理所有图片"""
    ensure_output_dir()
    all_data = []  # 用于存储所有的结果
    
    # 获取所有图片文件列表
    img_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # 新增进度条（核心修改部分）
    with tqdm(total=len(img_files), desc="🔄 处理图片进度", unit="image") as pbar:
        for img_file in img_files:
            process_single_image(img_file, all_data)
            pbar.update(1)  # 更新进度条
            
    if all_data:
        save_json(all_data, json_namee)
    else:
        print("❌ 没有有效的订单数据，未保存文件。")

if __name__ == "__main__":
    process_batch_images()