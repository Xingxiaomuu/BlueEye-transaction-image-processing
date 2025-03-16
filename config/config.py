# config.py

import os
from datetime import datetime

# 配置
API_KEY = ""                 # API_KEY不要修改
API_URL = "https://api.siliconflow.cn/v1"                                       # API_URL不要修改
MODEL_NAME = "Pro/OpenGVLab/InternVL2-8B"                                       # 模型名称
IMAGE_FOLDER = r"C:\Users\User\OneDrive\Desktop\ME\Notebook\Test\BlueEye"       # 图片文件夹路径 例如替换为/tmp/nfs/quick_other/quick3/ExtractingPictures/pic3 (多个文件夹需要部署多次)
OUTPUT_FOLDER = r"C:\Users\User\OneDrive\Desktop\ME\Notebook\Test\BlueEye"      # JSON输出路径
JSON_FOLDER = OUTPUT_FOLDER                                                     # JSON输入以及EXCEL保存路径
NUM_PRODUCT = 7                                                                 # 单个订单最大商品数量的翻译（1为单商品）
OUTPUT_PREFIX = "Orders"                                                        # 输出文件前缀

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

# 新增目录配置 ROOT_1_OPTIONS = ["A", "B"]
ROOT_2_OPTIONS = ["京东","淘宝","拼多多","抖音","快手"]
ROOT_3_OPTIONS = ["单商品"]

# 保留原有变量命名
model_name_short = MODEL_NAME.split("/")[-1]
timestamp = datetime.now().strftime("%Y-%m-%d")
tdays = 3 # 计算ROOT_0目录（当前日期-3天）