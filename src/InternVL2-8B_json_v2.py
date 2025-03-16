import os
import re
import json
import base64
from datetime import datetime, timedelta
from openai import OpenAI
from tqdm import tqdm
from config import API_KEY, API_URL, MODEL_NAME, IMAGE_FOLDER, OUTPUT_FOLDER, PROMPT, ROOT_2_OPTIONS, ROOT_3_OPTIONS, model_name_short, timestamp, tdays

def get_root0_folder():    
    target_date = datetime.now() - timedelta(days=tdays)
    return target_date.strftime("%Y%m%d")

def process_single_image(image_path, path_metadata, all_data):
    """修改后的单图片处理函数"""
    try:
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
        
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

        raw_data = response.choices[0].message.content
        data = parse_response(raw_data,image_path)
        # print(data)
        if data:
            orders = data if isinstance(data, list) else [data]
            for order in orders:
                order.update({
                    "图片名称": os.path.basename(image_path),
                    "根目录": path_metadata["root0"],
                    "电商平台": path_metadata["root2"],
                    "订单类型": path_metadata["root3"],
                    "用户ID": path_metadata["shop_id"]
                })
            all_data.extend(orders)
            
    except Exception as e:
        print(f"❌ 处理失败 {image_path}: {str(e)}")

def traverse_directory_structure():
    """更新后的目录遍历逻辑"""
    all_data = []
    root0_name = get_root0_folder()
    base_path = os.path.join(IMAGE_FOLDER, root0_name)
    
    # 校验根目录0
    if not os.path.exists(base_path):
        print(f"⚠️ 无 {root0_name} 数据！请检查目录结构。")
        return all_data

    # 校验平台目录
    existing_platforms = set(os.listdir(base_path))
    invalid_platforms = existing_platforms - set(ROOT_2_OPTIONS)
    for platform in invalid_platforms:
        print("⚠️ 有其它平台数据！请检查目录结构。")

    # 校验订单类型目录
    for root2 in ROOT_2_OPTIONS:
        platform_path = os.path.join(base_path, root2)
        if not os.path.exists(platform_path):
            continue
            
        existing_types = set(os.listdir(platform_path))
        invalid_types = existing_types - set(ROOT_3_OPTIONS)
        for order_type in invalid_types:
            print(f"⚠️ {platform_path}-无单商品数据！请检查目录结构。")    
    
    
    # 预计算总图片数
    total_images = 0
    for root2 in ROOT_2_OPTIONS:
        for root3 in ROOT_3_OPTIONS:
            current_path = os.path.join(base_path, root2, root3)
            if os.path.exists(current_path):
                for shop_id in os.listdir(current_path):
                    shop_path = os.path.join(current_path, shop_id)
                    if os.path.isdir(shop_path) and shop_id.isdigit():
                        total_images += len([
                            f for f in os.listdir(shop_path) 
                            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
                        ])
    
    # 带进度条处理
    with tqdm(total=total_images, desc="🚀 处理进度", unit="img") as pbar:
        for root2 in ROOT_2_OPTIONS:
            for root3 in ROOT_3_OPTIONS:
                current_path = os.path.join(base_path, root2, root3)
                if not os.path.exists(current_path):
                    continue
                
                for shop_id in os.listdir(current_path):
                    shop_path = os.path.join(current_path, shop_id)
                    if not (os.path.isdir(shop_path) and shop_id.isdigit()):
                        continue
                    
                    # 构建路径元数据
                    path_meta = {
                        "root0": root0_name,
                        "root2": root2,
                        "root3": root3,
                        "shop_id": shop_id
                    }
                    
                    # 处理店铺图片
                    for img_file in os.listdir(shop_path):
                        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                            img_path = os.path.join(shop_path, img_file)
                            process_single_image(img_path, path_meta, all_data)
                            pbar.update(1)
    
    return all_data

# 保留原有工具函数不变
def ensure_output_dir():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def save_json(data, filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 已保存: {filename}")

def parse_response(raw_data,image_path):
    try:
        if not raw_data.strip():
            return None
        match = re.search(r'```json\s*(.*?)\s*```', raw_data, re.DOTALL)
        if match:
            raw_data = match.group(1).strip()
        return json.loads(raw_data)
    except json.JSONDecodeError as e:
        print(f"❌ {image_path} 解析JSON失败: {str(e)}")
        return None
    
def save_results(data):
    """修改后的保存函数"""
    ensure_output_dir()
    if data:
        # 保留原有命名规则
        json_name = f"{model_name_short}_{timestamp}.json"
        save_json(data, json_name)
    else:
        print("⚠️ 没有提取到有效数据")

if __name__ == "__main__":
    # 保留原有主逻辑结构
    extracted_data = traverse_directory_structure()
    save_results(extracted_data)