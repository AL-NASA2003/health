from flask import g, request
from app.models.comment import Comment
from app.models.forum_post import ForumPost
from app.models.user_like import UserLike
from app.utils.common import validate_params, format_response
from loguru import logger
from flask_restx import Namespace, Resource, fields

# 创建命名空间
comment_ns = Namespace('comment', description='评论相关操作')

# 定义请求模型
add_comment_model = comment_ns.model('AddComment', {
    'post_id': fields.Integer(required=True, description='帖子ID'),
    'content': fields.String(required=True, description='评论内容')
})

update_comment_model = comment_ns.model('UpdateComment', {
    'content': fields.String(required=True, description='评论内容')
})

# 定义响应模型
comment_model = comment_ns.model('Comment', {
    'id': fields.Integer(description='评论ID'),
    'post_id': fields.Integer(description='帖子ID'),
    'user_id': fields.Integer(description='用户ID'),
    'content': fields.String(description='评论内容'),
    'likes': fields.Integer(description='点赞数'),
    'create_time': fields.String(description='创建时间'),
    'is_liked': fields.Boolean(description='是否已点赞')
})

comment_list_model = comment_ns.model('CommentList', {
    'total': fields.Integer(description='总数'),
    'list': fields.List(fields.Nested(comment_model), description='评论列表'),
    'page': fields.Integer(description='页码'),
    'page_size': fields.Integer(description='每页大小')
})

from app.utils.auth_decorator import login_required

@comment_ns.route('/add')
class AddComment(Resource):
    """添加评论"""
    @login_required
    @comment_ns.expect(add_comment_model)
    def post(self):
        """添加评论
        请求参数：post_id, content
        """
        # 验证参数
        required_params = ["post_id", "content"]
        valid, params = validate_params(required_params)
        if not valid:
            return format_response(**params)
        
        # 检查帖子是否存在
        post = ForumPost.get_by_id(params["post_id"])
        if not post:
            return format_response(404, "帖子不存在")
        
        # 创建评论
        comment = Comment(
            post_id=params["post_id"],
            user_id=g.user_id,
            content=params["content"]
        )
        
        if comment.save():
            return format_response(msg="评论添加成功", data=comment.to_dict())
        else:
            return format_response(500, "评论添加失败")

@comment_ns.route('/list/<int:post_id>')
class CommentList(Resource):
    """获取评论列表"""
    @login_required
    @comment_ns.marshal_with(comment_list_model)
    def get(self, post_id):
        """获取评论列表
        请求参数：page, page_size(可选)
        """
        # 检查帖子是否存在
        post = ForumPost.get_by_id(post_id)
        if not post:
            return format_response(404, "帖子不存在")
        
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
        
        # 获取评论列表
        comments = Comment.get_by_post(post_id, page, page_size)
        comments_dict = []
        
        for comment in comments:
            comment_data = comment.to_dict()
            # 检查是否点赞
            like = UserLike.get_by_user_and_target(g.user_id, comment_id=comment.id)
            comment_data["is_liked"] = like is not None
            comments_dict.append(comment_data)
        
        # 获取总数
        total = Comment.query.filter_by(post_id=post_id).count()
        
        return format_response(data={
            "total": total,
            "list": comments_dict,
            "page": page,
            "page_size": page_size
        })

@comment_ns.route('/my/list')
class MyCommentList(Resource):
    """获取我的评论列表"""
    @login_required
    @comment_ns.marshal_with(comment_list_model)
    def get(self):
        """获取我的评论列表
        请求参数：page, page_size(可选)
        """
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
        
        # 获取评论列表
        comments = Comment.get_by_user(g.user_id, page, page_size)
        comments_dict = [c.to_dict() for c in comments]
        
        # 获取总数
        total = Comment.query.filter_by(user_id=g.user_id).count()
        
        return format_response(data={
            "total": total,
            "list": comments_dict,
            "page": page,
            "page_size": page_size
        })

@comment_ns.route('/update/<int:comment_id>')
class UpdateComment(Resource):
    """更新评论"""
    @login_required
    @comment_ns.expect(update_comment_model)
    def put(self, comment_id):
        """更新评论
        请求参数：content
        """
        comment = Comment.get_by_id(comment_id)
        if not comment:
            return format_response(404, "评论不存在")
        
        # 验证权限
        if comment.user_id != g.user_id:
            return format_response(403, "无权修改该评论")
        
        # 获取参数
        content = request.json.get("content")
        if not content:
            return format_response(400, "评论内容不能为空")
        
        # 更新字段
        comment.content = content
        
        if comment.update():
            return format_response(msg="评论更新成功", data=comment.to_dict())
        else:
            return format_response(500, "评论更新失败")

@comment_ns.route('/delete/<int:comment_id>')
class DeleteComment(Resource):
    """删除评论"""
    @login_required
    def delete(self, comment_id):
        """删除评论"""
        comment = Comment.get_by_id(comment_id)
        if not comment:
            return format_response(404, "评论不存在")
        
        # 验证权限
        if comment.user_id != g.user_id:
            return format_response(403, "无权删除该评论")
        
        if comment.delete():
            return format_response(msg="评论删除成功")
        else:
            return format_response(500, "评论删除失败")

@comment_ns.route('/like/<int:comment_id>')
class LikeComment(Resource):
    """点赞评论"""
    @login_required
    def post(self, comment_id):
        """点赞评论"""
        # 检查评论是否存在
        comment = Comment.get_by_id(comment_id)
        if not comment:
            return format_response(404, "评论不存在")
        
        # 检查是否已经点赞
        existing_like = UserLike.get_by_user_and_target(g.user_id, comment_id=comment_id)
        if existing_like:
            return format_response(400, "已经点赞过了")
        
        # 创建点赞记录
        like = UserLike(
            user_id=g.user_id,
            comment_id=comment_id
        )
        
        if like.save():
            # 增加评论点赞数
            comment.likes += 1
            comment.update()
            return format_response(msg="点赞成功")
        else:
            return format_response(500, "点赞失败")

@comment_ns.route('/unlike/<int:comment_id>')
class UnlikeComment(Resource):
    """取消点赞评论"""
    @login_required
    def post(self, comment_id):
        """取消点赞评论"""
        # 查找点赞记录
        like = UserLike.get_by_user_and_target(g.user_id, comment_id=comment_id)
        if not like:
            return format_response(400, "还没有点赞")
        
        # 获取评论
        comment = Comment.get_by_id(comment_id)
        if comment:
            # 减少评论点赞数
            if comment.likes > 0:
                comment.likes -= 1
                comment.update()
        
        if like.delete():
            return format_response(msg="取消点赞成功")
        else:
            return format_response(500, "取消点赞失败")

# 命名空间将在app/__init__.py中注册
