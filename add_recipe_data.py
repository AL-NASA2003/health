from app import create_app
from app.models.recipe import Recipe

app = create_app()

with app.app_context():
    # 检查现有食谱数量
    existing_count = Recipe.query.count()
    print(f"现有食谱数量: {existing_count}")
    
    # 如果没有食谱数据，添加一些测试数据
    if existing_count == 0:
        test_recipes = [
            {
                "recipe_name": "番茄炒蛋",
                "ingre_list": "番茄,鸡蛋,葱,盐,糖",
                "cook_step": "1. 番茄切块，鸡蛋打散\n2. 热锅倒油，炒鸡蛋\n3. 加入番茄翻炒\n4. 加盐糖调味",
                "calorie": 150,
                "protein": 10,
                "carb": 15,
                "fat": 8,
                "flavor": "酸甜",
                "cook_type": "炒",
                "suitable_crowd": "所有人",
                "image": "https://picsum.photos/seed/tomato-egg/300/200"
            },
            {
                "recipe_name": "红烧肉",
                "ingre_list": "五花肉,酱油,料酒,冰糖,姜",
                "cook_step": "1. 五花肉切块焯水\n2. 热锅下肉翻炒\n3. 加入调料炖煮\n4. 收汁出锅",
                "calorie": 300,
                "protein": 15,
                "carb": 5,
                "fat": 25,
                "flavor": "酱香",
                "cook_type": "炖",
                "suitable_crowd": "成年人",
                "image": "https://picsum.photos/seed/braised-pork/300/200"
            },
            {
                "recipe_name": "清炒西兰花",
                "ingre_list": "西兰花,蒜,盐,油",
                "cook_step": "1. 西兰花切朵焯水\n2. 热锅下蒜爆香\n3. 加入西兰花翻炒\n4. 加盐调味",
                "calorie": 80,
                "protein": 5,
                "carb": 10,
                "fat": 3,
                "flavor": "清淡",
                "cook_type": "炒",
                "suitable_crowd": "所有人",
                "image": "https://picsum.photos/seed/broccoli/300/200"
            }
        ]
        
        for recipe_data in test_recipes:
            recipe = Recipe(**recipe_data)
            recipe.save()
            print(f"添加食谱: {recipe.recipe_name}")
        
        print(f"添加完成，现在有 {Recipe.query.count()} 个食谱")
    else:
        # 打印现有食谱
        recipes = Recipe.query.all()
        print("现有食谱:")
        for recipe in recipes:
            print(f"- {recipe.id}: {recipe.recipe_name}")
