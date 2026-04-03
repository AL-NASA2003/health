const { get, post, put } = require('../../../utils/request');
const { loginGuard } = require('../../../utils/auth');
const { setUserInfo } = require('../../../utils/storage');

Page({
  data: {
    userInfo: {
      avatar: '',
      nickname: '',
      height: '',
      weight: '',
      age: '',
      gender: '',
      goal: ''
    },
    goalTypes: ['减脂', '增肌', '维持现状', '改善体质'],
    goalIndex: 0,
    bodyTypes: ['苗条型', '匀称型', '健硕型', '丰满型'],
    bodyTypeIndex: 0,
    loading: false
  },

  // 页面加载
  onLoad(options) {
    if (!loginGuard()) return;
    this.getUserInfo();
  },

  // 获取用户信息
  getUserInfo() {
    this.setData({ loading: true });
    
    get('/user/info')
      .then((result) => {
        const userInfo = result.data || {};
        this.setData({
          userInfo: {
            avatar: userInfo.avatar || '',
            nickname: userInfo.nickname || '',
            height: userInfo.height || '',
            weight: userInfo.weight || '',
            waist: userInfo.waist || '',
            hip: userInfo.hip || '',
            age: userInfo.age || '',
            gender: userInfo.gender || '',
            goal: userInfo.goal || ''
          },
          goalIndex: this.data.goalTypes.indexOf(userInfo.goal || '减脂'),
          bodyTypeIndex: 0, // 默认值，实际项目中应该从后端获取
          loading: false
        });
      })
      .catch((err) => {
        console.error('获取用户信息失败：', err);
        this.setData({ loading: false });
        wx.showToast({ title: '获取用户信息失败', icon: 'none' });
      });
  },

  // 选择头像
  chooseAvatar() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePaths = res.tempFilePaths;
        if (tempFilePaths && tempFilePaths.length > 0) {
          this.uploadAvatar(tempFilePaths[0]);
        }
      },
      fail: (err) => {
        console.error('选择头像失败：', err);
      }
    });
  },

  // 上传头像
  uploadAvatar(tempFilePath) {
    wx.showLoading({ title: '上传中...' });
    
    wx.uploadFile({
      url: 'http://localhost:5000/api/upload/image',
      filePath: tempFilePath,
      name: 'file',
      success: (res) => {
        wx.hideLoading();
        try {
          const result = JSON.parse(res.data);
          if (result.code === 0) {
            this.setData({
              'userInfo.avatar': result.data.url
            });
            wx.showToast({ title: '头像上传成功', icon: 'success' });
          } else {
            wx.showToast({ title: '上传失败', icon: 'none' });
          }
        } catch (e) {
          wx.showToast({ title: '上传失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('上传头像失败：', err);
        wx.showToast({ title: '上传失败', icon: 'none' });
      }
    });
  },

  // 选择微信头像
  onChooseAvatar(e) {
    const { avatarUrl } = e.detail;
    this.setData({
      'userInfo.avatar': avatarUrl
    });
    wx.showToast({ title: '头像选择成功', icon: 'success' });
  },

  // 昵称输入
  onNicknameInput(e) {
    this.setData({
      'userInfo.nickname': e.detail.value
    });
  },

  // 身高输入
  onHeightInput(e) {
    this.setData({
      'userInfo.height': e.detail.value
    });
  },

  // 体重输入
  onWeightInput(e) {
    this.setData({
      'userInfo.weight': e.detail.value
    });
  },

  // 腰围输入
  onWaistInput(e) {
    this.setData({
      'userInfo.waist': e.detail.value
    });
  },

  // 臀围输入
  onHipInput(e) {
    this.setData({
      'userInfo.hip': e.detail.value
    });
  },

  // 年龄输入
  onAgeInput(e) {
    this.setData({
      'userInfo.age': e.detail.value
    });
  },

  // 选择性别
  selectGender(e) {
    this.setData({
      'userInfo.gender': e.currentTarget.dataset.gender
    });
  },

  // 健康目标选择
  onGoalChange(e) {
    const index = e.detail.value;
    this.setData({
      goalIndex: index,
      'userInfo.goal': this.data.goalTypes[index]
    });
  },

  // 目标身材选择
  onBodyTypeChange(e) {
    this.setData({
      bodyTypeIndex: e.detail.value
    });
  },

  // 保存修改
  saveProfile() {
    const { userInfo } = this.data;
    
    // 验证表单
    if (!userInfo.nickname) {
      wx.showToast({ title: '请输入昵称', icon: 'none' });
      return;
    }
    
    if (!userInfo.height || !userInfo.weight || !userInfo.age) {
      wx.showToast({ title: '请填写身高、体重和年龄', icon: 'none' });
      return;
    }
    
    if (!userInfo.gender) {
      wx.showToast({ title: '请选择性别', icon: 'none' });
      return;
    }
    
    this.setData({ loading: true });
    
    // 构造更新数据
    const updateData = {
      avatar: userInfo.avatar,
      nickname: userInfo.nickname,
      height: parseFloat(userInfo.height),
      weight: parseFloat(userInfo.weight),
      waist: parseFloat(userInfo.waist) || 0,
      hip: parseFloat(userInfo.hip) || 0,
      age: parseInt(userInfo.age),
      gender: userInfo.gender,
      health_goal: userInfo.goal,
      body_type: this.data.bodyTypes[this.data.bodyTypeIndex]
    };
    
    // 调用后端接口更新用户信息
    // 使用PUT方法请求/api/user/info接口
    put('/user/info', updateData)
      .then((result) => {
        this.setData({ loading: false });
        
        if (result.code === 0) {
          // 保存用户目标到数据库
          post('/health/goal', {
            daily_calorie_goal: 2000, // 默认值，实际项目中应该根据用户信息计算
            daily_water_goal: 2000, // 默认值
            daily_exercise_goal: 30, // 默认值
            health_goal: userInfo.goal,
            dietary_preference: '清淡' // 默认值，实际项目中应该让用户选择
          }, false)
            .then((goalResult) => {
              if (goalResult && goalResult.code === 0) {
                console.log('用户目标保存成功');
              } else {
                console.error('用户目标保存失败：', goalResult);
              }
            })
            .catch((err) => {
              console.error('用户目标保存失败：', err);
            });
          
          // 重新获取更新后的用户信息
          get('/user/info')
            .then((userResult) => {
              if (userResult.data) {
                // 更新本地存储
                setUserInfo(userResult.data);
                wx.showToast({ title: '保存成功', icon: 'success' });
                // 返回上一页
                setTimeout(() => {
                  wx.navigateBack();
                }, 1500);
              }
            })
            .catch((err) => {
              console.error('获取用户信息失败：', err);
              wx.showToast({ title: '保存成功', icon: 'success' });
              // 返回上一页
              setTimeout(() => {
                wx.navigateBack();
              }, 1500);
            });
        } else {
          wx.showToast({ title: result.msg || '保存失败', icon: 'none' });
        }
      })
      .catch((err) => {
        console.error('保存失败：', err);
        this.setData({ loading: false });
        wx.showToast({ title: '保存失败', icon: 'none' });
      });
  }
});