const { get, post } = require('../../utils/request');
const { loginGuard } = require('../../utils/auth');
const cache = require('../../utils/cache');
const { loadFromCache, showToast, navigateTo } = require('../../utils/common');

Page({
  data: {
    hotFoodList: [],
    loading: true,
    skeletonShow: true
  },

  // 页面加载
  onLoad(options) {
    // 不强制登录验证，热点美食可以匿名查看
    const cachedData = cache.get('hotfood:list');
    if (cachedData && cachedData.length > 0) {
      // 有缓存数据，立即显示，不等待网络请求
      this.setData({
        hotFoodList: cachedData,
        loading: false,
        skeletonShow: false
      });
    } else {
      // 没有缓存数据，立即显示默认数据
      this.loadMockData();
    }
    
    // 延迟发起网络请求更新数据，避免阻塞页面显示
    setTimeout(() => {
      this.getHotFoodList();
    }, 100);
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.getHotFoodList(() => {
      wx.stopPullDownRefresh();
    });
  },

  // 优先从缓存加载
  loadFromCacheFirst() {
    const cachedData = cache.get('hotfood:list');
    if (cachedData && cachedData.length > 0) {
      this.setData({
        hotFoodList: cachedData,
        loading: false,
        skeletonShow: false
      });
    }
  },

  // 获取热点美食列表
  getHotFoodList(callback) {
    // 不显示loading，因为已经立即显示了默认数据
    get('/hotfood/list', {}, false, true)
      .then((result) => {
        if (result && result.data && result.data.list) {
          const hotFoodList = result.data.list;
          this.setData({
            hotFoodList: hotFoodList
          });
          // 缓存数据
          cache.set('hotfood:list', hotFoodList, 30 * 60 * 1000);
        }
        callback && callback();
      })
      .catch((err) => {
        console.error('获取热点美食失败：', err);
        // 保持默认数据，不做任何处理
        callback && callback();
      });
  },

  // 加载模拟数据
  loadMockData() {
    const today = new Date().toLocaleDateString('zh-CN');
    const mockData = [
      {
        id: 1,
        title: '春季养生汤品推荐：银耳莲子汤',
        desc: '滋阴润肺，适合春季养生',
        likes: 1234,
        source: '小红书',
        link: '',
        tags: ['养生', '汤品'],
        image: '',
        create_time: today
      },
      {
        id: 2,
        title: '低脂减肥餐食谱分享：一周不重样',
        desc: '健康减肥，营养均衡',
        likes: 2345,
        source: '小红书',
        link: '',
        tags: ['减肥', '低脂'],
        image: '',
        create_time: today
      },
      {
        id: 3,
        title: '高蛋白健身餐制作指南',
        desc: '增肌必备，简单易做',
        likes: 1890,
        source: '小红书',
        link: '',
        tags: ['健身', '高蛋白'],
        image: '',
        create_time: today
      },
      {
        id: 4,
        title: '宝宝辅食：营养蔬菜泥',
        desc: '适合6个月以上宝宝',
        likes: 987,
        source: '小红书',
        link: '',
        tags: ['辅食', '营养'],
        image: '',
        create_time: today
      },
      {
        id: 5,
        title: '懒人快手菜：15分钟搞定晚餐',
        desc: '上班族必备，简单美味',
        likes: 3456,
        source: '小红书',
        link: '',
        tags: ['快手菜', '晚餐'],
        image: '',
        create_time: today
      }
    ];

    // 确保先隐藏任何加载弹窗
    wx.hideLoading();
    
    this.setData({
      hotFoodList: mockData,
      loading: false,
      skeletonShow: false
    });
    
    // 缓存模拟数据
    cache.set('hotfood:list', mockData, 30 * 60 * 1000);
  },

  // 刷新热点数据
  refreshHotFood() {
    this.getHotFoodList(() => {
      showToast('刷新成功');
    });
  },

  // 手动爬取热点数据
  manualCrawl() {
    wx.showModal({
      title: '提示',
      content: '确认爬取最新热点美食数据吗？',
      success: (res) => {
        if (res.confirm) {
          this.setData({ loading: true });
          
          post('/hotfood/crawl')
            .then(() => {
              showToast('爬取任务已启动');
              // 先关闭loading
              this.setData({ loading: false });
              // 再刷新列表
              this.getHotFoodList();
            })
            .catch((err) => {
              console.error('爬取热点美食失败：', err);
              this.setData({ loading: false });
              showToast('爬取失败', 'none');
            });
        }
      }
    });
  },

  // 打开原文链接
  openLink(e) {
    const link = e.currentTarget.dataset.link;
    if (!link) {
      showToast('暂无链接', 'none');
      return;
    }

    // 在小程序中打开外部链接
    navigateTo(`/pages/webview/webview?url=${encodeURIComponent(link)}`);
  }
});