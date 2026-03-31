const { setToken, setUserInfo } = require('../../utils/storage');

Page({
  data: {
    // 注册步骤
    step: 1,
    // 表单数据
    phone: '',
    smsCode: '',
    password: '',
    confirmPassword: '',
    nickname: '',
    height: '',
    weight: '',
    age: '',
    gender: '',
    goalTypes: ['减脂', '增肌', '维持现状', '改善体质'],
    goalIndex: 0,
    // 验证码倒计时
    countdown: 0,
    // 开发模式
    isDev: true
  },

  onLoad() {
    // 尝试获取微信手机号
    this.getWechatPhone();
  },

  // 获取微信手机号
  getWechatPhone() {
    if (wx.getSetting) {
      wx.getSetting({
        success: (res) => {
          if (res.authSetting['scope.userPhoneNumber']) {
            wx.login({
              success: (loginRes) => {
                if (loginRes.code) {
                  // 这里可以调用后端接口获取手机号
                  // 模拟获取手机号
                  if (this.data.isDev) {
                    this.setData({
                      phone: '13800138000'
                    });
                  }
                }
              }
            });
          }
        }
      });
    }
  },

  // 手机号输入
  onPhoneInput(e) {
    this.setData({
      phone: e.detail.value
    });
  },

  // 验证码输入
  onSmsCodeInput(e) {
    this.setData({
      smsCode: e.detail.value
    });
  },

  // 密码输入
  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    });
  },

  // 确认密码输入
  onConfirmPasswordInput(e) {
    this.setData({
      confirmPassword: e.detail.value
    });
  },

  // 昵称输入
  onNicknameInput(e) {
    this.setData({
      nickname: e.detail.value
    });
  },

  // 身高输入
  onHeightInput(e) {
    this.setData({
      height: e.detail.value
    });
  },

  // 体重输入
  onWeightInput(e) {
    this.setData({
      weight: e.detail.value
    });
  },

  // 年龄输入
  onAgeInput(e) {
    this.setData({
      age: e.detail.value
    });
  },

  // 选择性别
  selectGender(e) {
    this.setData({
      gender: e.currentTarget.dataset.gender
    });
  },

  // 健康目标选择
  onGoalChange(e) {
    this.setData({
      goalIndex: e.detail.value
    });
  },

  // 发送验证码
  sendSmsCode() {
    const phone = this.data.phone;
    if (!phone || phone.length !== 11) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      });
      return;
    }

    // 模拟发送验证码
    if (this.data.isDev) {
      wx.showToast({
        title: '验证码已发送: 123456',
        icon: 'none'
      });
    } else {
      // 调用后端接口发送验证码
      wx.request({
        url: 'http://localhost:5000/api/auth/send-sms',
        method: 'POST',
        data: { phone },
        success: (res) => {
          if (res.data.code === 0) {
            wx.showToast({
              title: '验证码已发送',
              icon: 'success'
            });
          } else {
            wx.showToast({
              title: res.data.msg || '发送失败',
              icon: 'none'
            });
          }
        },
        fail: () => {
          wx.showToast({
            title: '发送失败',
            icon: 'none'
          });
        }
      });
    }

    // 开始倒计时
    this.setData({ countdown: 60 });
    const timer = setInterval(() => {
      this.setData({
        countdown: this.data.countdown - 1
      });
      if (this.data.countdown <= 0) {
        clearInterval(timer);
      }
    }, 1000);
  },

  // 下一步
  nextStep() {
    if (this.data.step === 1) {
      // 验证手机号和验证码
      const phone = this.data.phone;
      const smsCode = this.data.smsCode;

      if (!phone || phone.length !== 11) {
        wx.showToast({
          title: '请输入正确的手机号',
          icon: 'none'
        });
        return;
      }

      if (!smsCode || smsCode.length !== 6) {
        wx.showToast({
          title: '请输入正确的验证码',
          icon: 'none'
        });
        return;
      }

      // 验证验证码
      if (!this.data.isDev) {
        // 调用后端接口验证验证码
        wx.request({
          url: 'http://localhost:5000/api/auth/verify-sms',
          method: 'POST',
          data: { phone, sms_code: smsCode },
          success: (res) => {
            if (res.data.code === 0) {
              this.setData({ step: 2 });
            } else {
              wx.showToast({
                title: res.data.msg || '验证码错误',
                icon: 'none'
              });
            }
          },
          fail: () => {
            wx.showToast({
              title: '验证失败',
              icon: 'none'
            });
          }
        });
      } else {
        // 开发模式直接通过
        this.setData({ step: 2 });
      }
    } else if (this.data.step === 2) {
      // 验证密码
      const password = this.data.password;
      const confirmPassword = this.data.confirmPassword;

      if (!password || password.length < 6 || password.length > 20) {
        wx.showToast({
          title: '密码长度应在6-20位之间',
          icon: 'none'
        });
        return;
      }

      if (password !== confirmPassword) {
        wx.showToast({
          title: '两次输入的密码不一致',
          icon: 'none'
        });
        return;
      }

      this.setData({ step: 3 });
    }
  },

  // 上一步
  prevStep() {
    if (this.data.step > 1) {
      this.setData({ step: this.data.step - 1 });
    }
  },

  // 生成7位数用户ID
  generateUserId() {
    return Math.floor(1000000 + Math.random() * 9000000);
  },

  // 完成注册
  register() {
    // 验证所有信息
    const { nickname, height, weight, age, gender } = this.data;

    if (!nickname) {
      wx.showToast({
        title: '请输入昵称',
        icon: 'none'
      });
      return;
    }

    if (!height || !weight || !age) {
      wx.showToast({
        title: '请填写身高、体重和年龄',
        icon: 'none'
      });
      return;
    }

    if (!gender) {
      wx.showToast({
        title: '请选择性别',
        icon: 'none'
      });
      return;
    }

    // 生成用户ID
    const userId = this.generateUserId();
    const goal = this.data.goalTypes[this.data.goalIndex];

    // 构造注册数据
    const registerData = {
      phone: this.data.phone,
      password: this.data.password,
      nickname,
      height: parseFloat(height),
      weight: parseFloat(weight),
      age: parseInt(age),
      gender,
      goal,
      user_id: userId
    };

    if (this.data.isDev) {
      // 开发模式模拟注册成功
      wx.showToast({
        title: '注册成功',
        icon: 'success'
      });
      
      // 生成模拟token
      const mockToken = 'mock_token_' + Date.now();
      
      // 保存用户信息到本地
      const mockUserInfo = {
        ...registerData,
        id: userId,
        health_goal: goal
      };
      
      // 使用与登录相同的存储方法
      setToken(mockToken);
      setUserInfo(mockUserInfo);
      getApp().updateUserInfo(mockUserInfo);
      
      // 跳转到首页
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/index/index'
        });
      }, 1500);
    } else {
      // 调用后端注册接口
      wx.request({
        url: 'http://localhost:5000/api/auth/register',
        method: 'POST',
        data: registerData,
        success: (res) => {
          if (res.data.code === 0) {
            wx.showToast({
              title: '注册成功',
              icon: 'success'
            });
            
            // 保存用户信息到本地
            setToken(res.data.token);
            setUserInfo(res.data.data);
            getApp().updateUserInfo(res.data.data);
            
            // 跳转到首页
            setTimeout(() => {
              wx.switchTab({
                url: '/pages/index/index'
              });
            }, 1500);
          } else {
            wx.showToast({
              title: res.data.msg || '注册失败',
              icon: 'none'
            });
          }
        },
        fail: () => {
          wx.showToast({
            title: '注册失败',
            icon: 'none'
          });
        }
      });
    }
  },

  // 跳转到登录页面
  goToLogin() {
    wx.redirectTo({
      url: '/pages/login/login'
    });
  }
});