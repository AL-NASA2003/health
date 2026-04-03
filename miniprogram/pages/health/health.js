const { loginGuard } = require('../../utils/auth');

Page({
  data: {
    height: '',
    weight: '',
    age: '',
    genderIndex: 0,
    genderOptions: ['男', '女'],
    showResult: false,
    bmi: '',
    bmiStatus: '',
    bmiStatusClass: '',
    bmiPercent: 0,
    bmr: '',
    idealWeight: '',
    dailyCalories: '',
    historyList: []
  },

  onLoad(options) {
    if (!loginGuard()) return;
    this.loadHistory();
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

  calculateHealth() {
    const { height, weight, age, genderIndex } = this.data;
    
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
    
    if (h <= 0 || w <= 0 || a <= 0) {
      wx.showToast({
        title: '请输入有效的数值',
        icon: 'none'
      });
      return;
    }
    
    const heightInM = h / 100;
    const bmiValue = (w / (heightInM * heightInM)).toFixed(1);
    
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
    
    let bmr;
    if (isMale) {
      bmr = Math.round(88.362 + (13.397 * w) + (4.799 * h) - (5.677 * a));
    } else {
      bmr = Math.round(447.593 + (9.247 * w) + (3.098 * h) - (4.330 * a));
    }
    
    const idealWeightMin = Math.round(18.5 * heightInM * heightInM);
    const idealWeightMax = Math.round(23.9 * heightInM * heightInM);
    const idealWeight = `${idealWeightMin}-${idealWeightMax}`;
    
    const dailyCalories = Math.round(bmr * 1.55);
    
    this.setData({
      showResult: true,
      bmi: bmiValue,
      bmiStatus: bmiStatus,
      bmiStatusClass: bmiStatusClass,
      bmiPercent: bmiPercent.toFixed(0),
      bmr: bmr,
      idealWeight: idealWeight,
      dailyCalories: dailyCalories
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
  }
});
