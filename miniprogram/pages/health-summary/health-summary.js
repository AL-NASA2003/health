const { loginGuard } = require('../../utils/auth');
const { getUserInfo } = require('../../utils/auth');
const { navigateTo } = require('../../utils/common');

Page({
  data: {
    currentDate: '',
    dietRecords: [],
    waterRecords: [],
    exerciseRecords: [],
    totalCalories: 0,
    totalWater: 0,
    totalExerciseCalories: 0,
    totalExerciseDuration: 0,
    netCalories: 0,
    userInfo: null,
    dailyCalorieGoal: 2000,
    dailyWaterGoal: 2000,
    bmi: null,
    bmiStatus: '',
    bmr: null,
    idealWeight: '',
    healthScore: 0
  },

  onLoad(options) {
    if (!loginGuard()) return;
    this.setCurrentDate();
    this.loadUserInfo();
    this.loadAllRecords();
    this.calculateHealth();
  },

  onShow() {
    this.loadAllRecords();
    this.calculateHealth();
  },

  setCurrentDate() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][today.getDay()];
    this.setData({
      currentDate: `${year}-${month}-${day} ${week}`
    });
  },

  loadUserInfo() {
    const userInfo = getUserInfo();
    this.setData({
      userInfo: userInfo,
      dailyCalorieGoal: userInfo?.daily_calorie || 2000
    });
  },

  loadAllRecords() {
    const today = new Date().toISOString().split('T')[0];
    
    // 加载饮食记录
    const dietData = wx.getStorageSync(`diet_${today}`);
    const dietRecords = dietData?.records || [];
    
    // 加载饮水记录
    const waterData = wx.getStorageSync(`water_${today}`);
    const waterRecords = waterData?.records || [];
    const totalWater = waterData?.totalAmount || 0;
    
    // 加载运动记录
    const exerciseData = wx.getStorageSync(`exercise_${today}`);
    const exerciseRecords = exerciseData?.records || [];
    
    // 计算总热量
    let totalCalories = 0;
    dietRecords.forEach(record => {
      totalCalories += record.calories || 0;
    });
    
    // 计算运动总热量消耗
    let totalExerciseCalories = 0;
    let totalExerciseDuration = 0;
    exerciseRecords.forEach(record => {
      totalExerciseCalories += record.totalCalories || 0;
      totalExerciseDuration += record.duration || 0;
    });
    
    // 计算净热量
    const netCalories = totalCalories - totalExerciseCalories;
    
    this.setData({
      dietRecords: dietRecords,
      waterRecords: waterRecords,
      exerciseRecords: exerciseRecords,
      totalCalories: totalCalories,
      totalWater: totalWater,
      totalExerciseCalories: totalExerciseCalories,
      totalExerciseDuration: totalExerciseDuration,
      netCalories: netCalories
    });
  },

  calculateHealth() {
    const userInfo = this.data.userInfo;
    if (!userInfo || !userInfo.height || !userInfo.weight) {
      return;
    }
    
    const height = parseFloat(userInfo.height);
    const weight = parseFloat(userInfo.weight);
    const age = parseInt(userInfo.age) || 30;
    const isMale = userInfo.gender === '男' || userInfo.gender === 1;
    
    // 计算 BMI
    const heightInM = height / 100;
    const bmiValue = (weight / (heightInM * heightInM)).toFixed(1);
    
    // BMI 状态
    let bmiStatus;
    if (bmiValue < 18.5) {
      bmiStatus = '偏瘦';
    } else if (bmiValue < 24) {
      bmiStatus = '正常';
    } else if (bmiValue < 28) {
      bmiStatus = '偏胖';
    } else {
      bmiStatus = '肥胖';
    }
    
    // 计算 BMR
    let bmr;
    if (isMale) {
      bmr = Math.round(88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age));
    } else {
      bmr = Math.round(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age));
    }
    
    // 理想体重
    const idealWeightMin = Math.round(18.5 * heightInM * heightInM);
    const idealWeightMax = Math.round(23.9 * heightInM * heightInM);
    const idealWeight = `${idealWeightMin}-${idealWeightMax}kg`;
    
    // 计算健康分数（0-100）
    let healthScore = 0;
    
    // BMI 分数 (0-40)
    if (bmiValue >= 18.5 && bmiValue < 24) {
      healthScore += 40;
    } else if (bmiValue >= 17 && bmiValue < 18.5) {
      healthScore += 30;
    } else if (bmiValue >= 24 && bmiValue < 26) {
      healthScore += 30;
    } else if (bmiValue >= 16 && bmiValue < 17) {
      healthScore += 20;
    } else if (bmiValue >= 26 && bmiValue < 28) {
      healthScore += 20;
    } else {
      healthScore += 10;
    }
    
    // 饮食热量 (0-20)
    const calorieProgress = this.data.netCalories / this.data.dailyCalorieGoal;
    if (calorieProgress >= 0.8 && calorieProgress <= 1.2) {
      healthScore += 20;
    } else if (calorieProgress >= 0.6 && calorieProgress <= 1.4) {
      healthScore += 15;
    } else if (calorieProgress >= 0.4 && calorieProgress <= 1.6) {
      healthScore += 10;
    } else {
      healthScore += 5;
    }
    
    // 饮水 (0-20)
    const waterProgress = this.data.totalWater / this.data.dailyWaterGoal;
    if (waterProgress >= 0.8) {
      healthScore += 20;
    } else if (waterProgress >= 0.6) {
      healthScore += 15;
    } else if (waterProgress >= 0.4) {
      healthScore += 10;
    } else {
      healthScore += 5;
    }
    
    // 运动 (0-20)
    if (this.data.totalExerciseDuration >= 30) {
      healthScore += 20;
    } else if (this.data.totalExerciseDuration >= 20) {
      healthScore += 15;
    } else if (this.data.totalExerciseDuration >= 10) {
      healthScore += 10;
    } else if (this.data.totalExerciseDuration > 0) {
      healthScore += 5;
    } else {
      healthScore += 0;
    }
    
    this.setData({
      bmi: bmiValue,
      bmiStatus: bmiStatus,
      bmr: bmr,
      idealWeight: idealWeight,
      healthScore: Math.min(healthScore, 100)
    });
  },

  goToRecords() {
    console.log('点击了我的记录');
    wx.switchTab({
      url: '/pages/records/records',
      success: function(res) {
        console.log('跳转成功', res);
      },
      fail: function(err) {
        console.log('跳转失败', err);
        wx.showToast({
          title: '跳转失败',
          icon: 'none'
        });
      }
    });
  },

  goToDiet() {
    wx.switchTab({
      url: '/pages/records/records'
    });
  },

  goToWater() {
    wx.navigateTo({
      url: '/pages/records/records'
    });
  },

  goToExercise() {
    wx.navigateTo({
      url: '/pages/records/records'
    });
  },

  goToHealth() {
    wx.navigateTo({
      url: '/pages/health/health'
    });
  }
});
