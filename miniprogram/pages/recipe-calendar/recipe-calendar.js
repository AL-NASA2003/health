const { get, post } = require('../../utils/request');
const { loginGuard } = require('../../utils/auth');

Page({
  data: {
    currentYear: 2026,
    currentMonth: 3,
    weekDays: ['日', '一', '二', '三', '四', '五', '六'],
    calendarDays: [],
    selectedDate: '',
    dayRecipes: [],
    recommendRecipes: [],
    loadingRecommend: false,
    calendarRecipes: {}
  },

  onLoad(options) {
    if (!loginGuard()) return;
    
    // 立即初始化日历和显示默认数据，不等待网络请求
    this.initCalendar();
    this.loadCalendarRecipes();
    
    // 立即设置默认推荐食谱
    this.setData({
      recommendRecipes: [
        { id: 1, recipe_name: '健康沙拉', image: '', calorie: 350, cooking_time: 15 },
        { id: 2, recipe_name: '烤鸡胸肉', image: '', calorie: 420, cooking_time: 25 },
        { id: 3, recipe_name: '清蒸鱼', image: '', calorie: 380, cooking_time: 20 },
        { id: 4, recipe_name: '蔬菜炒饭', image: '', calorie: 450, cooking_time: 18 }
      ],
      loadingRecommend: false
    });
    
    // 延迟发起网络请求更新推荐食谱
    setTimeout(() => {
      this.loadRecommendRecipes();
    }, 100);
  },

  initCalendar() {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth() + 1;
    this.setData({
      currentYear: year,
      currentMonth: month
    });
    this.generateCalendarDays(year, month);
  },

  generateCalendarDays(year, month) {
    const firstDay = new Date(year, month - 1, 1);
    const lastDay = new Date(year, month, 0);
    const today = new Date();
    const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    
    const days = [];
    const startWeekDay = firstDay.getDay();
    
    for (let i = 0; i < startWeekDay; i++) {
      days.push({
        day: '',
        isEmpty: true,
        date: ''
      });
    }
    
    for (let i = 1; i <= lastDay.getDate(); i++) {
      const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
      const hasRecipe = this.data.calendarRecipes[dateStr] && this.data.calendarRecipes[dateStr].length > 0;
      
      days.push({
        day: i,
        date: dateStr,
        isToday: dateStr === todayStr,
        isSelected: dateStr === this.data.selectedDate,
        isEmpty: false,
        hasRecipe: hasRecipe
      });
    }
    
    this.setData({ calendarDays: days });
  },

  prevMonth() {
    let { currentYear, currentMonth } = this.data;
    currentMonth--;
    if (currentMonth < 1) {
      currentMonth = 12;
      currentYear--;
    }
    this.setData({ currentYear, currentMonth });
    this.generateCalendarDays(currentYear, currentMonth);
  },

  nextMonth() {
    let { currentYear, currentMonth } = this.data;
    currentMonth++;
    if (currentMonth > 12) {
      currentMonth = 1;
      currentYear++;
    }
    this.setData({ currentYear, currentMonth });
    this.generateCalendarDays(currentYear, currentMonth);
  },

  selectDay(e) {
    const date = e.currentTarget.dataset.date;
    if (!date) return;
    
    const dayRecipes = this.data.calendarRecipes[date] || [];
    
    this.setData({
      selectedDate: date,
      dayRecipes: dayRecipes
    });
    
    this.generateCalendarDays(this.data.currentYear, this.data.currentMonth);
  },

  loadRecommendRecipes() {
    get('/recipe/list', {}, false)
      .then((result) => {
        if (result && result.data && result.data.list) {
          this.setData({
            recommendRecipes: result.data.list.slice(0, 5)
          });
        }
      })
      .catch((err) => {
        console.error('获取推荐食谱失败：', err);
      });
  },

  loadCalendarRecipes() {
    const saved = wx.getStorageSync('calendarRecipes') || {};
    this.setData({ calendarRecipes: saved });
  },

  saveCalendarRecipes() {
    wx.setStorageSync('calendarRecipes', this.data.calendarRecipes);
  },

  addToCalendar(e) {
    const recipe = e.currentTarget.dataset.recipe;
    const { selectedDate } = this.data;
    
    if (!selectedDate) {
      wx.showToast({
        title: '请先选择日期',
        icon: 'none'
      });
      return;
    }
    
    const calendarRecipes = { ...this.data.calendarRecipes };
    if (!calendarRecipes[selectedDate]) {
      calendarRecipes[selectedDate] = [];
    }
    
    calendarRecipes[selectedDate].push({
      id: recipe.id,
      name: recipe.recipe_name,
      calories: recipe.calorie
    });
    
    this.setData({
      calendarRecipes: calendarRecipes,
      dayRecipes: calendarRecipes[selectedDate]
    });
    
    this.saveCalendarRecipes();
    this.generateCalendarDays(this.data.currentYear, this.data.currentMonth);
    
    wx.showToast({
      title: '已添加到日历',
      icon: 'success'
    });
  },

  viewRecipe(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/recipe-detail/recipe-detail?id=${id}`
    });
  },

  addRecipe() {
    wx.switchTab({
      url: '/pages/recipe/recipe'
    });
  }
});
