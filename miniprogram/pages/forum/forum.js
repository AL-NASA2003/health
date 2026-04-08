const { get, post, del } = require('../../utils/request');
const { loginGuard } = require('../../utils/auth');

Page({
  data: {
    postList: [],
    loading: false,
    showDialog: false,
    formData: {
      title: '',
      content: '',
      image: ''
    }
  },

  // 页面加载
  onLoad(options) {
    if (!loginGuard()) return;
    this.getPostList();
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.getPostList(() => {
      wx.stopPullDownRefresh();
    });
  },

  // 获取帖子列表
  getPostList(callback) {
    this.setData({ loading: true });
    
    get('/forum/list')
      .then((result) => {
        let postList = result.data.list || [];
        const app = getApp();
        // 处理图片URL
        postList = postList.map(item => {
          if (item.image && !item.image.startsWith('http')) {
            item.image = app.globalData.staticBaseUrl + item.image;
          }
          return item;
        });
        this.setData({
          postList: postList,
          loading: false
        });
        callback && callback();
      })
      .catch((err) => {
        console.error('获取帖子列表失败：', err);
        this.setData({ loading: false });
        callback && callback();
        wx.showToast({ title: '获取帖子失败', icon: 'none' });
      });
  },

  // 显示添加弹窗
  showAddDialog() {
    this.setData({
      showDialog: true,
      formData: {
        title: '',
        content: '',
        image: ''
      }
    });
  },

  // 隐藏弹窗
  hideDialog() {
    this.setData({ showDialog: false });
  },

  // 表单输入
  onFormInput(e) {
    const key = e.currentTarget.dataset.key;
    const value = e.detail.value;
    this.setData({
      [`formData.${key}`]: value
    });
  },

  // 选择图片
  chooseImage() {
    wx.chooseImage({
      count: 1, // 最多选择1张图片
      sizeType: ['compressed'], // 使用压缩图
      sourceType: ['album', 'camera'], // 可以从相册或相机选择
      success: (res) => {
        const tempFilePaths = res.tempFilePaths;
        if (tempFilePaths.length > 0) {
          this.uploadImage(tempFilePaths[0]);
        }
      },
      fail: (err) => {
        console.error('选择图片失败：', err);
      }
    });
  },

  // 上传图片
  uploadImage(tempFilePath) {
    wx.showLoading({ title: '上传中...' });
    
    const app = getApp();
    const token = wx.getStorageSync('token');
    
    wx.uploadFile({
      url: app.globalData.baseUrl + '/upload/image',
      filePath: tempFilePath,
      name: 'file',
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        wx.hideLoading();
        try {
          const data = JSON.parse(res.data);
          if (data.code === 200 && data.data && data.data.url) {
            this.setData({
              'formData.image': data.data.url
            });
            wx.showToast({ title: '上传成功', icon: 'success' });
          } else {
            wx.showToast({ title: data.msg || '上传失败', icon: 'none' });
          }
        } catch (e) {
          console.error('解析上传响应失败：', e);
          wx.showToast({ title: '上传失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('上传图片失败：', err);
        wx.showToast({ title: '上传失败', icon: 'none' });
      }
    });
  },

  // 提交表单
  submitForm() {
    const { formData } = this.data;
    
    if (!formData.title) {
      wx.showToast({ title: '请输入标题', icon: 'none' });
      return;
    }
    if (!formData.content) {
      wx.showToast({ title: '请输入内容', icon: 'none' });
      return;
    }

    post('/forum/add', formData)
      .then(() => {
        wx.showToast({ title: '发布成功' });
        this.hideDialog();
        this.getPostList();
      })
      .catch((err) => {
        console.error('发布帖子失败：', err);
        wx.showToast({ title: '发布失败', icon: 'none' });
      });
  },

  // 查看帖子详情
  viewPostDetail(e) {
    const postId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/forum/detail/detail?id=${postId}`
    });
  },

  // 删除帖子
  deletePost(e) {
    const id = e.currentTarget.dataset.id;
    
    wx.showModal({
      title: '提示',
      content: '确定要删除该帖子吗？',
      success: (res) => {
        if (res.confirm) {
          del(`/forum/delete/${id}`)
            .then(() => {
              wx.showToast({ title: '删除成功' });
              this.getPostList();
            })
            .catch((err) => {
              console.error('删除帖子失败：', err);
              wx.showToast({ title: '删除失败', icon: 'none' });
            });
        }
      }
    });
  },

  // 点赞帖子
  likePost(e) {
    const id = e.currentTarget.dataset.id;
    const isLiked = e.currentTarget.dataset.liked;
    
    if (isLiked) {
      post(`/forum/unlike/${id}`)
        .then(() => {
          wx.showToast({ title: '取消点赞成功' });
          this.getPostList();
        })
        .catch((err) => {
          console.error('取消点赞失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    } else {
      post(`/forum/like/${id}`)
        .then(() => {
          wx.showToast({ title: '点赞成功' });
          this.getPostList();
        })
        .catch((err) => {
          console.error('点赞失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    }
  },

  // 收藏帖子
  collectPost(e) {
    const id = e.currentTarget.dataset.id;
    const isCollected = e.currentTarget.dataset.collected;
    
    if (isCollected) {
      post(`/forum/uncollect/${id}`)
        .then(() => {
          wx.showToast({ title: '取消收藏成功' });
          this.getPostList();
        })
        .catch((err) => {
          console.error('取消收藏失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    } else {
      post(`/forum/collect/${id}`)
        .then(() => {
          wx.showToast({ title: '收藏成功' });
          this.getPostList();
        })
        .catch((err) => {
          console.error('收藏失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    }
  }
});
