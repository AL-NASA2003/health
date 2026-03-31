from flask import request, jsonify
from loguru import logger

def validate_params(required_params):
    """验证请求参数是否完整
    :param required_params: list 必需参数列表
    :return: tuple (bool, dict) 验证结果，参数字典
    """
    try:
        # 获取JSON参数
        params = request.get_json() or {}
        missing_params = [p for p in required_params if p not in params]
        
        if missing_params:
            logger.warning(f"缺少参数：{missing_params}")
            return False, {"code": 400, "msg": f"缺少参数：{','.join(missing_params)}"}
        
        return True, params
    except Exception as e:
        logger.error(f"参数验证失败：{str(e)}")
        return False, {"code": 400, "msg": "参数格式错误"}

def format_response(code=0, msg="success", data=None):
    """统一响应格式
    :param code: int 状态码，0表示成功
    :param msg: str 提示信息
    :param data: any 数据
    :return: json 响应结果
    """
    response = {
        "code": code,
        "msg": msg,
        "data": data or {}
    }
    return jsonify(response)

def calculate_nutrition(ingredient, weight):
    """根据食用量计算营养成分
    :param ingredient: dict 食材信息
    :param weight: float 食用量(g)
    :return: dict 营养成分
    """
    rate = weight / 100
    return {
        "calorie": round(ingredient["calorie"] * rate, 1),
        "protein": round(ingredient["protein"] * rate, 1),
        "carb": round(ingredient["carb"] * rate, 1),
        "fat": round(ingredient["fat"] * rate, 1)
    }