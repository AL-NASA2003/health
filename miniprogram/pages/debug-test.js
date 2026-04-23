// 调试版本：直接输出所有信息
Page({
  data: {
    testResults: []
  },

  onLoad() {
    this.addLog('🚀 调试页面加载');
    this.testAll();
  },

  async testAll() {
    this.addLog('🧪 开始测试');
    
    // 测试1：获取今天的记录
    await this.testGetDietRecords();
    
    // 测试2：添加一条测试记录
    await this.testAddDietRecord();
    
    // 测试3：再次获取记录
    await this.testGetDietRecords();
    
    this.addLog('✅ 所有测试完成');
  },

  async testGetDietRecords() {
    this.addLog('📥 测试获取饮食记录...');
    const today = new Date().toISOString().split('T')[0];
    
    try {
      // 直接用 wx.request，绕过我们的请求封装
      const result = await new Promise((resolve, reject) => {
        wx.request({
          url: 'http://localhost:5000/api/diet/record',
          method: 'GET',
          data: { start_date: today, end_date: today },
          header: {
            'Authorization': wx.getStorageSync('token') || ''
          },
          success: (res) => resolve(res),
          fail: (err) => reject(err)
        });
      });
      
      this.addLog('✅ 获取成功');
      this.addLog('📄 响应：' + JSON.stringify(result.data));
      this.addLog('📋 记录数：' + (result.data.data?.list?.length || 0));
      
    } catch (err) {
      this.addLog('❌ 获取失败');
      this.addLog('📄 错误：' + JSON.stringify(err));
    }
  },

  async testAddDietRecord() {
    this.addLog('📤 测试添加饮食记录...');
    
    try {
      // 直接用 wx.request，绕过我们的请求封装
      const result = await new Promise((resolve, reject) => {
        wx.request({
          url: 'http://localhost:5000/api/diet/record',
          method: 'POST',
          data: {
            food_name: '测试食物' + Date.now(),
            food_type: '菜式',
            meal_time: '午餐',
            weight: 100
          },
          header: {
            'Authorization': wx.getStorageSync('token') || ''
          },
          success: (res) => resolve(res),
          fail: (err) => reject(err)
        });
      });
      
      this.addLog('✅ 添加成功');
      this.addLog('📄 响应：' + JSON.stringify(result.data));
      
    } catch (err) {
      this.addLog('❌ 添加失败');
      this.addLog('📄 错误：' + JSON.stringify(err));
    }
  },

  addLog(msg) {
    console.log(msg);
    const newResults = [...this.data.testResults, msg];
    this.setData({ testResults: newResults });
  }
})