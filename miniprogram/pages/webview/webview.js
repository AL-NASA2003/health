Page({
  data: {
    url: ''
  },

  onLoad(options) {
    if (options.url) {
      // 如果有url参数，直接加载
      this.setData({
        url: decodeURIComponent(options.url)
      });
    } else if (options.search) {
      // 如果有search参数，跳转到小红书搜索
      const searchKeyword = decodeURIComponent(options.search);
      const xiaohongshuSearchUrl = `https://www.xiaohongshu.com/search_result?keyword=${encodeURIComponent(searchKeyword)}`;
      this.setData({
        url: xiaohongshuSearchUrl
      });
    } else {
      wx.showToast({ title: '链接无效', icon: 'none' });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }
  }
});