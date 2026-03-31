from flask import Blueprint, g, request
from app.models.forum_post import ForumPost
from app.models.user_like import UserLike
from app.models.user_collection import UserCollection
from app.utils.common import validate_params, format_response
from loguru import logger

# 创建蓝图
forum_bp = Blueprint("forum", __name__)

from app.utils.auth_decorator import login_required

@forum_bp.route("/add", methods=["POST"])
@login_required
def add_post():
    """添加帖子
    请求参数：title, content, image(可选)
    """

    
    # 验证参数
    required_params = ["title", "content"]
    valid, params = validate_params(required_params)
    if not valid:
        return format_response(**params)
    
    # 获取图片参数（可选）
    image = request.json.get("image", "")
    
    # 创建帖子
    post = ForumPost(
        user_id=g.user_id,
        title=params["title"],
        content=params["content"],
        image=image
    )
    
    if post.save():
        return format_response(msg="帖子添加成功", data=post.to_dict())
    else:
        return format_response(500, "帖子添加失败")

@forum_bp.route("/list", methods=["GET"])
@login_required
def get_post_list():
    """获取帖子列表
    请求参数：page, page_size(可选)
    """

    
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    
    # 获取帖子列表
    posts = ForumPost.get_all(page, page_size)
    posts_dict = []
    
    for post in posts:
        post_data = post.to_dict()
        # 检查是否点赞
        like = UserLike.get_by_user_and_target(g.user_id, post_id=post.id)
        post_data["is_liked"] = like is not None
        # 检查是否收藏
        collection = UserCollection.get_by_user_and_target(g.user_id, post_id=post.id)
        post_data["is_collected"] = collection is not None
        posts_dict.append(post_data)
    
    # 获取总数
    total = ForumPost.query.count()
    
    return format_response(data={
        "total": total,
        "list": posts_dict,
        "page": page,
        "page_size": page_size
    })

@forum_bp.route("/my/list", methods=["GET"])
@login_required
def get_my_post_list():
    """获取我的帖子列表
    请求参数：page, page_size(可选)
    """

    
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    
    # 获取帖子列表
    posts = ForumPost.get_by_user(g.user_id, page, page_size)
    posts_dict = [p.to_dict() for p in posts]
    
    # 获取总数
    total = ForumPost.query.filter_by(user_id=g.user_id).count()
    
    return format_response(data={
        "total": total,
        "list": posts_dict,
        "page": page,
        "page_size": page_size
    })

@forum_bp.route("/detail/<int:post_id>", methods=["GET"])
@login_required
def get_post_detail(post_id):
    """获取帖子详情"""

    
    post = ForumPost.get_by_id(post_id)
    if not post:
        return format_response(404, "帖子不存在")
    
    # 增加浏览数
    post.increment_views()
    
    # 检查是否点赞
    like = UserLike.get_by_user_and_target(g.user_id, post_id=post_id)
    is_liked = like is not None
    
    # 检查是否收藏
    collection = UserCollection.get_by_user_and_target(g.user_id, post_id=post_id)
    is_collected = collection is not None
    
    data = post.to_dict()
    data["is_liked"] = is_liked
    data["is_collected"] = is_collected
    
    return format_response(data=data)

@forum_bp.route("/update/<int:post_id>", methods=["PUT"])
@login_required
def update_post(post_id):
    """更新帖子
    请求参数：title, content
    """

    
    post = ForumPost.get_by_id(post_id)
    if not post:
        return format_response(404, "帖子不存在")
    
    # 验证权限
    if post.user_id != g.user_id:
        return format_response(403, "无权修改该帖子")
    
    # 获取参数
    title = request.json.get("title")
    content = request.json.get("content")
    
    # 更新字段
    if title:
        post.title = title
    if content:
        post.content = content
    
    if post.update():
        return format_response(msg="帖子更新成功", data=post.to_dict())
    else:
        return format_response(500, "帖子更新失败")

@forum_bp.route("/delete/<int:post_id>", methods=["DELETE"])
@login_required
def delete_post(post_id):
    """删除帖子"""

    
    post = ForumPost.get_by_id(post_id)
    if not post:
        return format_response(404, "帖子不存在")
    
    # 验证权限
    if post.user_id != g.user_id:
        return format_response(403, "无权删除该帖子")
    
    if post.delete():
        return format_response(msg="帖子删除成功")
    else:
        return format_response(500, "帖子删除失败")

@forum_bp.route("/top/<int:post_id>", methods=["POST"])
@login_required
def top_post(post_id):
    """置顶帖子"""

    
    post = ForumPost.get_by_id(post_id)
    if not post:
        return format_response(404, "帖子不存在")
    
    # 验证权限（这里简化处理，实际应该检查用户是否为管理员）
    if post.user_id != g.user_id:
        return format_response(403, "无权置顶该帖子")
    
    post.is_top = True
    if post.update():
        return format_response(msg="帖子置顶成功")
    else:
        return format_response(500, "帖子置顶失败")

@forum_bp.route("/untop/<int:post_id>", methods=["POST"])
@login_required
def untop_post(post_id):
    """取消置顶帖子"""

    
    post = ForumPost.get_by_id(post_id)
    if not post:
        return format_response(404, "帖子不存在")
    
    # 验证权限（这里简化处理，实际应该检查用户是否为管理员）
    if post.user_id != g.user_id:
        return format_response(403, "无权取消置顶该帖子")
    
    post.is_top = False
    if post.update():
        return format_response(msg="帖子取消置顶成功")
    else:
        return format_response(500, "帖子取消置顶失败")

@forum_bp.route("/like/<int:post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    """点赞帖子"""

    
    # 检查帖子是否存在
    post = ForumPost.get_by_id(post_id)
    if not post:
        return format_response(404, "帖子不存在")
    
    # 检查是否已经点赞
    existing_like = UserLike.get_by_user_and_target(g.user_id, post_id=post_id)
    if existing_like:
        return format_response(400, "已经点赞过了")
    
    # 创建点赞记录
    like = UserLike(
        user_id=g.user_id,
        post_id=post_id
    )
    
    if like.save():
        # 增加帖子点赞数
        post.likes += 1
        post.update()
        return format_response(msg="点赞成功")
    else:
        return format_response(500, "点赞失败")

@forum_bp.route("/unlike/<int:post_id>", methods=["POST"])
@login_required
def unlike_post(post_id):
    """取消点赞帖子"""

    
    # 查找点赞记录
    like = UserLike.get_by_user_and_target(g.user_id, post_id=post_id)
    if not like:
        return format_response(400, "还没有点赞")
    
    # 获取帖子
    post = ForumPost.get_by_id(post_id)
    if post:
        # 减少帖子点赞数
        if post.likes > 0:
            post.likes -= 1
            post.update()
    
    if like.delete():
        return format_response(msg="取消点赞成功")
    else:
        return format_response(500, "取消点赞失败")

@forum_bp.route("/collect/<int:post_id>", methods=["POST"])
@login_required
def collect_post(post_id):
    """收藏帖子"""

    
    # 检查帖子是否存在
    post = ForumPost.get_by_id(post_id)
    if not post:
        return format_response(404, "帖子不存在")
    
    # 检查是否已经收藏
    existing_collection = UserCollection.get_by_user_and_target(g.user_id, post_id=post_id)
    if existing_collection:
        return format_response(400, "已经收藏过了")
    
    # 创建收藏记录
    collection = UserCollection(
        user_id=g.user_id,
        post_id=post_id
    )
    
    if collection.save():
        return format_response(msg="收藏成功")
    else:
        return format_response(500, "收藏失败")

@forum_bp.route("/uncollect/<int:post_id>", methods=["POST"])
@login_required
def uncollect_post(post_id):
    """取消收藏帖子"""

    
    # 查找收藏记录
    collection = UserCollection.get_by_user_and_target(g.user_id, post_id=post_id)
    if not collection:
        return format_response(400, "还没有收藏")
    
    if collection.delete():
        return format_response(msg="取消收藏成功")
    else:
        return format_response(500, "取消收藏失败")
