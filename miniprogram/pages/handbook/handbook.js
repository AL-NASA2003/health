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
    aiSizes: ['1024x1024', '1024x1536', '1536x1024', '512x512'],
    aiSizeIndex: 0,
    generatingImage: false,
    generatedImage: '',
    // 手账专属配置
    aiStyles: [
      { key: 'cute', name: '可爱风格' },
      { key: 'watercolor', name: '水彩风格' },
      { key: 'minimal', name: '简约风格' },
      { key: 'retro', name: '复古风格' },
      { key: 'food', name: '美食主题' },
      { key: 'nature', name: '自然主题' }
    ],
    aiStyleIndex: 0,
    aiMoods: [
      { key: 'happy', name: '开心' },
      { key: 'calm', name: '平静' },
      { key: 'excited', name: '兴奋' },
      { key: 'grateful', name: '感恩' },
      { key: 'motivated', name: '励志' },
      { key: 'sad', name: '忧郁' }
    ],
    aiMoodIndex: 0,
    showStylePicker: false,
    showMoodPicker: false,
    // 预设快速提示词
    quickPrompts: [
      '健康早餐', '美味午餐', '健身打卡', '美好心情',
      '春日风景', '夏日清凉', '秋日美食', '冬日温暖',
      '营养沙拉', '轻食主义', '美食日记', '健康生活'
    ]
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
            // 更新为服务器返回的URL，并拼接完整URL
            let imageUrl = data.data.url;
            if (imageUrl.startsWith('/static/')) {
              imageUrl = getApp().globalData.staticBaseUrl + imageUrl;
            }
            this.setData({
              'formData.image': imageUrl
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
            // 拼接完整的URL
            let imageUrl = data.data.url;
            if (imageUrl.startsWith('/static/')) {
              imageUrl = getApp().globalData.staticBaseUrl + imageUrl;
            }
            this.setData({
              'formData.image': imageUrl
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
    const { formData, isEdit, handbookList } = this.data;
    
    if (!formData.title) {
      wx.showToast({ title: '请输入标题', icon: 'none' });
      return;
    }
    if (!formData.content) {
      wx.showToast({ title: '请输入内容', icon: 'none' });
      return;
    }

    if (isEdit) {
      // 乐观更新：先更新本地数据
      const updatedList = handbookList.map(item => {
        if (item.id === formData.id) {
          return { ...item, ...formData };
        }
        return item;
      });
      this.setData({ handbookList: updatedList });
      this.hideDialog();
      
      put(`/handbook/update/${formData.id}`, formData)
        .then(() => {
          wx.showToast({ title: '保存成功' });
          this.getHandbookList();
        })
        .catch((err) => {
          console.error('更新手账失败：', err);
          wx.showToast({ title: '保存失败', icon: 'none' });
          this.getHandbookList(); // 失败回滚
        });
    } else {
      // 乐观更新：先添加到本地列表
      const newHandbook = {
        id: Date.now(), // 使用临时ID
        title: formData.title,
        content: formData.content,
        image: formData.image,
        is_liked: false,
        likes: 0,
        create_time: new Date().toLocaleString(),
        user: {
          nickname: '我',
          avatar: ''
        }
      };
      const newList = [newHandbook, ...this.data.handbookList];
      this.setData({ handbookList: newList });
      this.hideDialog();
      
      // 使用后端返回的数据更新本地
      post('/handbook/add', formData)
        .then((res) => {
          if (res.data) {
            const app = getApp();
            let imageUrl = res.data.image || '';
            if (imageUrl && !imageUrl.startsWith('http')) {
              imageUrl = app.globalData.staticBaseUrl + imageUrl;
            }
            const realHandbook = {
              ...res.data,
              image: imageUrl,
              is_liked: false
            };
            // 替换临时数据为真实数据
            const updatedList = this.data.handbookList.map(item => {
              if (item.id === newHandbook.id) {
                return realHandbook;
              }
              return item;
            });
            this.setData({ handbookList: updatedList });
          }
          wx.showToast({ title: '添加成功' });
        })
        .catch((err) => {
          console.error('添加手账失败：', err);
          wx.showToast({ title: '添加失败', icon: 'none' });
          // 失败时删除临时添加的数据
          const updatedList = this.data.handbookList.filter(item => item.id !== newHandbook.id);
          this.setData({ handbookList: updatedList });
        });
    }
  },

  // 删除手账
  deleteHandbook(e) {
    const id = e.currentTarget.dataset.id;
    const { handbookList } = this.data;
    
    wx.showModal({
      title: '提示',
      content: '确定要删除该手账吗？',
      success: (res) => {
        if (res.confirm) {
          // 乐观更新：先从本地删除
          const updatedList = handbookList.filter(item => item.id !== id);
          this.setData({ handbookList: updatedList });
          
          del(`/handbook/delete/${id}`)
            .then(() => {
              wx.showToast({ title: '删除成功' });
              this.getHandbookList();
            })
            .catch((err) => {
              console.error('删除手账失败：', err);
              wx.showToast({ title: '删除失败', icon: 'none' });
              this.getHandbookList(); // 失败回滚
            });
        }
      }
    });
  },

  // 点赞手账
  likeHandbook(e) {
    const id = e.currentTarget.dataset.id;
    const isLiked = e.currentTarget.dataset.liked;
    const { handbookList } = this.data;
    
    // 乐观更新：先更新本地
    const updatedList = handbookList.map(item => {
      if (item.id === id) {
        return {
          ...item,
          isLiked: !isLiked,
          likes: isLiked ? Math.max(0, (item.likes || 0) - 1) : (item.likes || 0) + 1
        };
      }
      return item;
    });
    this.setData({ handbookList: updatedList });
    
    if (isLiked) {
      post(`/handbook/unlike/${id}`)
        .then(() => {
          wx.showToast({ title: '取消点赞成功' });
        })
        .catch((err) => {
          console.error('取消点赞失败：', err);
          // 失败回滚
          if (!(err.data && err.data.code === 400)) {
            wx.showToast({ title: '操作失败', icon: 'none' });
          }
          this.getHandbookList();
        });
    } else {
      post(`/handbook/like/${id}`)
        .then(() => {
          wx.showToast({ title: '点赞成功' });
        })
        .catch((err) => {
          console.error('点赞失败：', err);
          // 失败回滚
          if (!(err.data && err.data.code === 400)) {
            wx.showToast({ title: '操作失败', icon: 'none' });
          }
          this.getHandbookList();
        });
    }
  },

  // 收藏手账
  collectHandbook(e) {
    const id = e.currentTarget.dataset.id;
    const isCollected = e.currentTarget.dataset.collected;
    const { handbookList } = this.data;
    
    // 乐观更新：先更新本地
    const updatedList = handbookList.map(item => {
      if (item.id === id) {
        return {
          ...item,
          isCollected: !isCollected,
          collects: isCollected ? Math.max(0, (item.collects || 0) - 1) : (item.collects || 0) + 1
        };
      }
      return item;
    });
    this.setData({ handbookList: updatedList });
    
    if (isCollected) {
      post(`/handbook/uncollect/${id}`)
        .then(() => {
          wx.showToast({ title: '取消收藏成功' });
        })
        .catch((err) => {
          console.error('取消收藏失败：', err);
          // 失败回滚
          if (!(err.data && err.data.code === 400)) {
            wx.showToast({ title: '操作失败', icon: 'none' });
          }
          this.getHandbookList();
        });
    } else {
      post(`/handbook/collect/${id}`)
        .then(() => {
          wx.showToast({ title: '收藏成功' });
        })
        .catch((err) => {
          console.error('收藏失败：', err);
          // 失败回滚
          if (!(err.data && err.data.code === 400)) {
            wx.showToast({ title: '操作失败', icon: 'none' });
          }
          this.getHandbookList();
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

  // 选择快速提示词
  selectQuickPrompt(e) {
    const prompt = e.currentTarget.dataset.prompt;
    this.setData({ aiPrompt: prompt });
  },

  // 显示风格选择器
  showStyleSelect() {
    this.setData({ showStylePicker: true });
  },

  // 隐藏风格选择器
  hideStyleSelect() {
    this.setData({ showStylePicker: false });
  },

  // 选择风格
  onStyleChange(e) {
    this.setData({ aiStyleIndex: e.detail.value });
  },

  // 显示心情选择器
  showMoodSelect() {
    this.setData({ showMoodPicker: true });
  },

  // 隐藏心情选择器
  hideMoodSelect() {
    this.setData({ showMoodPicker: false });
  },

  // 选择心情
  onMoodChange(e) {
    this.setData({ aiMoodIndex: e.detail.value });
  },

  // 生成AI图像 - 手账专属版本
  generateAIImage() {
    const { 
      aiPrompt, aiSizes, aiSizeIndex, 
      aiStyles, aiStyleIndex, 
      aiMoods, aiMoodIndex 
    } = this.data;
    
    if (!aiPrompt.trim()) {
      wx.showToast({ title: '请输入图像描述', icon: 'none' });
      return;
    }

    // 记录开始时间
    const startTime = Date.now();
    
    this.setData({ generatingImage: true, generatedImage: '' });

    const style = aiStyles[aiStyleIndex].key;
    const mood = aiMoods[aiMoodIndex].key;

    post('/image/generate-handbook', {
      prompt: aiPrompt,
      style: style,
      mood: mood,
      size: aiSizes[aiSizeIndex]
    })
      .then((result) => {
        if (result.data && result.data.image_url) {
          // 优先使用后端返回的真实生成时间
          let generateTime = result.data.generate_time;
          
          if (!generateTime) {
            // 如果后端没有返回，使用前端计算的时间
            const endTime = Date.now();
            generateTime = ((endTime - startTime) / 1000).toFixed(1);
          }
          
          this.setData({ 
            generatedImage: result.data.image_url,
            generatingImage: false 
          });
          
          wx.showToast({ 
            title: `图像已生成！耗时 ${generateTime}秒`, 
            icon: 'success',
            duration: 2500
          });
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

  // 轮询等待AI图片生成
  startPollingForAIImage(prompt, style, size) {
    let pollCount = 0;
    const maxPolls = 10;
    const pollInterval = 3000;

    const poll = () => {
      pollCount++;
      
      post('/image/generate-handbook', {
        prompt: prompt,
        style: style,
        size: size
      }).then((result) => {
        if (result.data && result.data.source === 'cogview_cached') {
          // 成功获取AI生成的图片
          this.setData({ 
            generatedImage: result.data.image_url 
          });
          wx.showToast({
            title: 'AI优化图片已就绪！',
            icon: 'success',
            duration: 1500
          });
        } else if (pollCount < maxPolls) {
          // 继续轮询
          setTimeout(poll, pollInterval);
        }
      }).catch(() => {
        // 轮询失败，不处理
      });
    };

    // 延迟开始轮询
    setTimeout(poll, pollInterval);
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
