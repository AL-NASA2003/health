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
    // 先显示本地图片
    this.setData({
      'formData.image': tempFilePath
    });
    
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
            // 拼接完整的URL
            let imageUrl = data.data.url;
            if (imageUrl.startsWith('/static/')) {
              imageUrl = app.globalData.staticBaseUrl + imageUrl;
            }
            this.setData({
              'formData.image': imageUrl
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
    const { formData, postList } = this.data;
    
    if (!formData.title) {
      wx.showToast({ title: '请输入标题', icon: 'none' });
      return;
    }
    if (!formData.content) {
      wx.showToast({ title: '请输入内容', icon: 'none' });
      return;
    }

    // 乐观更新：先添加到本地列表
    const newPost = {
      id: Date.now(), // 使用临时ID
      title: formData.title,
      content: formData.content,
      image: formData.image,
      is_liked: false,
      is_collected: false,
      likes: 0,
      views: 0,
      create_time: new Date().toLocaleString(),
      user: {
        nickname: '我',
        avatar: ''
      }
    };
    const newList = [newPost, ...postList];
    this.setData({ postList: newList });
    this.hideDialog();
    
    // 使用后端返回的数据更新本地
    post('/forum/add', formData)
      .then((res) => {
        if (res.data) {
          const app = getApp();
          let imageUrl = res.data.image || '';
          if (imageUrl && !imageUrl.startsWith('http')) {
            imageUrl = app.globalData.staticBaseUrl + imageUrl;
          }
          const realPost = {
            ...res.data,
            image: imageUrl,
            is_liked: false,
            is_collected: false
          };
          // 替换临时数据为真实数据
          const updatedList = this.data.postList.map(item => {
            if (item.id === newPost.id) {
              return realPost;
            }
            return item;
          });
          this.setData({ postList: updatedList });
        }
        wx.showToast({ title: '发布成功' });
      })
      .catch((err) => {
        console.error('发布帖子失败：', err);
        wx.showToast({ title: '发布失败', icon: 'none' });
        // 失败时删除临时添加的数据
        const updatedList = this.data.postList.filter(item => item.id !== newPost.id);
        this.setData({ postList: updatedList });
      });
  },

  // 查看帖子详情
  viewPostDetail(e) {
    const postId = e.currentTarget.dataset.id;
    if (!postId) {
      wx.showToast({ title: '帖子不存在', icon: 'none' });
      return;
    }
    console.log('跳转到帖子详情:', postId);
    wx.navigateTo({
      url: `/pages/forum/detail/detail?id=${postId}`,
      success: () => {
        console.log('跳转成功');
      },
      fail: (err) => {
        console.error('跳转失败:', err);
        wx.showToast({ title: '打开失败', icon: 'none' });
      }
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
    
    // 先乐观更新UI
    const newPostList = this.data.postList.map(post => {
      if (post.id === id) {
        return {
          ...post,
          is_liked: !isLiked,
          likes: isLiked ? Math.max(0, (post.likes || 0) - 1) : (post.likes || 0) + 1
        };
      }
      return post;
    });
    this.setData({ postList: newPostList });
    
    if (isLiked) {
      post(`/forum/unlike/${id}`)
        .then(() => {
          wx.showToast({ title: '取消点赞成功' });
        })
        .catch((err) => {
          console.error('取消点赞失败：', err);
          // 失败回滚
          this.getPostList();
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    } else {
      post(`/forum/like/${id}`)
        .then(() => {
          wx.showToast({ title: '点赞成功' });
        })
        .catch((err) => {
          console.error('点赞失败：', err);
          // 失败回滚
          this.getPostList();
          if (err.data && err.data.code === 400 && err.data.msg === '已经点赞过了') {
            // 已点赞过，不显示错误
          } else {
            wx.showToast({ title: '操作失败', icon: 'none' });
          }
        });
    }
  },

  // 收藏帖子
  collectPost(e) {
    const id = e.currentTarget.dataset.id;
    const isCollected = e.currentTarget.dataset.collected;
    
    // 先乐观更新UI
    const newPostList = this.data.postList.map(post => {
      if (post.id === id) {
        return {
          ...post,
          is_collected: !isCollected,
          collects: isCollected ? Math.max(0, (post.collects || 0) - 1) : (post.collects || 0) + 1
        };
      }
      return post;
    });
    this.setData({ postList: newPostList });
    
    if (isCollected) {
      post(`/forum/uncollect/${id}`)
        .then(() => {
          wx.showToast({ title: '取消收藏成功' });
        })
        .catch((err) => {
          console.error('取消收藏失败：', err);
          // 失败回滚
          this.getPostList();
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    } else {
      post(`/forum/collect/${id}`)
        .then(() => {
          wx.showToast({ title: '收藏成功' });
        })
        .catch((err) => {
          console.error('收藏失败：', err);
          // 失败回滚
          this.getPostList();
          if (err.data && err.data.code === 400 && err.data.msg === '已经收藏过了') {
            // 已收藏过，不显示错误
          } else {
            wx.showToast({ title: '操作失败', icon: 'none' });
          }
        });
    }
  }
});
