const { get, post, put, del } = require('../../utils/request');
const { loginGuard } = require('../../utils/auth');

Page({
  data: {
    ingredientList: [],
    loading: true,
    searchKey: '',
    showDialog: false,
    isEdit: false,
    categories: ['蔬菜', '肉类', '水果', '主食', '豆制品', '调味品', '其他'],
    formData: {
      id: '',
      ingre_name: '',
      categoryIndex: 0,
      category: '',
      calorie: '',
      protein: '',
      carb: '',
      fat: '',
      stock: '',
      expire_date: ''
    }
  },

  // 页面加载
  onLoad(options) {
    if (!loginGuard()) return;
    
    // 立即显示默认数据，不等待网络请求
    this.setData({
      ingredientList: [],
      loading: false
    });
    
    // 延迟发起网络请求更新数据
    setTimeout(() => {
      this.getIngredientList();
    }, 100);
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.getIngredientList(() => {
      wx.stopPullDownRefresh();
    });
  },

  // 获取食材列表
  getIngredientList(callback) {
    get('/ingredient/search', { keyword: '' }, false)
      .then((result) => {
        this.setData({
          ingredientList: result.data.list || []
        });
        callback && callback();
      })
      .catch((err) => {
        console.error('获取食材列表失败：', err);
        callback && callback();
      });
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ searchKey: e.detail.value });
  },

  // 搜索食材
  searchIngredient() {
    const { searchKey } = this.data;
    
    get('/ingredient/search', { keyword: searchKey }, false)
      .then((result) => {
        this.setData({
          ingredientList: result.data.list || []
        });
      })
      .catch((err) => {
        console.error('搜索食材失败：', err);
        wx.showToast({ title: '搜索失败', icon: 'none' });
      });
  },

  // 显示添加弹窗
  showAddDialog() {
    // 重置表单
    this.setData({
      showDialog: true,
      isEdit: false,
      formData: {
        id: '',
        ingre_name: '',
        categoryIndex: 0,
        category: '',
        calorie: '',
        protein: '',
        carb: '',
        fat: '',
        stock: '',
        expire_date: ''
      }
    });
  },

  // 隐藏弹窗
  hideDialog() {
    this.setData({ showDialog: false });
  },

  // 编辑食材
  editIngredient(e) {
    const item = e.currentTarget.dataset.item;
    // 查找分类索引
    const categoryIndex = this.data.categories.findIndex(c => c === item.category);
    
    this.setData({
      showDialog: true,
      isEdit: true,
      formData: {
        id: item.id,
        ingre_name: item.ingre_name,
        categoryIndex: categoryIndex >= 0 ? categoryIndex : 0,
        category: item.category,
        calorie: item.calorie,
        protein: item.protein,
        carb: item.carb,
        fat: item.fat,
        stock: item.stock,
        expire_date: item.expire_date || ''
      }
    });
  },

  // 表单输入
  onFormInput(e) {
    const key = e.currentTarget.dataset.key;
    const value = e.detail.value;
    this.setData({
      [`formData.${key}`]: value
    });
  },

  // 选择分类
  onCategoryChange(e) {
    const index = e.detail.value;
    this.setData({
      'formData.categoryIndex': index,
      'formData.category': this.data.categories[index]
    });
  },

  // 选择日期
  onDateChange(e) {
    this.setData({
      'formData.expire_date': e.detail.value
    });
  },

  // 提交表单（添加/编辑）
  submitForm() {
    const { formData, isEdit, ingredientList } = this.data;
    
    // 校验必填项
    if (!formData.ingre_name) {
      wx.showToast({ title: '请输入食材名称', icon: 'none' });
      return;
    }
    if (!formData.calorie || isNaN(formData.calorie)) {
      wx.showToast({ title: '请输入有效热量值', icon: 'none' });
      return;
    }
    if (!formData.protein || isNaN(formData.protein)) {
      wx.showToast({ title: '请输入有效蛋白质值', icon: 'none' });
      return;
    }
    if (!formData.carb || isNaN(formData.carb)) {
      wx.showToast({ title: '请输入有效碳水值', icon: 'none' });
      return;
    }
    if (!formData.fat || isNaN(formData.fat)) {
      wx.showToast({ title: '请输入有效脂肪值', icon: 'none' });
      return;
    }

    // 构造请求参数
    const params = {
      ingre_name: formData.ingre_name,
      category: this.data.categories[formData.categoryIndex],
      calorie: Number(formData.calorie),
      protein: Number(formData.protein),
      carb: Number(formData.carb),
      fat: Number(formData.fat),
      stock: formData.stock ? Number(formData.stock) : 0,
      expire_date: formData.expire_date
    };

    // 编辑模式
    if (isEdit) {
      // 先更新本地数据（乐观更新）
      const updatedList = ingredientList.map(item => {
        if (item.id === formData.id) {
          return { ...item, ...params };
        }
        return item;
      });
      this.setData({ ingredientList: updatedList });
      this.hideDialog();
      
      put(`/ingredient/${formData.id}`, params)
        .then(() => {
          wx.showToast({ title: '保存成功' });
          // 成功后不再刷新列表，数据已经更新
        })
        .catch((err) => {
          console.error('编辑食材失败：', err);
          wx.showToast({ title: '保存失败', icon: 'none' });
          // 失败回滚
          this.getIngredientList();
        });
    } 
    // 添加模式
    else {
      // 先更新本地数据（乐观更新）
      const newIngredient = {
        id: Date.now(),
        ...params,
        create_time: new Date().toISOString()
      };
      const newList = [newIngredient, ...ingredientList];
      this.setData({ ingredientList: newList });
      this.hideDialog();
      
      post('/ingredient', params)
        .then((result) => {
          wx.showToast({ title: '添加成功' });
          // 用后端返回的真实数据更新临时数据
          if (result && result.data) {
            const updatedList = [result.data, ...ingredientList];
            this.setData({ ingredientList: updatedList });
          }
          // 不再调用 getIngredientList()
        })
        .catch((err) => {
          console.error('添加食材失败：', err);
          wx.showToast({ title: '添加失败', icon: 'none' });
          // 失败回滚
          this.getIngredientList();
        });
    }
  },

  // 删除食材
  deleteIngredient(e) {
    const id = e.currentTarget.dataset.id;
    const { ingredientList } = this.data;
    
    wx.showModal({
      title: '提示',
      content: '确定要删除该食材吗？',
      success: (res) => {
        if (res.confirm) {
          // 先从本地删除（乐观更新）
          const updatedList = ingredientList.filter(item => item.id !== id);
          this.setData({ ingredientList: updatedList });
          
          del(`/ingredient/${id}`)
            .then(() => {
              wx.showToast({ title: '删除成功' });
              // 不再刷新列表
            })
            .catch((err) => {
              console.error('删除食材失败：', err);
              wx.showToast({ title: '删除失败', icon: 'none' });
              // 失败回滚
              this.getIngredientList();
            });
        }
      }
    });
  },

  // 判断是否过期
  isExpired(dateStr) {
    if (!dateStr) return false;
    const expireDate = new Date(dateStr);
    const today = new Date();
    // 只比较日期，忽略时间
    expireDate.setHours(0, 0, 0, 0);
    today.setHours(0, 0, 0, 0);
    return expireDate < today;
  }
});