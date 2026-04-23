const { loginGuard } = require('../../utils/auth');

Page({
  data: {
    height: '',
    weight: '',
    age: '',
    genderIndex: 0,
    genderOptions: ['男', '女'],
    activityIndex: 2, // 默认中等活动
    activityOptions: [
      { name: '久坐', value: 1.2, desc: '几乎不运动' },
      { name: '轻度活动', value: 1.375, desc: '每周1-3次运动' },
      { name: '中度活动', value: 1.55, desc: '每周3-5次运动' },
      { name: '高度活动', value: 1.725, desc: '每周6-7次运动' },
      { name: '极高活动', value: 1.9, desc: '专业运动员' }
    ],
    showResult: false,
    bmi: '',
    bmiStatus: '',
    bmiStatusClass: '',
    bmiPercent: 0,
    bmr: '',
    tdee: '', // 每日总能量消耗
    bodyFat: '', // 体脂率
    idealWeight: '',
    dailyCalories: '',
    healthTips: [], // 健康建议
    historyList: []
  },

  onLoad(options) {
    if (!loginGuard()) return;
    this.loadHistory();
    this.loadUserInfo();
  },

  // 加载用户信息
  loadUserInfo() {
    const { get } = require('../../utils/request');
    get('/user/info', {}, false)
      .then((result) => {
        if (result && result.data) {
          const userInfo = result.data;
          this.setData({
            height: userInfo.height || '',
            weight: userInfo.weight || '',
            age: userInfo.age || '',
            genderIndex: userInfo.gender === '男' ? 0 : 1
          });
        }
      })
      .catch((err) => {
        console.error('获取用户信息失败：', err);
      });
  },

  onHeightInput(e) {
    this.setData({ height: e.detail.value });
  },

  onWeightInput(e) {
    this.setData({ weight: e.detail.value });
  },

  onAgeInput(e) {
    this.setData({ age: e.detail.value });
  },

  onGenderChange(e) {
    this.setData({ genderIndex: parseInt(e.detail.value) });
  },

  onActivityChange(e) {
    this.setData({ activityIndex: parseInt(e.detail.value) });
  },

  calculateHealth() {
    const { height, weight, age, genderIndex, activityIndex, activityOptions } = this.data;
    
    if (!height || !weight || !age) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      });
      return;
    }
    
    const h = parseFloat(height);
    const w = parseFloat(weight);
    const a = parseInt(age);
    const isMale = genderIndex === 0;
    const activityCoeff = activityOptions[activityIndex].value;
    
    if (h <= 0 || w <= 0 || a <= 0) {
      wx.showToast({
        title: '请输入有效的数值',
        icon: 'none'
      });
      return;
    }
    
    const heightInM = h / 100;
    const bmiValue = parseFloat((w / (heightInM * heightInM)).toFixed(1));
    
    // 1. 计算BMI状态
    let bmiStatus, bmiStatusClass, bmiPercent;
    if (bmiValue < 18.5) {
      bmiStatus = '偏瘦';
      bmiStatusClass = 'thin';
      bmiPercent = (bmiValue / 18.5) * 25;
    } else if (bmiValue < 24) {
      bmiStatus = '正常';
      bmiStatusClass = 'normal';
      bmiPercent = 25 + ((bmiValue - 18.5) / 5.5) * 25;
    } else if (bmiValue < 28) {
      bmiStatus = '偏胖';
      bmiStatusClass = 'overweight';
      bmiPercent = 50 + ((bmiValue - 24) / 4) * 25;
    } else {
      bmiStatus = '肥胖';
      bmiStatusClass = 'obese';
      bmiPercent = Math.min(75 + ((bmiValue - 28) / 10) * 25, 100);
    }
    
    // 2. 计算BMR（使用Mifflin-St Jeor公式，更准确！）
    let bmr;
    if (isMale) {
      bmr = Math.round(10 * w + 6.25 * h - 5 * a + 5);
    } else {
      bmr = Math.round(10 * w + 6.25 * h - 5 * a - 161);
    }
    
    // 3. 计算TDEE（每日总能量消耗）
    const tdee = Math.round(bmr * activityCoeff);
    
    // 4. 估算体脂率（用BMI估算）
    let bodyFat;
    if (isMale) {
      // 成年男性公式：1.20 * BMI + 0.23 * 年龄 - 16.2
      bodyFat = (1.20 * bmiValue + 0.23 * a - 16.2).toFixed(1);
    } else {
      // 成年女性公式：1.20 * BMI + 0.23 * 年龄 - 5.4
      bodyFat = (1.20 * bmiValue + 0.23 * a - 5.4).toFixed(1);
    }
    // 体脂率不能为负
    bodyFat = Math.max(5, parseFloat(bodyFat));
    
    // 5. 计算理想体重
    const idealWeightMin = Math.round(18.5 * heightInM * heightInM);
    const idealWeightMax = Math.round(23.9 * heightInM * heightInM);
    const idealWeight = `${idealWeightMin}-${idealWeightMax}`;
    
    // 6. 生成健康建议
    const healthTips = this.generateHealthTips(bmiValue, bmiStatus, isMale);
    
    this.setData({
      showResult: true,
      bmi: bmiValue,
      bmiStatus: bmiStatus,
      bmiStatusClass: bmiStatusClass,
      bmiPercent: bmiPercent.toFixed(0),
      bmr: bmr,
      tdee: tdee,
      bodyFat: bodyFat,
      idealWeight: idealWeight,
      dailyCalories: tdee,
      healthTips: healthTips
    });
    
    this.saveToHistory(bmiValue, bmiStatus, bmiStatusClass);
    
    wx.showToast({
      title: '计算完成',
      icon: 'success'
    });
  },

  saveToHistory(bmi, status, statusClass) {
    const today = new Date();
    const date = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    
    // 保存到数据库
    const { post } = require('../../utils/request');
    post('/health/index/record', {
      height: parseFloat(this.data.height),
      weight: parseFloat(this.data.weight),
      age: parseInt(this.data.age),
      gender: this.data.genderIndex,
      bmi: parseFloat(bmi),
      bmi_status: status,
      bmr: parseInt(this.data.bmr),
      ideal_weight: this.data.idealWeight,
      daily_calories: parseInt(this.data.dailyCalories),
      health_score: parseInt(this.calculateHealthScore())
    }, false)
      .then((result) => {
        if (result && result.code === 0) {
          console.log('健康指数记录保存成功');
        } else {
          console.error('健康指数记录保存失败：', result);
        }
      })
      .catch((err) => {
        console.error('健康指数记录保存失败：', err);
      });
    
    // 同时保存到本地存储作为备用
    const newRecord = {
      date: date,
      bmi: bmi,
      status: status,
      statusClass: statusClass
    };
    
    const historyList = wx.getStorageSync('healthHistory') || [];
    historyList.unshift(newRecord);
    
    const uniqueHistory = historyList.filter((item, index, self) =>
      index === self.findIndex(t => t.date === item.date)
    ).slice(0, 30);
    
    wx.setStorageSync('healthHistory', uniqueHistory);
    this.setData({ historyList: uniqueHistory });
  },

  loadHistory() {
    // 从数据库获取健康指数记录
    const { get } = require('../../utils/request');
    get('/health/index/record', { limit: 10 }, false)
      .then((result) => {
        if (result && result.data && result.data.list) {
          const historyList = result.data.list.map(item => ({
            date: item.create_time.split(' ')[0],
            bmi: item.bmi,
            status: item.bmi_status,
            statusClass: item.bmi_status === '正常' ? 'normal' : item.bmi_status === '偏瘦' ? 'thin' : item.bmi_status === '偏胖' ? 'overweight' : 'obese'
          }));
          this.setData({ historyList: historyList });
        }
      })
      .catch((err) => {
        console.error('获取健康指数记录失败：', err);
        // 从本地存储获取作为备用
        const historyList = wx.getStorageSync('healthHistory') || [];
        this.setData({ historyList: historyList.slice(0, 10) });
      });
  },

  calculateHealthScore() {
    // 计算健康分数
    const bmi = parseFloat(this.data.bmi);
    let healthScore = 0;
    
    // BMI 分数 (0-40)
    if (bmi >= 18.5 && bmi < 24) {
      healthScore += 40;
    } else if (bmi >= 17 && bmi < 18.5) {
      healthScore += 30;
    } else if (bmi >= 24 && bmi < 26) {
      healthScore += 30;
    } else if (bmi >= 16 && bmi < 17) {
      healthScore += 20;
    } else if (bmi >= 26 && bmi < 28) {
      healthScore += 20;
    } else {
      healthScore += 10;
    }
    
    return healthScore;
  },

  generateHealthTips(bmi, bmiStatus, isMale) {
    const tips = [];
    
    // 1. BMI相关建议
    if (bmiStatus === '偏瘦') {
      tips.push('💪 您的体重偏轻，建议适当增加营养摄入');
      tips.push('🥗 多吃富含蛋白质的食物，如鸡蛋、牛奶、鱼肉');
      tips.push('🏋️ 适当进行力量训练，增加肌肉量');
    } else if (bmiStatus === '正常') {
      tips.push('✅ 您的BMI在正常范围内，继续保持！');
      tips.push('🥦 保持均衡饮食，多吃蔬菜水果');
      tips.push('🏃 每周进行至少150分钟中等强度运动');
    } else if (bmiStatus === '偏胖') {
      tips.push('⚖️ 您的体重偏高，建议控制热量摄入');
      tips.push('🥗 减少精制碳水化合物，增加膳食纤维');
      tips.push('🏃 增加有氧运动，每周至少3-5次');
    } else {
      tips.push('⚠️ 您的体重过重，建议咨询专业医生');
      tips.push('🥗 控制饮食，减少高热量食物摄入');
      tips.push('🚶 从低强度运动开始，逐步增加活动量');
    }
    
    // 2. 通用建议
    tips.push('💧 每天喝足够的水，建议8杯以上');
    tips.push('😴 保证充足睡眠，每天7-8小时');
    tips.push('📊 定期监测体重和健康指标');
    
    return tips;
  }
});
