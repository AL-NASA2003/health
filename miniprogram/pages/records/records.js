const { get, post, put, del } = require('../../utils/request');
const { getUserInfo } = require('../../utils/storage');
const { loginGuard } = require('../../utils/auth');
const { loadMockData } = require('../../utils/mockData');

Page({
  data: {
    currentTab: 'diet', // diet, water, exercise
    currentDate: '',
    // 饮食记录相关数据
    totalCalories: 0,
    dietList: [],
    loading: true,
    searchKey: '',
    searchSuggest: [],
    showAddDialog: false,
    isEdit: false,
    editRecordId: null,
    foodTypes: ['饮品', '菜式', '主食', '水果', '零食'],
    mealTimes: ['早餐', '午餐', '晚餐', '加餐'],
    formData: {
      foodName: '',
      foodTypeIndex: 1,
      mealTimeIndex: 0,
      weight: '',
      ingredientId: ''
    },
    // 饮水记录相关数据
    waterRecords: [],
    totalWater: 0,
    dailyTarget: 2000,
    currentAmount: 0,
    progressPercent: 0,
    remainingAmount: 2000,
    customAmount: '',
    // 运动记录相关数据
    exerciseRecords: [],
    totalExerciseCalories: 0,
    totalExerciseDuration: 0,
    todayCalories: 0,
    todayDuration: 0,
    todayCount: 0,
    exerciseTypes: [
      { id: 1, name: '跑步', icon: '🏃', calories: 600, color: 'linear-gradient(135deg, #ff6b6b, #ee5a24)' },
      { id: 2, name: '快走', icon: '🚶', calories: 300, color: 'linear-gradient(135deg, #4ecdc4, #44a08d)' },
      { id: 3, name: '游泳', icon: '🏊', calories: 500, color: 'linear-gradient(135deg, #667eea, #764ba2)' },
      { id: 4, name: '骑行', icon: '🚴', calories: 450, color: 'linear-gradient(135deg, #f093fb, #f5576c)' },
      { id: 5, name: '跳绳', icon: '🏋️', calories: 700, color: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
      { id: 6, name: '瑜伽', icon: '🧘', calories: 250, color: 'linear-gradient(135deg, #fa709a, #fee140)' },
      { id: 7, name: '健身', icon: '💪', calories: 400, color: 'linear-gradient(135deg, #a18cd1, #fbc2eb)' },
      { id: 8, name: '篮球', icon: '🏀', calories: 550, color: 'linear-gradient(135deg, #ff9a9e, #fecfef)' }
    ],
    customName: '',
    customDuration: '',
    customCalories: ''
  },

  onLoad(options) {
    if (!loginGuard()) return;
    this.initDate();
    this.setCurrentDate();
    this.loadAllRecords();
  },

  onShow() {
    this.loadAllRecords();
  },

  initDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const currentDate = `${year}年${month}月${day}日`;
    this.setData({ currentDate });
  },

  setCurrentDate() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][today.getDay()];
    this.setData({
      currentDateForHeader: `${year}-${month}-${day} ${week}`
    });
  },

  goBack() {
    console.log('点击了返回按钮');
    wx.switchTab({
      url: '/pages/index/index',
      success: function(res) {
        console.log('返回首页成功', res);
      },
      fail: function(err) {
        console.log('返回首页失败', err);
      }
    });
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ currentTab: tab });
  },

  loadAllRecords() {
    // 加载饮食记录
    this.getDietList();
    
    // 加载饮水记录
    const today = new Date().toISOString().split('T')[0];
    const waterData = wx.getStorageSync(`water_${today}`);
    const waterRecords = waterData?.records || [];
    const totalWater = waterData?.totalAmount || 0;
    
    // 加载运动记录
    const exerciseData = wx.getStorageSync(`exercise_${today}`);
    const exerciseRecords = exerciseData?.records || [];
    
    // 计算运动总热量消耗
    let totalExerciseCalories = 0;
    let totalExerciseDuration = 0;
    exerciseRecords.forEach(record => {
      totalExerciseCalories += record.totalCalories || 0;
      totalExerciseDuration += record.duration || 0;
    });
    
    this.setData({
      waterRecords: waterRecords,
      totalWater: totalWater,
      currentAmount: totalWater,
      exerciseRecords: exerciseRecords,
      totalExerciseCalories: totalExerciseCalories,
      totalExerciseDuration: totalExerciseDuration
    });
    
    this.updateWaterProgress();
    this.updateExerciseStats();
  },

  // ========== 饮食记录相关函数 ==========
  calculateTotalCalories(dietList) {
    let total = 0;
    dietList.forEach(item => {
      total += item.calorie || 0;
    });
    this.setData({ totalCalories: total });
  },

  getDietList() {
    get('/diet/record', {}, false)
      .then((result) => {
        if (result && result.data && result.data.list) {
          const dietList = result.data.list;
          this.calculateTotalCalories(dietList);
          this.setData({
            dietList,
            loading: false
          });
        }
      })
      .catch((err) => {
        console.error('获取饮食记录失败：', err);
        this.loadMockData();
      });
  },

  loadMockData() {
    const mockData = loadMockData('dietRecord').map(item => ({
      id: item.id,
      food_name: item.ingredient_id === 1 ? '番茄' : '鸡蛋',
      food_type: '菜式',
      meal_time: item.meal_type,
      weight: item.weight,
      calorie: item.ingredient_id === 1 ? 30 : 155,
      protein: item.ingredient_id === 1 ? 1.8 : 13,
      carb: item.ingredient_id === 1 ? 7.8 : 1.1,
      fat: item.ingredient_id === 1 ? 0.4 : 11,
      create_time: new Date(item.create_time).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }));

    this.calculateTotalCalories(mockData);
    this.setData({
      dietList: mockData,
      loading: false
    });
  },

  onSearchInput(e) {
    const value = e.detail.value;
    this.setData({ searchKey: value });
    
    if (value) {
      get('/ingredient/search', { keyword: value })
        .then((result) => {
          this.setData({
            searchSuggest: result.data.list || []
          });
        })
        .catch((err) => {
          console.error('搜索食材失败：', err);
        });
    } else {
      this.setData({ searchSuggest: [] });
    }
  },

  selectIngredient(e) {
    const item = e.currentTarget.dataset.item;
    this.setData({
      searchKey: item.ingre_name,
      searchSuggest: [],
      'formData.foodName': item.ingre_name,
      'formData.ingredientId': item.id
    });
  },

  searchDiet() {
    const { searchKey } = this.data;
    if (!searchKey) {
      this.getDietList();
      return;
    }
    
    const filteredList = this.data.dietList.filter(item => 
      item.food_name.includes(searchKey)
    );
    
    this.setData({
      dietList: filteredList,
      loading: false
    });
  },

  showAddDialog() {
    this.setData({ showAddDialog: true });
  },

  showEditDialog(e) {
    const item = e.currentTarget.dataset.item;
    const foodTypeIndex = this.data.foodTypes.indexOf(item.food_type);
    const mealTimeIndex = this.data.mealTimes.indexOf(item.meal_time);
    
    this.setData({
      showAddDialog: true,
      isEdit: true,
      editRecordId: item.id,
      formData: {
        foodName: item.food_name,
        foodTypeIndex: foodTypeIndex >= 0 ? foodTypeIndex : 1,
        mealTimeIndex: mealTimeIndex >= 0 ? mealTimeIndex : 0,
        weight: item.weight.toString(),
        ingredientId: item.ingredient_id || ''
      }
    });
  },

  hideAddDialog() {
    this.setData({ 
      showAddDialog: false,
      isEdit: false,
      editRecordId: null,
      formData: {
        foodName: '',
        foodTypeIndex: 1,
        mealTimeIndex: 0,
        weight: '',
        ingredientId: ''
      }
    });
  },

  onFormInput(e) {
    const key = e.currentTarget.dataset.key;
    const value = e.detail.value;
    this.setData({
      [`formData.${key}`]: value
    });
  },

  onFoodTypeChange(e) {
    this.setData({
      'formData.foodTypeIndex': e.detail.value
    });
  },

  onMealTimeChange(e) {
    this.setData({
      'formData.mealTimeIndex': e.detail.value
    });
  },

  submitDietRecord() {
    const { formData, foodTypes, mealTimes, isEdit, editRecordId } = this.data;
    
    if (!formData.foodName) {
      wx.showToast({ title: '请输入食材名称', icon: 'none' });
      return;
    }
    
    if (!formData.weight) {
      wx.showToast({ title: '请输入食用量', icon: 'none' });
      return;
    }
    
    const weightRegex = /^\d+(\.\d+)?$/;
    if (!weightRegex.test(formData.weight)) {
      wx.showToast({ title: '请输入有效的数字', icon: 'none' });
      return;
    }
    
    const weight = Number(formData.weight);
    if (weight <= 0 || weight > 10000) {
      wx.showToast({ title: '请输入0-10000之间的食用量', icon: 'none' });
      return;
    }
    
    const params = {
      food_name: formData.foodName,
      food_type: foodTypes[formData.foodTypeIndex],
      meal_time: mealTimes[formData.mealTimeIndex],
      weight: weight
    };
    
    if (formData.ingredientId) {
      params.ingredient_id = formData.ingredientId;
    }
    
    if (isEdit && editRecordId) {
      put(`/diet/record/${editRecordId}`, params)
        .then((result) => {
          wx.showToast({ title: '更新成功' });
          this.hideAddDialog();
          this.getDietList();
        })
        .catch((err) => {
          console.error('更新饮食记录失败：', err);
          wx.showToast({ title: '更新失败', icon: 'none' });
        });
    } else {
      post('/diet/record', params)
        .then((result) => {
          wx.showToast({ title: '添加成功' });
          this.hideAddDialog();
          this.getDietList();
        })
        .catch((err) => {
          console.error('添加饮食记录失败：', err);
          wx.showToast({ title: '添加失败', icon: 'none' });
        });
    }
  },

  deleteDietRecord(e) {
    const id = e.currentTarget.dataset.id;
    
    wx.showModal({
      title: '提示',
      content: '确定要删除这条记录吗？',
      success: (res) => {
        if (res.confirm) {
          del(`/diet/record/${id}`)
            .then((result) => {
              wx.showToast({ title: '删除成功' });
              this.getDietList();
            })
            .catch((err) => {
              console.error('删除记录失败：', err);
              wx.showToast({ title: '删除失败', icon: 'none' });
            });
        }
      }
    });
  },

  // ========== 饮水记录相关函数 ==========
  updateWaterProgress() {
    const percent = Math.min((this.data.currentAmount / this.data.dailyTarget) * 100, 100);
    const remaining = Math.max(this.data.dailyTarget - this.data.currentAmount, 0);
    
    this.setData({
      progressPercent: percent.toFixed(0),
      remainingAmount: remaining
    });
  },

  saveWaterData() {
    const today = new Date().toISOString().split('T')[0];
    const data = {
      records: this.data.waterRecords,
      totalAmount: this.data.currentAmount
    };
    wx.setStorageSync(`water_${today}`, data);
  },

  addWater(e) {
    const amount = parseInt(e.currentTarget.dataset.amount);
    this.addWaterAmount(amount);
  },

  onCustomAmountInput(e) {
    this.setData({
      customAmount: e.detail.value
    });
  },

  addCustomWater() {
    const amount = parseInt(this.data.customAmount);
    
    if (!amount || amount <= 0) {
      wx.showToast({
        title: '请输入有效的水量',
        icon: 'none'
      });
      return;
    }
    
    this.addWaterAmount(amount);
    this.setData({ customAmount: '' });
  },

  addWaterAmount(amount) {
    const now = new Date();
    const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    
    const newRecord = {
      amount: amount,
      time: time
    };
    
    const newRecords = [newRecord, ...this.data.waterRecords];
    const newTotal = this.data.currentAmount + amount;
    
    this.setData({
      waterRecords: newRecords,
      currentAmount: newTotal,
      totalWater: newTotal
    });
    
    this.updateWaterProgress();
    this.saveWaterData();
    
    wx.showToast({
      title: `已添加 ${amount}ml`,
      icon: 'success'
    });
    
    if (newTotal >= this.data.dailyTarget && 
        newTotal - amount < this.data.dailyTarget) {
      setTimeout(() => {
        wx.showModal({
          title: '恭喜！',
          content: '您已完成今日饮水目标！',
          showCancel: false
        });
      }, 1000);
    }
  },

  deleteWaterRecord(e) {
    const index = e.currentTarget.dataset.index;
    const record = this.data.waterRecords[index];
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除这条 ${record.amount}ml 的记录吗？`,
      success: (res) => {
        if (res.confirm) {
          const today = new Date().toISOString().split('T')[0];
          const waterData = wx.getStorageSync(`water_${today}`) || { records: [], totalAmount: 0 };
          waterData.records.splice(index, 1);
          waterData.totalAmount = Math.max(0, waterData.totalAmount - record.amount);
          wx.setStorageSync(`water_${today}`, waterData);
          this.loadAllRecords();
          wx.showToast({ title: '删除成功', icon: 'success' });
        }
      }
    });
  },

  // ========== 运动记录相关函数 ==========
  updateExerciseStats() {
    let totalCalories = 0;
    let totalDuration = 0;
    
    this.data.exerciseRecords.forEach(record => {
      totalCalories += record.totalCalories;
      totalDuration += record.duration;
    });
    
    this.setData({
      todayCalories: totalCalories,
      todayDuration: totalDuration,
      todayCount: this.data.exerciseRecords.length
    });
  },

  addExercise(e) {
    const exerciseType = e.currentTarget.dataset.type;
    
    wx.showModal({
      title: `添加${exerciseType.name}`,
      editable: true,
      placeholderText: '请输入运动时长(分钟)',
      success: (res) => {
        if (res.confirm) {
          const duration = parseInt(res.content);
          if (!duration || duration <= 0) {
            wx.showToast({
              title: '请输入有效的时长',
              icon: 'none'
            });
            return;
          }
          
          this.addExerciseRecord(exerciseType, duration);
        }
      }
    });
  },

  onCustomNameInput(e) {
    this.setData({ customName: e.detail.value });
  },

  onCustomDurationInput(e) {
    this.setData({ customDuration: e.detail.value });
  },

  onCustomCaloriesInput(e) {
    this.setData({ customCalories: e.detail.value });
  },

  addCustomExercise() {
    const { customName, customDuration, customCalories } = this.data;
    
    if (!customName.trim()) {
      wx.showToast({
        title: '请输入运动名称',
        icon: 'none'
      });
      return;
    }
    
    const duration = parseInt(customDuration);
    if (!duration || duration <= 0) {
      wx.showToast({
        title: '请输入有效的时长',
        icon: 'none'
      });
      return;
    }
    
    const calories = parseInt(customCalories);
    if (!calories || calories <= 0) {
      wx.showToast({
        title: '请输入有效的热量消耗',
        icon: 'none'
      });
      return;
    }
    
    const customType = {
      name: customName,
      icon: '⚡',
      calories: calories,
      color: 'linear-gradient(135deg, #a8edea, #fed6e3)'
    };
    
    this.addExerciseRecord(customType, duration);
    
    this.setData({
      customName: '',
      customDuration: '',
      customCalories: ''
    });
  },

  addExerciseRecord(exerciseType, duration) {
    const now = new Date();
    const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    const totalCalories = Math.round((exerciseType.calories / 60) * duration);
    
    const newRecord = {
      name: exerciseType.name,
      icon: exerciseType.icon,
      color: exerciseType.color,
      duration: duration,
      caloriesPerHour: exerciseType.calories,
      totalCalories: totalCalories,
      time: time
    };
    
    const newRecords = [newRecord, ...this.data.exerciseRecords];
    
    this.setData({
      exerciseRecords: newRecords,
      totalExerciseCalories: this.data.totalExerciseCalories + totalCalories,
      totalExerciseDuration: this.data.totalExerciseDuration + duration
    });
    
    this.updateExerciseStats();
    this.saveExerciseData();
    
    wx.showToast({
      title: `已记录 ${exerciseType.name} ${duration}分钟`,
      icon: 'success'
    });
  },

  saveExerciseData() {
    const today = new Date().toISOString().split('T')[0];
    const data = {
      records: this.data.exerciseRecords
    };
    wx.setStorageSync(`exercise_${today}`, data);
  },

  deleteExerciseRecord(e) {
    const index = e.currentTarget.dataset.index;
    const record = this.data.exerciseRecords[index];
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除这条 ${record.name} 记录吗？`,
      success: (res) => {
        if (res.confirm) {
          const newRecords = [...this.data.exerciseRecords];
          newRecords.splice(index, 1);
          
          this.setData({
            exerciseRecords: newRecords,
            totalExerciseCalories: this.data.totalExerciseCalories - record.totalCalories,
            totalExerciseDuration: this.data.totalExerciseDuration - record.duration
          });
          
          this.updateExerciseStats();
          this.saveExerciseData();
          
          wx.showToast({
            title: '删除成功',
            icon: 'success'
          });
        }
      }
    });
  }
});
