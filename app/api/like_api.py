from flask import Blueprint, g, request
from app.models.user_like import UserLike
from app.models.hot_food import HotFood
from app.models.forum_post import ForumPost
from app.models.comment import Comment
from app.models.hand_account import HandAccount
from app.utils.common import format_response
from loguru import logger

# 创建蓝图
like_bp = Blueprint("like", __name__)

from app.utils.auth_decorator import login_required

@like_bp.route("/list", methods=["GET"])
@login_required
def get_like_list():
    """获取点赞列表
    请求参数：type(hot_food/post/comment/hand_account), page, page_size(可选)
    """

    
    like_type = request.args.get("type")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    
    # 获取点赞列表
    likes = UserLike.get_by_user(g.user_id, like_type, page, page_size)
    likes_dict = []
    
    for like in likes:
        like_data = like.to_dict()
        # 根据点赞类型获取详细信息
        if like.hot_food_id:
            hot_food = HotFood.query.get(like.hot_food_id)
            if hot_food:
                like_data["target"] = {
                    "id": hot_food.id,
                    "title": hot_food.food_name,
                    "type": "hot_food"
                }
        elif like.post_id:
            post = ForumPost.query.get(like.post_id)
            if post:
                like_data["target"] = {
                    "id": post.id,
                    "title": post.title,
                    "type": "post"
                }
        elif like.comment_id:
            comment = Comment.query.get(like.comment_id)
            if comment:
                like_data["target"] = {
                    "id": comment.id,
                    "content": comment.content[:50] + "..." if len(comment.content) > 50 else comment.content,
                    "type": "comment"
                }
        elif like.hand_account_id:
            hand_account = HandAccount.query.get(like.hand_account_id)
            if hand_account:
                like_data["target"] = {
                    "id": hand_account.id,
                    "title": hand_account.title,
                    "type": "hand_account"
                }
        likes_dict.append(like_data)
    
    # 获取总数
    total = UserLike.query.filter_by(user_id=g.user_id).count()
    if like_type:
        if like_type == "hot_food":
            total = UserLike.query.filter_by(user_id=g.user_id, hot_food_id__isnot=None).count()
        elif like_type == "post":
            total = UserLike.query.filter_by(user_id=g.user_id, post_id__isnot=None).count()
        elif like_type == "comment":
            total = UserLike.query.filter_by(user_id=g.user_id, comment_id__isnot=None).count()
        elif like_type == "hand_account":
            total = UserLike.query.filter_by(user_id=g.user_id, hand_account_id__isnot=None).count()
    
    return format_response(data={
        "total": total,
        "list": likes_dict,
        "page": page,
        "page_size": page_size
    })

@like_bp.route("/add", methods=["POST"])
@login_required
def add_like():
    """添加点赞
    请求参数：type(hot_food/post/comment/hand_account), target_id
    """

    
    # 获取参数
    like_type = request.json.get("type")
    target_id = request.json.get("target_id")
    
    if not like_type or not target_id:
        return format_response(400, "参数缺失")
    
    # 检查目标是否存在
    if like_type == "hot_food":
        target = HotFood.query.get(target_id)
        if not target:
            return format_response(404, "热点美食不存在")
    elif like_type == "post":
        target = ForumPost.query.get(target_id)
        if not target:
            return format_response(404, "帖子不存在")
    elif like_type == "comment":
        target = Comment.query.get(target_id)
        if not target:
            return format_response(404, "评论不存在")
    elif like_type == "hand_account":
        target = HandAccount.query.get(target_id)
        if not target:
            return format_response(404, "手账不存在")
    else:
        return format_response(400, "无效的点赞类型")
    
    # 检查是否已经点赞
    existing_like = None
    if like_type == "hot_food":
        existing_like = UserLike.get_by_user_and_target(g.user_id, hot_food_id=target_id)
    elif like_type == "post":
        existing_like = UserLike.get_by_user_and_target(g.user_id, post_id=target_id)
    elif like_type == "comment":
        existing_like = UserLike.get_by_user_and_target(g.user_id, comment_id=target_id)
    elif like_type == "hand_account":
        existing_like = UserLike.get_by_user_and_target(g.user_id, hand_account_id=target_id)
    
    if existing_like:
        return format_response(400, "已经点赞过了")
    
    # 创建点赞记录
    like = UserLike(
        user_id=g.user_id
    )
    
    if like_type == "hot_food":
        like.hot_food_id = target_id
    elif like_type == "post":
        like.post_id = target_id
    elif like_type == "comment":
        like.comment_id = target_id
    elif like_type == "hand_account":
        like.hand_account_id = target_id
    
    if like.save():
        # 增加目标点赞数
        if like_type == "post":
            target.likes += 1
            target.update()
        elif like_type == "comment":
            target.likes += 1
            target.update()
        return format_response(msg="点赞成功")
    else:
        return format_response(500, "点赞失败")

@like_bp.route("/remove", methods=["POST"])
@login_required
def remove_like():
    """取消点赞
    请求参数：type(hot_food/post/comment/hand_account), target_id
    """

    
    # 获取参数
    like_type = request.json.get("type")
    target_id = request.json.get("target_id")
    
    if not like_type or not target_id:
        return format_response(400, "参数缺失")
    
    # 查找点赞记录
    like = None
    if like_type == "hot_food":
        like = UserLike.get_by_user_and_target(g.user_id, hot_food_id=target_id)
    elif like_type == "post":
        like = UserLike.get_by_user_and_target(g.user_id, post_id=target_id)
    elif like_type == "comment":
        like = UserLike.get_by_user_and_target(g.user_id, comment_id=target_id)
    elif like_type == "hand_account":
        like = UserLike.get_by_user_and_target(g.user_id, hand_account_id=target_id)
    else:
        return format_response(400, "无效的点赞类型")
    
    if not like:
        return format_response(400, "还没有点赞")
    
    # 获取目标并减少点赞数
    if like_type == "post":
        target = ForumPost.query.get(target_id)
        if target and target.likes > 0:
            target.likes -= 1
            target.update()
    elif like_type == "comment":
        target = Comment.query.get(target_id)
        if target and target.likes > 0:
            target.likes -= 1
            target.update()
    
    if like.delete():
        return format_response(msg="取消点赞成功")
    else:
        return format_response(500, "取消点赞失败")

@like_bp.route("/check", methods=["POST"])
@login_required
def check_like():
    """检查是否点赞
    请求参数：type(hot_food/post/comment/hand_account), target_id
    """

    
    # 获取参数
    like_type = request.json.get("type")
    target_id = request.json.get("target_id")
    
    if not like_type or not target_id:
        return format_response(400, "参数缺失")
    
    # 查找点赞记录
    like = None
    if like_type == "hot_food":
        like = UserLike.get_by_user_and_target(g.user_id, hot_food_id=target_id)
    elif like_type == "post":
        like = UserLike.get_by_user_and_target(g.user_id, post_id=target_id)
    elif like_type == "comment":
        like = UserLike.get_by_user_and_target(g.user_id, comment_id=target_id)
    elif like_type == "hand_account":
        like = UserLike.get_by_user_and_target(g.user_id, hand_account_id=target_id)
    else:
        return format_response(400, "无效的点赞类型")
    
    return format_response(data={"is_liked": like is not None})
