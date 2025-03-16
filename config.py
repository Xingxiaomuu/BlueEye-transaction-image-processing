# config.py

import os
from datetime import datetime

# 配置参数
API_KEY = ""
API_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "Pro/OpenGVLab/InternVL2-8B"
IMAGE_FOLDER = r"C:\Users\Administrator\Desktop\Jupyter\BlueEye\Test\Test_0"
OUTPUT_FOLDER = r"C:\Users\Administrator\Desktop\Jupyter\BlueEye\Test"

# 生成输出 JSON 文件名
model_name_short = MODEL_NAME.split("/")[-1]
folder_name = os.path.basename(IMAGE_FOLDER)
timestamp = datetime.now().strftime("%Y-%m-%d")
json_namee = f"{model_name_short}_{folder_name}_{timestamp}.json"

# 提示信息
PROMPT = """请从图片中提取完整订单信息，包含以下中文字段：
- 交易状态
- 下单时间
- 订单编号
- 店铺名称
- 商品信息列表：商品名称、商品件数、商品价格、商品划线价、服务标签
- 金额信息：总价、实付款、运费、运费险
- 优惠信息：店铺优惠、跨店满减、红包、礼金、购物券、支付优惠
**严格要求：**  
1. **必须** 直接返回 **JSON 数组**，不要添加任何解释性文本。  
2. **仅输出 JSON**，不要加 markdown 代码块 ```json ```。
3. 缺失字段保持为空，不要填充默认值。
4. **请确保所有字段必须使用中文，不要包含英文或其他语言。**
5. 若图片中存在多个*，请忽略。"""