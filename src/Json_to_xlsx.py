import pandas as pd
import os
import json
from datetime import datetime
from collections.abc import MutableMapping
from config import NUM_PRODUCT, JSON_FOLDER, OUTPUT_PREFIX

# ================= 配置部分 =================
# JSON_FOLDER = r"C:\Users\Administrator\Desktop\Jupyter\BlueEye\Test"

# 中英文字段映射表（可根据需要扩展）
FIELD_MAPPING = {
    # 订单基本信息
    "transaction_status": "transaction_status",
    "交易状态": "transaction_status",
    "order_time": "order_time",
    "下单时间": "order_time",
    "支付时间": "order_time",
    "order_number": "order_number",
    "订单编号": "order_number",
    "store_name": "store_name",
    "店铺名称": "store_name",
    "shop_name": "store_name",
    
    # 商品信息
    "product_info": "product_list",
    "商品信息列表": "product_list",
    "product_name": "product_name",
    "商品名称": "product_name",
    "quantity": "quantity",
    "商品件数": "quantity",
    "price": "price",
    "total_price": "price",
    "商品价格": "price",
    "discount_price": "price",
    "unit_price": "original_price",
    "商品划线价": "original_price",
    "original_price": "original_price",
    
    # 金额信息
    "amount_info": "amount_details",
    "金额信息": "amount_details",
    "real_payment": "actual_payment",
    "实付款": "actual_payment",
    "final_total": "actual_payment",
    
    # 促销信息
    "运费": "shipping_fee",
    "shipping_fee": "shipping_fee",
    "运费险": "shipping_security",
    "店铺优惠": "shop_discount",
    "store_discount": "shop_discount",
    "跨店满减": "cross_shop_discount",
    "红包": "Red_Envelope",
    "礼金": "refund",
    "refund": "refund",
    "购物券": "Shopping_Coupon",
    "支付优惠": "Payment_Coupon",

    # 物流信息
    "收货地址": "shipping_address",
    "配送方式": "delivery_method",
    
    # 联系信息
    "contact": "contact_info",
    "customer_service": "customer_service",
    "support": "logistics_support",
    
    # 其他通用字段
    "图片名称": "image_name",
    "根目录": "root_dir",
    "电商平台": "platform",
    "订单类型": "order_type",
    "用户ID": "user_id",
    
    # 服务信息
    "order_services": "services",
    "breakage_return": "breakage_return",
    "refund_reimbursement": "refund_reimbursement",
    "late_delivery_compensation": "late_delivery_comp"
}
# 列名二次映射（处理展平后的字段）
COLUMN_MAPPING = {
    # 金额信息
    'amount_details_淘金币抵扣': 'amount_tao_coin_deduction',
    
    # 联系信息
    'contact_info_customer_service': 'customer_service',
    'contact_info_logistics_support': 'logistics_support',
    
    # 商品信息（动态生成）
    **{f'product_list_{i}_{field}': f'product_{i}_{en_field}'
       for i in range(NUM_PRODUCT)  # 支持最多2个商品
       for field, en_field in [
           ('original_price', 'original_price'),
           ('price', 'price'),
           ('product_name', 'name'),
           ('quantity', 'quantity'),
           ('service_label', 'service_label'),
           ('服务标签', 'service_label')  # 合并中文标签字段
       ]},
    
    # 服务信息
    'services_breakage_return': 'service_breakage_return',
    'services_late_delivery_comp': 'service_late_delivery',
    'services_refund_reimbursement': 'service_refund',
    
    # 交易信息
    '交易快照': 'transaction_snapshot',
    '付款时间': 'payment_time',
    '成交时间': 'completion_time',
    '支付宝交易号': 'alipay_id',
    
    # 操作类
    '再买一单': 'action_reorder',
    '创建时间': 'create_time',
    '删除订单': 'action_delete',
    '卖了换钱': 'action_sell',
    '申请售后': 'action_after_sale',
    
    # 物流信息
    '发货时间': 'ship_time',
    '收货信息': 'delivery_info',
    
    # 促销信息
    '天猫积分': 'tmall_points',
    '优惠信息_cross_shop_discount': 'discount_cross_store',
    '优惠信息_payment_coupon': 'coupon_payment',
    '优惠信息_red_envelope': 'coupon_red_envelope',
    '优惠信息_refund': 'discount_refund',
    '优惠信息_shop_discount': 'discount_store',
    '优惠信息_shopping_coupon': 'coupon_shopping',
    
    # 赠品信息
    '赠品_赠品名称': 'gift_name',
    '赠品_赠品数量': 'gift_quantity',
    
    # 其他字段保留直译
    'promotion_info': 'promotion_info',
    'promotion_info_cashback': 'promotion_cashback',
    'promotion_info_shop_discount': 'promotion_store_discount'
}
# ================= 核心函数 =================
def translate_keys(data, mapping):
    """递归翻译字典键名"""
    if isinstance(data, dict):
        return {mapping.get(k, k): translate_keys(v, mapping) for k, v in data.items()}
    elif isinstance(data, list):
        return [translate_keys(item, mapping) for item in data]
    return data

def flatten_nested_data(data, parent_key='', sep='_', index_suffix=True):
    """
    递归展平嵌套数据结构
    :param data: 输入数据（dict/list）
    :param parent_key: 父级键前缀
    :param sep: 分隔符
    :param index_suffix: 是否为列表元素添加索引后缀
    :return: 展平后的字典
    """
    items = {}
    
    def process_item(key, value):
        # 处理字典类型
        if isinstance(value, MutableMapping):
            for k, v in value.items():
                new_key = f"{key}{sep}{k}" if key else k
                process_item(new_key, v)
        # 处理列表类型
        elif isinstance(value, list):
            if len(value) == 0:
                items[key] = None
            else:
                for idx, item in enumerate(value):
                    if index_suffix:
                        new_key = f"{key}{sep}{idx}"
                    else:
                        new_key = key
                    # 递归处理列表元素
                    if isinstance(item, (MutableMapping, list)):
                        process_item(new_key, item)
                    else:
                        # 合并简单类型列表为字符串
                        if idx == 0:
                            items[key] = str(item)
                        else:
                            items[key] += f"; {item}"
        # 处理简单类型
        else:
            items[key] = value

    process_item(parent_key, data)
    return items

def process_products(order_data, sep='_'):
    """特殊处理商品信息展开"""
    processed = []
    
    # 获取商品列表（兼容多种格式）
    products = order_data.get("product_list", [])
    if isinstance(products, str):
        try:
            products = json.loads(products.replace("'", "\""))
        except:
            products = []
    
    # 没有商品时保留订单主信息
    if not products:
        processed.append(order_data)
        return processed
    
    # 展开每个商品信息
    for idx, product in enumerate(products):
        # 深拷贝原始数据
        merged = order_data.copy()
        
        # 展平商品信息并添加前缀
        flat_product = flatten_nested_data(
            product, 
            parent_key=f"product{sep}{idx}" if idx > 0 else "product",
            index_suffix=False
        )
        
        # 合并数据并清理原始字段
        merged.update(flat_product)
        merged.pop("product_list", None)
        processed.append(merged)
    
    return processed

# ================= 主流程 =================
if __name__ == "__main__":
    # 1. 准备文件路径
    target_date = datetime.now().strftime("%Y-%m-%d")
    input_filename = f"InternVL2-8B_{target_date}.json"
    input_path = os.path.join(JSON_FOLDER, input_filename)
    output_filename = f"{OUTPUT_PREFIX}_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    output_path = os.path.join(JSON_FOLDER, output_filename)

    # 2. 加载并处理数据
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"文件加载失败: {str(e)}")
        exit()

    # 3. 数据预处理流程
    all_records = []
    for order in raw_data:
        try:
            # 步骤1: 字段翻译
            translated = translate_keys(order, FIELD_MAPPING)
            
            # 步骤2: 展平嵌套数据
            flattened = flatten_nested_data(translated)
            
            # 步骤3: 处理商品信息展开
            processed_orders = process_products(flattened)
            
            all_records.extend(processed_orders)
        except Exception as e:
            print(f"订单处理失败: {str(e)}")
            continue

    # 4. 创建数据框并保存
    if all_records:
        df = pd.DataFrame(all_records)
        
        # 列名处理流程优化
        # 步骤1: 统一格式
        df.columns = [
            col.replace(' ', '_')
               .replace('/', '_')
               .lower()
            for col in df.columns
        ]
        
        # 步骤2: 应用列名映射
        df = df.rename(columns=lambda x: COLUMN_MAPPING.get(x, x))
        
        # 步骤3: 合并重复字段（如中英文标签）
        for i in range(NUM_PRODUCT):
            cn_col = f'product_{i}_service_label'
            en_col = f'product_{i}_service_tag'
            if en_col in df.columns:
                df[cn_col] = df[cn_col].fillna(df[en_col])
                df = df.drop(columns=[en_col])
        
        # 步骤4: 清理空列
        df = df.dropna(axis=1, how='all')
        
        # 定义推荐列顺序
        preferred_columns = [
            # 基础信息
            'order_time', 'platform', 'order_number',
            'store_name', 'transaction_status', 'user_id',
            
            # 商品信息
            *[f'product_{i}_{field}' 
              for i in range(NUM_PRODUCT) 
              for field in ['name', 'quantity', 'price', 'original_price']],
            
            # 金额信息
            'amount_actual_payment', 'amount_tao_coin_deduction',
            
            # 物流信息
            'shipping_address', 'delivery_method', 'ship_time',
            
            # 其他
            'image_name', 'root_dir'
        ]
        
        # 生成最终列顺序
        existing_columns = [col for col in preferred_columns if col in df.columns]
        other_columns = sorted(list(set(df.columns) - set(existing_columns)))
        final_columns = existing_columns + other_columns
        
        # 保存结果
        df[final_columns].to_excel(output_path, index=False)
        print(f"成功导出 {len(df)} 条记录到: {output_path}")
    else:
        print("没有有效数据需要导出")
