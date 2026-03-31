const { get, post, put, del } = require('../../../utils/request');
const { loginGuard } = require('../../../utils/auth');

Page({
  data: {
    handbookDetail: {},
    loading: true,
    showEditDialog: false,
    formData: {
      id: '',
      title: '',
      content: '',
      image: ''
    }
  },

  // 页面加载
  onLoad(options) {
    if (!loginGuard()) return;
    const handbookId = options.id;
    if (handbookId) {
      this.getHandbookDetail(handbookId);
    }
  },

  // 获取手账详情
  getHandbookDetail(handbookId) {
    this.setData({ loading: true });
    
    get(`/handbook/detail/${handbookId}`)
      .then((result) => {
        this.setData({
          handbookDetail: result.data || {},
          loading: false
        });
      })
      .catch((err) => {
        console.error('获取手账详情失败：', err);
        this.setData({ loading: false });
        wx.showToast({ title: '获取手账详情失败', icon: 'none' });
      });
  },

  // 显示编辑弹窗
  showEditDialog() {
    const { handbookDetail } = this.data;
    this.setData({
      showEditDialog: true,
      formData: {
        id: handbookDetail.id,
        title: handbookDetail.title,
        content: handbookDetail.content,
        image: handbookDetail.image
      }
    });
  },

  // 隐藏编辑弹窗
  hideEditDialog() {
    this.setData({ showEditDialog: false });
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
          this.setData({
            'formData.image': tempFilePaths[0]
          });
        }
      },
      fail: (err) => {
        console.error('选择图片失败：', err);
      }
    });
  },

  // 提交编辑
  submitEdit() {
    const { formData } = this.data;
    
    if (!formData.title) {
      wx.showToast({ title: '请输入标题', icon: 'none' });
      return;
    }
    if (!formData.content) {
      wx.showToast({ title: '请输入内容', icon: 'none' });
      return;
    }

    put(`/handbook/update/${formData.id}`, formData)
      .then(() => {
        wx.showToast({ title: '保存成功' });
        this.hideEditDialog();
        // 重新获取手账详情
        this.getHandbookDetail(formData.id);
      })
      .catch((err) => {
        console.error('更新手账失败：', err);
        wx.showToast({ title: '保存失败', icon: 'none' });
      });
  },

  // 点赞手账
  likeHandbook() {
    const { handbookDetail } = this.data;
    const isLiked = handbookDetail.is_liked;
    
    if (isLiked) {
      post(`/handbook/unlike/${handbookDetail.id}`)
        .then(() => {
          wx.showToast({ title: '取消点赞成功' });
          this.getHandbookDetail(handbookDetail.id);
        })
        .catch((err) => {
          console.error('取消点赞失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    } else {
      post(`/handbook/like/${handbookDetail.id}`)
        .then(() => {
          wx.showToast({ title: '点赞成功' });
          this.getHandbookDetail(handbookDetail.id);
        })
        .catch((err) => {
          console.error('点赞失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    }
  },

  // 收藏手账
  collectHandbook() {
    const { handbookDetail } = this.data;
    const isCollected = handbookDetail.is_collected;
    
    if (isCollected) {
      post(`/handbook/uncollect/${handbookDetail.id}`)
        .then(() => {
          wx.showToast({ title: '取消收藏成功' });
          this.getHandbookDetail(handbookDetail.id);
        })
        .catch((err) => {
          console.error('取消收藏失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    } else {
      post(`/handbook/collect/${handbookDetail.id}`)
        .then(() => {
          wx.showToast({ title: '收藏成功' });
          this.getHandbookDetail(handbookDetail.id);
        })
        .catch((err) => {
          console.error('收藏失败：', err);
          wx.showToast({ title: '操作失败', icon: 'none' });
        });
    }
  },

  // 删除手账
  deleteHandbook() {
    const { handbookDetail } = this.data;
    
    wx.showModal({
      title: '提示',
      content: '确定要删除该手账吗？',
      success: (res) => {
        if (res.confirm) {
          del(`/handbook/delete/${handbookDetail.id}`)
            .then(() => {
              wx.showToast({ title: '删除成功' });
              // 返回上一页
              wx.navigateBack();
            })
            .catch((err) => {
              console.error('删除手账失败：', err);
              wx.showToast({ title: '删除失败', icon: 'none' });
            });
        }
      }
    });
  }
});
