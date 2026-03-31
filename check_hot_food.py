from app import create_app, db
from app.models.hot_food import HotFood

app = create_app()
with app.app_context():
    foods = HotFood.query.all()
    print('热点美食数量:', len(foods))
    for food in foods[:5]:
        print('ID:', food.id, '名称:', food.food_name, '热度:', food.hot_score)
        print('描述:', food.description)
        print('图片:', food.image)
        print('标签:', food.tags)
        print('---')
