const { post } = require('../../utils/request');
const { setToken, setUserInfo } = require('../../utils/storage');

Page({
  data: {
    canIUseGetUserProfile: true,
    isDev: true,
    loginType: 'wechat', // wechat or phone or test
    phoneLoginType: 'sms', // sms or password
    phone: '',
    smsCode: '',
    password: '',
    countdown: 0
  },

  onLoad(options) {
    const token = wx.getStorageSync('token');
    if (token) {
      wx.switchTab({
        url: '/pages/index/index'
      });
    }
  },

  // 切换登录方式
  switchLoginType(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      loginType: type
    });
  },

  // 切换手机号登录方式
  switchPhoneLoginType(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      phoneLoginType: type
    });
  },

  // 手机号输入
  onPhoneInput(e) {
    this.setData({
      phone: e.detail.value
    });
  },

  // 验证码或密码输入
  onCodeInput(e) {
    if (this.data.phoneLoginType === 'sms') {
      this.setData({
        smsCode: e.detail.value
      });
    } else {
      this.setData({
        password: e.detail.value
      });
    }
  },

  // 发送验证码
  sendSmsCode() {
    const { phone } = this.data;
    
    // 验证手机号
    if (!phone || phone.length !== 11) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      });
      return;
    }

    // 模拟发送验证码
    wx.showToast({
      title: '验证码已发送',
      icon: 'success'
    });

    // 开始倒计时
    this.setData({ countdown: 60 });
    const timer = setInterval(() => {
      const { countdown } = this.data;
      if (countdown <= 1) {
        clearInterval(timer);
        this.setData({ countdown: 0 });
      } else {
        this.setData({ countdown: countdown - 1 });
      }
    }, 1000);
  },

  // 手机号登录
  phoneLogin() {
    const { phone, phoneLoginType, smsCode, password } = this.data;

    // 验证手机号
    if (!phone || phone.length !== 11) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      });
      return;
    }

    // 验证验证码或密码
    if (phoneLoginType === 'sms') {
      if (!smsCode || smsCode.length !== 6) {
        wx.showToast({
          title: '请输入6位验证码',
          icon: 'none'
        });
        return;
      }
    } else {
      if (!password || password.length < 6) {
        wx.showToast({
          title: '密码长度至少6位',
          icon: 'none'
        });
        return;
      }
    }

    wx.showLoading({
      title: '登录中...'
    });

    // 模拟登录
    setTimeout(() => {
      wx.hideLoading();
      this.mockLogin();
    }, 1000);
  },

  // 微信登录
  wxLogin() {
    wx.showLoading({
      title: '登录中...'
    });

    wx.login({
      success: (res) => {
        if (res.code) {
          this.doLogin(res.code);
        } else {
          wx.hideLoading();
          wx.showToast({
            title: '获取登录凭证失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('微信登录失败：', err);
        this.mockLogin();
      }
    });
  },

  doLogin(code) {
    post('/user/login', { code: code }, false)
      .then((result) => {
        wx.hideLoading();
        
        if (result && result.data) {
          const { token, user_info } = result.data;
          if (token) {
            setToken(token);
            setUserInfo(user_info || {});
            getApp().updateUserInfo(user_info || {});
            
            // 快速跳转，不等待toast
            wx.switchTab({
              url: '/pages/index/index'
            });
          } else {
            this.mockLogin();
          }
        } else {
          this.mockLogin();
        }
      })
      .catch((err) => {
        wx.hideLoading();
        console.error('登录失败：', err);
        this.mockLogin();
      });
  },

  // 跳转到注册页面
  goToRegister() {
    wx.navigateTo({
      url: '/pages/register/register'
    });
  },

  // 忘记密码
  forgotPassword() {
    wx.showToast({
      title: '忘记密码功能开发中',
      icon: 'none'
    });
  },

  // 测试账号登录
  testLogin() {
    wx.showLoading({
      title: '登录中...'
    });

    post('/user/login', { 
      username: 'test', 
      password: '123456' 
    }, false)
      .then((result) => {
        wx.hideLoading();
        
        if (result && result.data) {
          const { token, user_info } = result.data;
          if (token) {
            setToken(token);
            setUserInfo(user_info || {});
            getApp().updateUserInfo(user_info || {});
            
            wx.showToast({
              title: '登录成功！',
              icon: 'success'
            });
            
            setTimeout(() => {
              wx.switchTab({
                url: '/pages/index/index'
              });
            }, 1000);
          } else {
            wx.showToast({
              title: '登录失败',
              icon: 'none'
            });
          }
        } else {
          wx.showToast({
            title: '登录失败',
            icon: 'none'
          });
        }
      })
      .catch((err) => {
        wx.hideLoading();
        console.error('测试账号登录失败：', err);
        wx.showToast({
          title: '登录失败',
          icon: 'none'
        });
      });
  },

  mockLogin() {
    const mockToken = 'mock_token_' + Date.now();
    const mockUserInfo = {
      id: 1,
      nickname: '测试用户',
      avatar: '',
      phone: '',
      daily_calorie: 2000,
      health_goal: '健康生活'
    };

    setToken(mockToken);
    setUserInfo(mockUserInfo);
    getApp().updateUserInfo(mockUserInfo);

    // 快速跳转，不等待toast
    wx.switchTab({
      url: '/pages/index/index'
    });
  }
});
