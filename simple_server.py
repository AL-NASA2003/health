from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
import hashlib

app = Flask(__name__)
CORS(app)

SECRET_KEY = "health_food_system_2026"

def format_response(code=200, msg="success", data=None):
    return jsonify({"code": code, "msg": msg, "data": data})

def verify_token(token):
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        if token.startswith("mock_token_"):
            return {"user_id": 1}
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        return None

def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

mock_recipes = [
    {"id": 1, "name": "低脂鸡胸肉沙拉", "calorie": 280, "protein": 32, "carb": 15, "fat": 8, "flavor": "清淡", "cook_step": "1. 鸡胸肉切块腌制\n2. 煎至金黄\n3. 混合蔬菜"},
    {"id": 2, "name": "清蒸鲈鱼", "calorie": 180, "protein": 28, "carb": 5, "fat": 6, "flavor": "清淡", "cook_step": "1. 鲈鱼洗净\n2. 蒸10分钟\n3. 淋豉油"},
    {"id": 3, "name": "燕麦蓝莓粥", "calorie": 220, "protein": 8, "carb": 42, "fat": 4, "flavor": "清淡", "cook_step": "1. 燕麦煮开\n2. 加蓝莓"},
    {"id": 4, "name": "西兰花炒虾仁", "calorie": 200, "protein": 25, "carb": 10, "fat": 8, "flavor": "清淡", "cook_step": "1. 虾仁处理\n2. 西兰花焯水\n3. 翻炒"},
    {"id": 5, "name": "番茄牛腩", "calorie": 350, "protein": 22, "carb": 18, "fat": 20, "flavor": "酸甜", "cook_step": "1. 牛腩焯水\n2. 炒番茄\n3. 炖煮1小时"},
    {"id": 6, "name": "蒜蓉菠菜", "calorie": 80, "protein": 4, "carb": 8, "fat": 4, "flavor": "清淡", "cook_step": "1. 菠菜焯水\n2. 爆香蒜\n3. 翻炒"}
]

mock_diet_records = [
    {"id": 1, "food_name": "燕麦粥", "food_type": "主食", "meal_time": "早餐", "weight": 200, "calorie": 180, "protein": 6, "carb": 32, "fat": 3, "create_time": "08:30"},
    {"id": 2, "food_name": "鸡胸肉沙拉", "food_type": "菜式", "meal_time": "午餐", "weight": 300, "calorie": 280, "protein": 35, "carb": 15, "fat": 8, "create_time": "12:15"},
    {"id": 3, "food_name": "清蒸鲈鱼", "food_type": "菜式", "meal_time": "晚餐", "weight": 250, "calorie": 200, "protein": 28, "carb": 5, "fat": 6, "create_time": "18:30"}
]

mock_hotfoods = [
    {"id": 1, "title": "春季养生汤品推荐：银耳莲子汤", "desc": "滋阴润肺", "likes": 1234, "source": "小红书", "tags": ["养生", "汤品"], "link": ""},
    {"id": 2, "title": "低脂减肥餐食谱分享", "desc": "健康减肥", "likes": 2345, "source": "小红书", "tags": ["减肥", "低脂"], "link": ""},
    {"id": 3, "title": "高蛋白健身餐制作指南", "desc": "增肌必备", "likes": 1890, "source": "小红书", "tags": ["健身", "高蛋白"], "link": ""},
    {"id": 4, "title": "宝宝辅食：营养蔬菜泥", "desc": "适合宝宝", "likes": 987, "source": "小红书", "tags": ["辅食", "营养"], "link": ""},
    {"id": 5, "title": "懒人快手菜：15分钟搞定晚餐", "desc": "简单美味", "likes": 3456, "source": "小红书", "tags": ["快手菜", "晚餐"], "link": ""}
]

mock_ingredients = [
    {"id": 1, "ingre_name": "鸡胸肉", "calorie": 165, "protein": 31, "carb": 0, "fat": 3.6, "category": "肉类"},
    {"id": 2, "ingre_name": "西兰花", "calorie": 34, "protein": 2.8, "carb": 7, "fat": 0.4, "category": "蔬菜"},
    {"id": 3, "ingre_name": "燕麦", "calorie": 389, "protein": 16.9, "carb": 66, "fat": 6.9, "category": "谷物"},
    {"id": 4, "ingre_name": "鲈鱼", "calorie": 105, "protein": 18.6, "carb": 0, "fat": 3.1, "category": "鱼类"},
    {"id": 5, "ingre_name": "番茄", "calorie": 18, "protein": 0.9, "carb": 3.9, "fat": 0.2, "category": "蔬菜"}
]

@app.route("/api/user/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    code = data.get("code", "")
    user_id = 1
    token = generate_token(user_id)
    return format_response(data={
        "token": token,
        "user_info": {"id": user_id, "nickname": "测试用户", "avatar": "", "phone": ""}
    })

@app.route("/api/recipe/list", methods=["GET"])
def get_recipes():
    token = request.headers.get("Authorization", "")
    if not verify_token(token):
        return format_response(401, "Token无效")
    return format_response(data={"total": len(mock_recipes), "list": mock_recipes})

@app.route("/api/recipe/recommend", methods=["POST"])
def recommend_recipe():
    token = request.headers.get("Authorization", "")
    if not verify_token(token):
        return format_response(401, "Token无效")
    return format_response(data={"recommend_list": mock_recipes[:3]})

@app.route("/api/diet/record", methods=["GET", "POST"])
def diet_record():
    print(f"[DEBUG] diet_record called, method={request.method}, args={request.args}")
    token = request.headers.get("Authorization", "")
    if not verify_token(token):
        return format_response(401, "Token无效")
    if request.method == "GET":
        return format_response(data={"total": len(mock_diet_records), "list": mock_diet_records})
    else:
        return format_response(msg="添加成功")

@app.route("/api/diet/record/<int:record_id>", methods=["DELETE"])
def delete_diet_record(record_id):
    token = request.headers.get("Authorization", "")
    if not verify_token(token):
        return format_response(401, "Token无效")
    return format_response(msg="删除成功")

@app.route("/api/hotfood/list", methods=["GET"])
def get_hotfoods():
    token = request.headers.get("Authorization", "")
    if not verify_token(token):
        return format_response(401, "Token无效")
    return format_response(data={"total": len(mock_hotfoods), "list": mock_hotfoods})

@app.route("/api/hotfood/crawl", methods=["POST"])
def crawl_hotfood():
    token = request.headers.get("Authorization", "")
    if not verify_token(token):
        return format_response(401, "Token无效")
    return format_response(msg="爬取成功")

@app.route("/api/ingredient/search", methods=["GET"])
def search_ingredient():
    token = request.headers.get("Authorization", "")
    if not verify_token(token):
        return format_response(401, "Token无效")
    keyword = request.args.get("keyword", "")
    results = [i for i in mock_ingredients if keyword in i["ingre_name"]] if keyword else mock_ingredients
    return format_response(data={"total": len(results), "list": results})

if __name__ == "__main__":
    print("=" * 50)
    print("健康饮食助手后端服务启动中...")
    print("地址: http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
