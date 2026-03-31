// 统一管理模拟数据

// 热点美食模拟数据
export const hotFoodMockData = [
  {
    id: 1,
    food_name: '日式拉面',
    ingre_list: '小麦面粉,猪骨汤,叉烧,鸡蛋,葱',
    link: 'https://www.xiaohongshu.com/explore/12345',
    hot_score: 12800,
    source: '小红书',
    tags: ['美食', '日式', '拉面'],
    image: 'https://picsum.photos/seed/ramen/300/200',
    create_time: new Date().toISOString()
  },
  {
    id: 2,
    food_name: '泰式冬阴功汤',
    ingre_list: '香茅,柠檬叶,辣椒,虾,椰奶',
    link: 'https://www.xiaohongshu.com/explore/12346',
    hot_score: 9500,
    source: '小红书',
    tags: ['美食', '泰式', '汤'],
    image: 'https://picsum.photos/seed/tom-yum/300/200',
    create_time: new Date().toISOString()
  },
  {
    id: 3,
    food_name: '意式番茄意面',
    ingre_list: '意大利面,番茄,洋葱,大蒜,橄榄油',
    link: 'https://www.xiaohongshu.com/explore/12347',
    hot_score: 8200,
    source: '小红书',
    tags: ['美食', '意式', '意面'],
    image: 'https://picsum.photos/seed/pasta/300/200',
    create_time: new Date().toISOString()
  },
  {
    id: 4,
    food_name: '中式红烧肉',
    ingre_list: '五花肉,酱油,料酒,冰糖,姜',
    link: 'https://www.xiaohongshu.com/explore/12348',
    hot_score: 15600,
    source: '小红书',
    tags: ['美食', '中式', '红烧肉'],
    image: 'https://picsum.photos/seed/braised-pork/300/200',
    create_time: new Date().toISOString()
  },
  {
    id: 5,
    food_name: '韩式烤肉',
    ingre_list: '牛肉,韩式辣酱,大蒜,芝麻,生菜',
    link: 'https://www.xiaohongshu.com/explore/12349',
    hot_score: 10300,
    source: '小红书',
    tags: ['美食', '韩式', '烤肉'],
    image: 'https://picsum.photos/seed/korean-bbq/300/200',
    create_time: new Date().toISOString()
  }
];

// 食谱模拟数据
export const recipeMockData = [
  {
    id: 1,
    recipe_name: '番茄鸡蛋面',
    ingre_list: '面条,番茄,鸡蛋,葱,盐,生抽',
    cook_step: '1. 准备材料\n2. 煮面条\n3. 炒番茄鸡蛋\n4. 混合拌匀',
    calorie: 320,
    protein: 12,
    carb: 45,
    fat: 10,
    flavor: '清淡',
    cook_type: '煮',
    suitable_crowd: '所有人群',
    image: 'https://picsum.photos/seed/tomato-egg-noodle/300/200',
    create_time: new Date().toISOString(),
    update_time: new Date().toISOString()
  },
  {
    id: 2,
    recipe_name: '宫保鸡丁',
    ingre_list: '鸡肉,花生,辣椒,蒜,姜,酱油,糖',
    cook_step: '1. 准备材料\n2. 腌制鸡肉\n3. 炒制\n4. 调味出锅',
    calorie: 380,
    protein: 25,
    carb: 15,
    fat: 25,
    flavor: '麻辣',
    cook_type: '炒',
    suitable_crowd: '成年人',
    image: 'https://picsum.photos/seed/kung-pao-chicken/300/200',
    create_time: new Date().toISOString(),
    update_time: new Date().toISOString()
  }
];

// 手账模拟数据
export const handbookMockData = [
  {
    id: 1,
    user_id: 1,
    title: '今日饮食记录',
    content: '今天吃了番茄鸡蛋面，感觉很健康',
    image: 'https://picsum.photos/seed/handbook1/300/200',
    create_time: new Date().toISOString(),
    update_time: new Date().toISOString()
  },
  {
    id: 2,
    user_id: 1,
    title: '健身日记',
    content: '今天做了30分钟有氧运动',
    image: 'https://picsum.photos/seed/handbook2/300/200',
    create_time: new Date().toISOString(),
    update_time: new Date().toISOString()
  }
];

// 论坛帖子模拟数据
export const forumPostMockData = [
  {
    id: 1,
    user_id: 1,
    title: '分享一个健康食谱',
    content: '这是我自己研发的健康食谱，大家可以试试',
    image: 'https://picsum.photos/seed/forum1/300/200',
    category: '健康饮食',
    likes: 10,
    views: 100,
    is_top: false,
    create_time: new Date().toISOString(),
    update_time: new Date().toISOString()
  },
  {
    id: 2,
    user_id: 2,
    title: '健身打卡',
    content: '坚持健身第30天，感觉很棒',
    image: 'https://picsum.photos/seed/forum2/300/200',
    category: '健身',
    likes: 20,
    views: 200,
    is_top: true,
    create_time: new Date().toISOString(),
    update_time: new Date().toISOString()
  }
];

// 用户食材模拟数据
export const userIngredientMockData = [
  {
    id: 1,
    user_id: 1,
    ingredient_id: 1,
    weight: 500,
    unit: 'g',
    create_time: new Date().toISOString(),
    update_time: new Date().toISOString()
  },
  {
    id: 2,
    user_id: 1,
    ingredient_id: 2,
    weight: 300,
    unit: 'g',
    create_time: new Date().toISOString(),
    update_time: new Date().toISOString()
  }
];

// 食材模拟数据
export const ingredientMockData = [
  {
    id: 1,
    ingre_name: '番茄',
    calorie: 15,
    protein: 0.9,
    carb: 3.9,
    fat: 0.2,
    category: '蔬菜',
    stock: 1000,
    unit: 'g',
    image: 'https://picsum.photos/seed/tomato/300/200',
    expire_date: new Date().toISOString()
  },
  {
    id: 2,
    ingre_name: '鸡蛋',
    calorie: 155,
    protein: 13,
    carb: 1.1,
    fat: 11,
    category: '蛋类',
    stock: 500,
    unit: 'g',
    image: 'https://picsum.photos/seed/egg/300/200',
    expire_date: new Date().toISOString()
  }
];

// 饮食记录模拟数据
export const dietRecordMockData = [
  {
    id: 1,
    user_id: 1,
    ingredient_id: 1,
    weight: 200,
    meal_type: '午餐',
    create_date: new Date().toISOString(),
    create_time: new Date().toISOString()
  },
  {
    id: 2,
    user_id: 1,
    ingredient_id: 2,
    weight: 100,
    meal_type: '早餐',
    create_date: new Date().toISOString(),
    create_time: new Date().toISOString()
  }
];

// 统一的模拟数据加载函数
export function loadMockData(type) {
  switch (type) {
    case 'hotFood':
      return hotFoodMockData;
    case 'recipe':
      return recipeMockData;
    case 'handbook':
      return handbookMockData;
    case 'forumPost':
      return forumPostMockData;
    case 'userIngredient':
      return userIngredientMockData;
    case 'ingredient':
      return ingredientMockData;
    case 'dietRecord':
      return dietRecordMockData;
    default:
      return [];
  }
}
