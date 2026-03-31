const { get, post } = require('../../utils/request');
const { loginGuard, logout } = require('../../utils/auth');
const { clearStorage } = require('../../utils/storage');

Page({
  data: {
    userInfo: null,
    loading: true
  },

  // 页面加载
  onLoad(options) {
    if (!loginGuard()) return;
    
    // 立即显示默认数据
    this.setData({
      loading: false,
      userInfo: {
        id: 1,
        nickname: '测试用户',
        avatar: '',
        phone: '',
        daily_calorie: 2000,
        health_goal: '健康生活'
      }
    });
    
    // 延迟发起网络请求更新数据
    setTimeout(() => {
      this.getUserInfo();
    }, 100);
  },

  // 获取用户信息
  getUserInfo() {
    get('/user/info', {}, false)
      .then((result) => {
        if (result && result.data) {
          this.setData({
            userInfo: result.data
          });
        }
      })
      .catch((err) => {
        console.error('获取用户信息失败：', err);
        // 保持默认数据
      });
  },

  // 跳转到收藏页面
  goToCollection() {
    wx.navigateTo({
      url: '/pages/user/collection/collection'
    });
  },

  // 跳转到点赞页面
  goToLike() {
    wx.navigateTo({
      url: '/pages/user/like/like'
    });
  },

  // 跳转到手账页面
  goToHandbook() {
    wx.navigateTo({
      url: '/pages/handbook/handbook'
    });
  },

  // 跳转到论坛页面
  goToForum() {
    wx.navigateTo({
      url: '/pages/forum/forum'
    });
  },

  // 跳转到健康汇总页面
  goToHealthSummary() {
    wx.navigateTo({
      url: '/pages/health-summary/health-summary'
    });
  },

  // 跳转到完善个人信息页面
  goToEditProfile() {
    wx.navigateTo({
      url: '/pages/user/edit-profile/edit-profile'
    });
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          logout();
          clearStorage();
          wx.redirectTo({
            url: '/pages/login/login'
          });
        }
      }
    });
  }
});
