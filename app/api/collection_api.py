from flask import g, request
from app.models.user_collection import UserCollection
from app.models.recipe import Recipe
from app.models.forum_post import ForumPost
from app.models.hand_account import HandAccount
from app.utils.common import format_response
from loguru import logger
from flask_restx import Namespace, Resource, fields

# 创建命名空间
collection_ns = Namespace('collection', description='收藏相关操作')

# 定义请求模型
add_collection_model = collection_ns.model('AddCollection', {
    'type': fields.String(required=True, description='收藏类型：recipe/post/hand_account'),
    'target_id': fields.Integer(required=True, description='目标ID')
})

# 定义响应模型
collection_model = collection_ns.model('Collection', {
    'id': fields.Integer(description='收藏ID'),
    'user_id': fields.Integer(description='用户ID'),
    'recipe_id': fields.Integer(description='食谱ID'),
    'post_id': fields.Integer(description='帖子ID'),
    'hand_account_id': fields.Integer(description='手账ID'),
    'create_time': fields.String(description='创建时间')
})

target_model = collection_ns.model('CollectionTarget', {
    'id': fields.Integer(description='目标ID'),
    'name': fields.String(description='目标名称'),
    'title': fields.String(description='目标标题'),
    'type': fields.String(description='目标类型')
})

collection_with_target_model = collection_ns.inherit('CollectionWithTarget', collection_model, {
    'target': fields.Nested(target_model, description='目标详情')
})

collection_list_model = collection_ns.model('CollectionList', {
    'total': fields.Integer(description='总数'),
    'list': fields.List(fields.Nested(collection_with_target_model), description='收藏列表'),
    'page': fields.Integer(description='页码'),
    'page_size': fields.Integer(description='每页大小')
})

from app.utils.auth_decorator import login_required

@collection_ns.route('/list')
class CollectionList(Resource):
    """获取收藏列表"""
    @login_required
    @collection_ns.marshal_with(collection_list_model)
    def get(self):
        """获取收藏列表
        请求参数：type(recipe/post/hand_account), page, page_size(可选)
        """
        collection_type = request.args.get("type")
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))
        
        # 获取收藏列表
        collections = UserCollection.get_by_user(g.user_id, collection_type, page, page_size)
        collections_dict = []
        
        for collection in collections:
            collection_data = collection.to_dict()
            # 根据收藏类型获取详细信息
            if collection.recipe_id:
                recipe = Recipe.query.get(collection.recipe_id)
                if recipe:
                    collection_data["target"] = {
                        "id": recipe.id,
                        "name": recipe.recipe_name,
                        "type": "recipe"
                    }
            elif collection.post_id:
                post = ForumPost.query.get(collection.post_id)
                if post:
                    collection_data["target"] = {
                        "id": post.id,
                        "title": post.title,
                        "type": "post"
                    }
            elif collection.hand_account_id:
                hand_account = HandAccount.query.get(collection.hand_account_id)
                if hand_account:
                    collection_data["target"] = {
                        "id": hand_account.id,
                        "title": hand_account.title,
                        "type": "hand_account"
                    }
            collections_dict.append(collection_data)
        
        # 获取总数
        total = UserCollection.query.filter_by(user_id=g.user_id).count()
        if collection_type:
            if collection_type == "recipe":
                total = UserCollection.query.filter_by(user_id=g.user_id, recipe_id__isnot=None).count()
            elif collection_type == "post":
                total = UserCollection.query.filter_by(user_id=g.user_id, post_id__isnot=None).count()
            elif collection_type == "hand_account":
                total = UserCollection.query.filter_by(user_id=g.user_id, hand_account_id__isnot=None).count()
        
        return format_response(data={
            "total": total,
            "list": collections_dict,
            "page": page,
            "page_size": page_size
        })

@collection_ns.route('/add')
class AddCollection(Resource):
    """添加收藏"""
    @login_required
    @collection_ns.expect(add_collection_model)
    def post(self):
        """添加收藏
        请求参数：type(recipe/post/hand_account), target_id
        """
        # 获取参数
        collection_type = request.json.get("type")
        target_id = request.json.get("target_id")
        
        if not collection_type or not target_id:
            return format_response(400, "参数缺失")
        
        # 检查目标是否存在
        if collection_type == "recipe":
            target = Recipe.query.get(target_id)
            if not target:
                return format_response(404, "食谱不存在")
        elif collection_type == "post":
            target = ForumPost.query.get(target_id)
            if not target:
                return format_response(404, "帖子不存在")
        elif collection_type == "hand_account":
            target = HandAccount.query.get(target_id)
            if not target:
                return format_response(404, "手账不存在")
        else:
            return format_response(400, "无效的收藏类型")
        
        # 检查是否已经收藏
        existing_collection = None
        if collection_type == "recipe":
            existing_collection = UserCollection.get_by_user_and_target(g.user_id, recipe_id=target_id)
        elif collection_type == "post":
            existing_collection = UserCollection.get_by_user_and_target(g.user_id, post_id=target_id)
        elif collection_type == "hand_account":
            existing_collection = UserCollection.get_by_user_and_target(g.user_id, hand_account_id=target_id)
        
        if existing_collection:
            return format_response(400, "已经收藏过了")
        
        # 创建收藏记录
        collection = UserCollection(
            user_id=g.user_id
        )
        
        if collection_type == "recipe":
            collection.recipe_id = target_id
        elif collection_type == "post":
            collection.post_id = target_id
        elif collection_type == "hand_account":
            collection.hand_account_id = target_id
        
        if collection.save():
            return format_response(msg="收藏成功")
        else:
            return format_response(500, "收藏失败")

@collection_ns.route('/remove')
class RemoveCollection(Resource):
    """取消收藏"""
    @login_required
    @collection_ns.expect(add_collection_model)
    def post(self):
        """取消收藏
        请求参数：type(recipe/post/hand_account), target_id
        """
        # 获取参数
        collection_type = request.json.get("type")
        target_id = request.json.get("target_id")
        
        if not collection_type or not target_id:
            return format_response(400, "参数缺失")
        
        # 查找收藏记录
        collection = None
        if collection_type == "recipe":
            collection = UserCollection.get_by_user_and_target(g.user_id, recipe_id=target_id)
        elif collection_type == "post":
            collection = UserCollection.get_by_user_and_target(g.user_id, post_id=target_id)
        elif collection_type == "hand_account":
            collection = UserCollection.get_by_user_and_target(g.user_id, hand_account_id=target_id)
        else:
            return format_response(400, "无效的收藏类型")
        
        if not collection:
            return format_response(400, "还没有收藏")
        
        if collection.delete():
            return format_response(msg="取消收藏成功")
        else:
            return format_response(500, "取消收藏失败")

@collection_ns.route('/check')
class CheckCollection(Resource):
    """检查是否收藏"""
    @login_required
    @collection_ns.expect(add_collection_model)
    def post(self):
        """检查是否收藏
        请求参数：type(recipe/post/hand_account), target_id
        """
        # 获取参数
        collection_type = request.json.get("type")
        target_id = request.json.get("target_id")
        
        if not collection_type or not target_id:
            return format_response(400, "参数缺失")
        
        # 查找收藏记录
        collection = None
        if collection_type == "recipe":
            collection = UserCollection.get_by_user_and_target(g.user_id, recipe_id=target_id)
        elif collection_type == "post":
            collection = UserCollection.get_by_user_and_target(g.user_id, post_id=target_id)
        elif collection_type == "hand_account":
            collection = UserCollection.get_by_user_and_target(g.user_id, hand_account_id=target_id)
        else:
            return format_response(400, "无效的收藏类型")
        
        return format_response(data={"is_collected": collection is not None})

# 命名空间将在app/__init__.py中注册
