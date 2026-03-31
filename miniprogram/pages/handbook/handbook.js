const { get, post, put, del } = require('../../utils/request');
const { loginGuard } = require('../../utils/auth');

Page({
  data: {
    handbookList: [],
    loading: false,
    showDialog: false,
    isEdit: false,
    formData: {
      id: '',
      title: '',
      content: '',
      image: ''
    },
    showAIDialog: false,
    aiPrompt: '',
    aiSizes: ['1024x1024', '1024x1536', '1536x1024'],
    aiSizeIndex: 0,
    generatingImage: false,
    generatedImage: ''
  },

  // 页面加载
  onLoad(options) {
    if (!loginGuard()) return;
    
    // 立即显示默认数据，不等待网络请求
    this.setData({
      handbookList: [],
      loading: false
    });
    
    // 延迟发起网络请求更新数据
    setTimeout(() => {
      this.getHandbookList();
    }, 100);
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.getHandbookList(() => {
      wx.stopPullDownRefresh();
    });
  },

  // 获取手账列表
  getHandbookList(callback) {
    get('/handbook/list', {}, false)
      .then((result) => {
        let handbookList = result.data.list || [];
        const app = getApp();
        // 处理图片URL
        handbookList = handbookList.map(item => {
          if (item.image && !item.image.startsWith('http')) {
            item.image = app.globalData.staticBaseUrl + item.image;
          }
          return item;
        });
        this.setData({
          handbookList: handbookList
        });
        callback && callback();
      })
      .catch((err) => {
        console.error('获取手账列表失败：', err);
        callback && callback();
      });
  },

  // 显示添加弹窗
  showAddDialog() {
    this.setData({
      showDialog: true,
      isEdit: false,
      formData: {
        id: '',
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

  // 编辑手账
  editHandbook(e) {
    const item = e.currentTarget.dataset.item;
    let image = item.image;
    const app = getApp();
    // 处理图片URL
    if (image && !image.startsWith('http')) {
      image = app.globalData.staticBaseUrl + image;
    }
    this.setData({
      showDialog: true,
      isEdit: true,
      formData: {
        id: item.id,
        title: item.title,
        content: item.content,
        image: image
      }
    });
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
      sizeType: ['original', 'compressed'], // 可以选择原图或压缩图
      sourceType: ['album', 'camera'], // 可以从相册或相机选择
      success: (res) => {
        // 临时图片路径
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
    const token = wx.getStorageSync('token');
    
    // 先显示本地图片
    this.setData({
      'formData.image': tempFilePath
    });
    
    wx.uploadFile({
      url: getApp().globalData.baseUrl + '/upload/image',
      filePath: tempFilePath,
      name: 'file',
      header: {
        'Authorization': token
      },
      success: (res) => {
        try {
          const data = JSON.parse(res.data);
          if (data.code === 200) {
            // 更新为服务器返回的URL
            this.setData({
              'formData.image': data.data.url
            });
            wx.showToast({ title: '上传成功' });
          } else {
            wx.showToast({ title: data.msg || '上传失败', icon: 'none' });
          }
        } catch (e) {
          wx.showToast({ title: '上传失败', icon: 'none' });
        }
      },
      fail: (err) => {
        console.error('上传图片失败：', err);
        wx.showToast({ title: '上传失败', icon: 'none' });
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  },

  // 清除图片
  clearImage() {
    this.setData({
      'formData.image': ''
    });
  },

  // 一键抠图
  removeBg() {
    if (!this.data.formData.image) {
      wx.showToast({
        title: '请先上传图片',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({ title: '抠图中...', mask: true });
    
    const token = wx.getStorageSync('token');
    let imageUrl = this.data.formData.image;
    const staticBaseUrl = getApp().globalData.staticBaseUrl;
    
    if (imageUrl.startsWith('/static/')) {
      imageUrl = staticBaseUrl + imageUrl;
    }
    
    wx.downloadFile({
      url: imageUrl,
      timeout: 10000,
      success: (downloadRes) => {
        if (downloadRes.statusCode === 200 && downloadRes.tempFilePath) {
          this.uploadAndRemoveBg(downloadRes.tempFilePath, token);
        } else {
          wx.hideLoading();
          wx.showToast({
            title: '下载图片失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('下载图片失败：', err);
        wx.hideLoading();
        wx.showToast({
          title: '下载图片失败，请重试',
          icon: 'none'
        });
      }
    });
  },

  // 上传并抠图
  uploadAndRemoveBg(filePath, token) {
    wx.uploadFile({
      url: getApp().globalData.baseUrl + '/removebg/process',
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': token,
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000,
      success: (res) => {
        wx.hideLoading();
        try {
          const data = JSON.parse(res.data);
          if (data.code === 0 && data.data && data.data.url) {
            this.setData({
              'formData.image': data.data.url
            });
            wx.showToast({
              title: '抠图成功！',
              icon: 'success'
            });
          } else {
            wx.showToast({
              title: data.msg || '抠图失败',
              icon: 'none'
            });
          }
        } catch (e) {
          console.error('解析响应失败：', e);
          wx.showToast({
            title: '抠图失败，请重试',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('抠图失败：', err);
        wx.showToast({
          title: '抠图失败，请重试',
          icon: 'none'
        });
      }
    });
  },

  // 提交表单
  submitForm() {
    const { formData, isEdit } = this.data;
    
    if (!formData.title) {
      wx.showToast({ title: '请输入标题', icon: 'none' });
      return;
    }
    if (!formData.content) {
      wx.showToast({ title: '请输入内容', icon: 'none' });
      return;
    }

    if (isEdit) {
      put(`/handbook/update/${formData.id}`, formData)
        .then(() => {
          wx.showToast({ title: '保存成功' });
          this.hideDialog();
          this.getHandbookList();
        })
        .catch((err) => {
          console.error('更新手账失败：', err);
          wx.showToast({ title: '保存失败', icon: 'none' });
        });
    } else {
      post('/handbook/add', formData)
        .then(() => {
          wx.showToast({ title: '添加成功' });
          this.hideDialog();
          this.getHandbookList();
        })
        .catch((err) => {
          console.error('添加手账失败：', err);
          wx.showToast({ title: '添加失败', icon: 'none' });
        });
    }
  },

  // 删除手账
  deleteHandbook(e) {
    const id = e.currentTarget.dataset.id;
    
    wx.showModal({
      title: '提示',
      content: '确定要删除该手账吗？',
      success: (res) => {
        if (res.confirm) {
          del(`/handbook/delete/${id}`)
            .then(() => {
              wx.showToast({ title: '删除成功' });
              this.getHandbookList();
            })
            .catch((err) => {
              console.error('删除手账失败：', err);
              wx.showToast({ title: '删除失败', icon: 'none' });
            });
        }
      }
    });
  },

  // 点赞手账
  likeHandbook(e) {
    const id = e.currentTarget.dataset.id;
    const isLiked = e.currentTarget.dataset.liked;
    
    if (isLiked) {
      post(`/handbook/unlike/${id}`)
        .then(() => {
          wx.showToast({ title: '取消点赞成功' });
          this.getHandbookList();
        })
        .catch((err) => {
          console.error('取消点赞失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    } else {
      post(`/handbook/like/${id}`)
        .then(() => {
          wx.showToast({ title: '点赞成功' });
          this.getHandbookList();
        })
        .catch((err) => {
          console.error('点赞失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    }
  },

  // 收藏手账
  collectHandbook(e) {
    const id = e.currentTarget.dataset.id;
    const isCollected = e.currentTarget.dataset.collected;
    
    if (isCollected) {
      post(`/handbook/uncollect/${id}`)
        .then(() => {
          wx.showToast({ title: '取消收藏成功' });
          this.getHandbookList();
        })
        .catch((err) => {
          console.error('取消收藏失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    } else {
      post(`/handbook/collect/${id}`)
        .then(() => {
          wx.showToast({ title: '收藏成功' });
          this.getHandbookList();
        })
        .catch((err) => {
          console.error('收藏失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    }
  },

  // 显示AI生成弹窗
  showAIGenerateDialog() {
    this.setData({
      showAIDialog: true,
      aiPrompt: '',
      generatedImage: '',
      generatingImage: false
    });
  },

  // 隐藏AI生成弹窗
  hideAIGenerateDialog() {
    this.setData({ showAIDialog: false });
  },

  // AI提示词输入
  onAIPromptInput(e) {
    this.setData({ aiPrompt: e.detail.value });
  },

  // AI尺寸选择
  onAISizeChange(e) {
    this.setData({ aiSizeIndex: e.detail.value });
  },

  // 生成AI图像
  generateAIImage() {
    const { aiPrompt, aiSizes, aiSizeIndex } = this.data;
    
    if (!aiPrompt.trim()) {
      wx.showToast({ title: '请输入图像描述', icon: 'none' });
      return;
    }

    this.setData({ generatingImage: true, generatedImage: '' });

    post('/image/generate', {
      prompt: aiPrompt,
      size: aiSizes[aiSizeIndex]
    })
      .then((result) => {
        if (result.data && result.data.image_url) {
          const source = result.data.source || 'unknown';
          let message = '图像生成成功';
          if (source === 'zhipuai') {
            message = '智谱AI图像生成成功';
          } else if (source === 'fast_fallback' || source === 'fallback') {
            message = '已为您快速生成占位图像';
          }
          this.setData({ 
            generatedImage: result.data.image_url,
            generatingImage: false 
          });
          if (source !== 'zhipuai') {
            wx.showToast({ title: message, icon: 'success', duration: 2000 });
          } else {
            wx.showToast({ title: message, icon: 'success', duration: 1500 });
          }
        } else {
          throw new Error('生成失败');
        }
      })
      .catch((err) => {
        console.error('生成图像失败：', err);
        this.setData({ generatingImage: false });
        wx.showToast({ title: '生成图像失败', icon: 'none' });
      });
  },

  // 使用生成的图像
  useGeneratedImage() {
    const { generatedImage } = this.data;
    this.setData({
      'formData.image': generatedImage,
      showAIDialog: false
    });
    wx.showToast({ title: '已添加图像' });
  }
});
