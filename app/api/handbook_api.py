from flask import Blueprint, g, request
from app.models.hand_account import HandAccount
from app.models.user_like import UserLike
from app.models.user_collection import UserCollection
from app.utils.common import validate_params, format_response
from loguru import logger

# 创建蓝图
handbook_bp = Blueprint("handbook", __name__)

from app.utils.auth_decorator import login_required

@handbook_bp.route("/add", methods=["POST"])
@login_required
def add_handbook():
    """添加手账
    请求参数：title, content, image(可选)
    """

    
    # 验证参数
    required_params = ["title", "content"]
    valid, params = validate_params(required_params)
    if not valid:
        return format_response(**params)
    
    # 创建手账
    hand_account = HandAccount(
        user_id=g.user_id,
        title=params["title"],
        content=params["content"],
        image=params.get("image", "")
    )
    
    if hand_account.save():
        return format_response(msg="手账添加成功", data=hand_account.to_dict())
    else:
        return format_response(500, "手账添加失败")

@handbook_bp.route("/list", methods=["GET"])
@login_required
def get_handbook_list():
    """获取手账列表
    请求参数：page, page_size(可选)
    """

    
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 获取手账列表
    hand_accounts = HandAccount.query.filter_by(user_id=g.user_id).order_by(HandAccount.create_time.desc()).offset(offset).limit(page_size).all()
    hand_accounts_dict = []
    
    for h in hand_accounts:
        data = h.to_dict()
        # 检查是否点赞
        like = UserLike.get_by_user_and_target(g.user_id, hand_account_id=h.id)
        data["is_liked"] = like is not None
        # 检查是否收藏
        collection = UserCollection.get_by_user_and_target(g.user_id, hand_account_id=h.id)
        data["is_collected"] = collection is not None
        # 统计点赞和收藏数
        data["like_count"] = UserLike.query.filter_by(hand_account_id=h.id).count()
        data["collect_count"] = UserCollection.query.filter_by(hand_account_id=h.id).count()
        hand_accounts_dict.append(data)
    
    # 获取总数
    total = HandAccount.query.filter_by(user_id=g.user_id).count()
    
    return format_response(data={
        "total": total,
        "list": hand_accounts_dict,
        "page": page,
        "page_size": page_size
    })

@handbook_bp.route("/detail/<int:handbook_id>", methods=["GET"])
@login_required
def get_handbook_detail(handbook_id):
    """获取手账详情"""

    
    hand_account = HandAccount.get_by_id(handbook_id, g.user_id)
    if not hand_account:
        return format_response(404, "手账不存在")
    
    # 检查是否点赞
    like = UserLike.get_by_user_and_target(g.user_id, hand_account_id=handbook_id)
    is_liked = like is not None
    
    # 检查是否收藏
    collection = UserCollection.get_by_user_and_target(g.user_id, hand_account_id=handbook_id)
    is_collected = collection is not None
    
    data = hand_account.to_dict()
    data["is_liked"] = is_liked
    data["is_collected"] = is_collected
    
    return format_response(data=data)

@handbook_bp.route("/update/<int:handbook_id>", methods=["PUT"])
@login_required
def update_handbook(handbook_id):
    """更新手账
    请求参数：title, content, image(可选)
    """

    
    hand_account = HandAccount.get_by_id(handbook_id, g.user_id)
    if not hand_account:
        return format_response(404, "手账不存在")
    
    # 获取参数
    title = request.json.get("title")
    content = request.json.get("content")
    image = request.json.get("image")
    
    # 更新字段
    if title:
        hand_account.title = title
    if content:
        hand_account.content = content
    if image is not None:
        hand_account.image = image
    
    if hand_account.update():
        return format_response(msg="手账更新成功", data=hand_account.to_dict())
    else:
        return format_response(500, "手账更新失败")

@handbook_bp.route("/delete/<int:handbook_id>", methods=["DELETE"])
@login_required
def delete_handbook(handbook_id):
    """删除手账"""

    
    hand_account = HandAccount.get_by_id(handbook_id, g.user_id)
    if not hand_account:
        return format_response(404, "手账不存在")
    
    if hand_account.delete():
        return format_response(msg="手账删除成功")
    else:
        return format_response(500, "手账删除失败")

@handbook_bp.route("/like/<int:handbook_id>", methods=["POST"])
@login_required
def like_handbook(handbook_id):
    """点赞手账"""

    
    # 检查手账是否存在
    hand_account = HandAccount.get_by_id(handbook_id, g.user_id)
    if not hand_account:
        return format_response(404, "手账不存在")
    
    # 检查是否已经点赞
    existing_like = UserLike.get_by_user_and_target(g.user_id, hand_account_id=handbook_id)
    if existing_like:
        return format_response(400, "已经点赞过了")
    
    # 创建点赞记录
    like = UserLike(
        user_id=g.user_id,
        hand_account_id=handbook_id
    )
    
    if like.save():
        return format_response(msg="点赞成功")
    else:
        return format_response(500, "点赞失败")

@handbook_bp.route("/unlike/<int:handbook_id>", methods=["POST"])
@login_required
def unlike_handbook(handbook_id):
    """取消点赞手账"""

    
    # 查找点赞记录
    like = UserLike.get_by_user_and_target(g.user_id, hand_account_id=handbook_id)
    if not like:
        return format_response(400, "还没有点赞")
    
    if like.delete():
        return format_response(msg="取消点赞成功")
    else:
        return format_response(500, "取消点赞失败")

@handbook_bp.route("/collect/<int:handbook_id>", methods=["POST"])
@login_required
def collect_handbook(handbook_id):
    """收藏手账"""

    
    # 检查手账是否存在
    hand_account = HandAccount.get_by_id(handbook_id, g.user_id)
    if not hand_account:
        return format_response(404, "手账不存在")
    
    # 检查是否已经收藏
    existing_collection = UserCollection.get_by_user_and_target(g.user_id, hand_account_id=handbook_id)
    if existing_collection:
        return format_response(400, "已经收藏过了")
    
    # 创建收藏记录
    collection = UserCollection(
        user_id=g.user_id,
        hand_account_id=handbook_id
    )
    
    if collection.save():
        return format_response(msg="收藏成功")
    else:
        return format_response(500, "收藏失败")

@handbook_bp.route("/uncollect/<int:handbook_id>", methods=["POST"])
@login_required
def uncollect_handbook(handbook_id):
    """取消收藏手账"""

    
    # 查找收藏记录
    collection = UserCollection.get_by_user_and_target(g.user_id, hand_account_id=handbook_id)
    if not collection:
        return format_response(400, "还没有收藏")
    
    if collection.delete():
        return format_response(msg="取消收藏成功")
    else:
        return format_response(500, "取消收藏失败")
