const { get, post, del } = require('../../../utils/request');
const { loginGuard } = require('../../../utils/auth');

Page({
  data: {
    postDetail: {},
    loading: true,
    showCommentDialog: false,
    commentContent: ''
  },

  // 页面加载
  onLoad(options) {
    if (!loginGuard()) return;
    const postId = options.id;
    if (postId) {
      this.getPostDetail(postId);
    }
  },

  // 获取帖子详情
  getPostDetail(postId) {
    this.setData({ loading: true });
    
    get(`/forum/detail/${postId}`)
      .then((result) => {
        let postDetail = result.data || {};
        // 如果有图片且不是完整URL，拼接静态资源URL
        if (postDetail.image && !postDetail.image.startsWith('http')) {
          const app = getApp();
          postDetail.image = app.globalData.staticBaseUrl + postDetail.image;
        }
        this.setData({
          postDetail: postDetail,
          loading: false
        });
      })
      .catch((err) => {
        console.error('获取帖子详情失败：', err);
        this.setData({ loading: false });
        wx.showToast({ title: '获取帖子详情失败', icon: 'none' });
      });
  },

  // 显示评论弹窗
  showCommentDialog() {
    this.setData({ showCommentDialog: true });
  },

  // 隐藏评论弹窗
  hideCommentDialog() {
    this.setData({ showCommentDialog: false, commentContent: '' });
  },

  // 评论输入
  onCommentInput(e) {
    this.setData({ commentContent: e.detail.value });
  },

  // 提交评论
  submitComment() {
    const { commentContent, postDetail } = this.data;
    
    if (!commentContent.trim()) {
      wx.showToast({ title: '请输入评论内容', icon: 'none' });
      return;
    }

    post('/comment/add', {
      post_id: postDetail.id,
      content: commentContent
    })
      .then(() => {
        wx.showToast({ title: '评论成功' });
        this.hideCommentDialog();
        // 重新获取帖子详情，更新评论列表
        this.getPostDetail(postDetail.id);
      })
      .catch((err) => {
        console.error('评论失败：', err);
        wx.showToast({ title: '评论失败', icon: 'none' });
      });
  },

  // 点赞帖子
  likePost() {
    const { postDetail } = this.data;
    const isLiked = postDetail.is_liked;
    
    if (isLiked) {
      post(`/forum/unlike/${postDetail.id}`)
        .then(() => {
          wx.showToast({ title: '取消点赞成功' });
          this.getPostDetail(postDetail.id);
        })
        .catch((err) => {
          console.error('取消点赞失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    } else {
      post(`/forum/like/${postDetail.id}`)
        .then(() => {
          wx.showToast({ title: '点赞成功' });
          this.getPostDetail(postDetail.id);
        })
        .catch((err) => {
          console.error('点赞失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    }
  },

  // 收藏帖子
  collectPost() {
    const { postDetail } = this.data;
    const isCollected = postDetail.is_collected;
    
    if (isCollected) {
      post(`/forum/uncollect/${postDetail.id}`)
        .then(() => {
          wx.showToast({ title: '取消收藏成功' });
          this.getPostDetail(postDetail.id);
        })
        .catch((err) => {
          console.error('取消收藏失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    } else {
      post(`/forum/collect/${postDetail.id}`)
        .then(() => {
          wx.showToast({ title: '收藏成功' });
          this.getPostDetail(postDetail.id);
        })
        .catch((err) => {
          console.error('收藏失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    }
  },

  // 删除帖子
  deletePost() {
    const { postDetail } = this.data;
    
    wx.showModal({
      title: '提示',
      content: '确定要删除该帖子吗？',
      success: (res) => {
        if (res.confirm) {
          del(`/forum/delete/${postDetail.id}`)
            .then(() => {
              wx.showToast({ title: '删除成功' });
              // 返回上一页
              wx.navigateBack();
            })
            .catch((err) => {
              console.error('删除帖子失败：', err);
              wx.showToast({ title: '删除失败', icon: 'none' });
            });
        }
      }
    });
  }
});
