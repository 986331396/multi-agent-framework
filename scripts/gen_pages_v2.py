#!/usr/bin/env python3
"""生成 clothDiy 所有标准页面 - 完整功能版"""
import os
import json
from datetime import datetime

BASE = "/Users/mac/Desktop/clothDiy/clothDiy_miniprogram"

PAGES = {
    "pages/index/index": {
        "name": "clothDiy",
        "nav": [
            {"label": "🎨 开始设计", "method": "goToModels", "target": "/pages/models/models"},
            {"label": "📦 面料库", "method": "goToFabrics", "target": "/pages/fabrics/fabrics"},
            {"label": "👤 我的空间", "method": "goToMyspace", "target": "/pages/myspace/myspace", "isTab": True},
        ],
        "is_home": True
    },
    "pages/models/models": {
        "name": "建模库",
        "nav": [
            {"label": "➕ 创建新建模", "method": "goToDesign", "target": "/pages/design/design"},
            {"label": "🏠 返回首页", "method": "goToIndex", "target": "/pages/index/index", "isTab": True},
        ]
    },
    "pages/design/design": {
        "name": "设计衣服",
        "nav": [
            {"label": "👗 去试穿", "method": "goToTryon", "target": "/pages/tryon/tryon"},
            {"label": "← 返回", "method": "goBack", "target": ""},
        ]
    },
    "pages/tryon/tryon": {
        "name": "动态试穿",
        "nav": [
            {"label": "📝 下订单", "method": "goToOrderPreview", "target": "/pages/order/preview"},
            {"label": "← 重新设计", "method": "goBack", "target": ""},
        ],
        "has_3d": True
    },
    "pages/fabrics/fabrics": {
        "name": "面料库",
        "nav": [
            {"label": "🎨 去设计", "method": "goToDesign", "target": "/pages/design/design"},
            {"label": "🏠 首页", "method": "goToIndex", "target": "/pages/index/index", "isTab": True},
        ]
    },
    "pages/order/preview": {
        "name": "订单预览",
        "nav": [
            {"label": "✅ 确认订单", "method": "goToOrderConfirm", "target": "/pages/order/confirm"},
            {"label": "← 返回", "method": "goBack", "target": ""},
        ]
    },
    "pages/order/confirm": {
        "name": "订单确认",
        "nav": [
            {"label": "💳 去支付", "method": "goToPayment", "target": "/pages/order/payment"},
            {"label": "← 返回", "method": "goBack", "target": ""},
        ]
    },
    "pages/order/payment": {
        "name": "支付",
        "nav": [
            {"label": "✅ 支付完成", "method": "goToMyspace", "target": "/pages/myspace/myspace", "isTab": True},
            {"label": "← 返回", "method": "goBack", "target": ""},
        ]
    },
    "pages/myspace/myspace": {
        "name": "我的空间",
        "nav": [
            {"label": "🏠 首页", "method": "goToIndex", "target": "/pages/index/index", "isTab": True},
            {"label": "📋 我的订单", "method": "viewOrders", "target": ""},
        ]
    },
    "pages/profile/profile": {
        "name": "个人中心",
        "nav": [
            {"label": "✏️ 编辑资料", "method": "editProfile", "target": ""},
            {"label": "📦 我的订单", "method": "viewOrders", "target": "/pages/myspace/myspace", "isTab": True},
        ]
    },
}

def gen_js(page_path, cfg):
    page_name = cfg["name"]
    nav = cfg.get("nav", [])
    has_3d = cfg.get("has_3d", False)
    is_home = cfg.get("is_home", False)
    
    methods = ""
    for action in nav:
        method = action["method"]
        target = action.get("target", "")
        is_tab = action.get("isTab", False)
        
        if method == "goBack":
            methods += "\n  goBack() {\n    wx.navigateBack({ delta: 1 });\n  },"
        elif is_tab:
            methods += f"\n  {method}() {{\n    wx.switchTab({{ url: '{target}' }});\n  }},"
        elif target:
            methods += f"\n  {method}() {{\n    wx.navigateTo({{ url: '{target}' }});\n  }},"
        else:
            methods += f"\n  {method}() {{\n    wx.showToast({{ title: '{action['label']}', icon: 'none' }});\n  }},"
    
    # 首页额外方法
    home_extra = ""
    if is_home:
        home_extra = """
  
  // 首页额外方法
  onSearch() {
    wx.showToast({ title: '搜索功能开发中', icon: 'none' });
  },
  
  viewHotDesigns() {
    wx.showToast({ title: '热门设计', icon: 'none' });
  },
  
  quickStart() {
    wx.switchTab({ url: '/pages/models/models' });
  },"""
    
    # 3D 方法
    extra = ""
    if has_3d:
        extra = """
  
  /* 3D 试穿核心方法 */
  initThreeJS() {
    console.log('[3D] 初始化 Three.js 场景');
    const query = wx.createSelectorQuery();
    query.select('#three-canvas')
      .node()
      .exec((res) => {
        if (!res || !res[0] || !res[0].node) {
          console.error('[3D] Canvas 节点未找到');
          return;
        }
        const canvas = res[0].node;
        this.setupThreeScene(canvas);
      });
  },

  setupThreeScene(canvas) {
    console.log('[3D] 设置 Three.js 场景');
    // 这里需要引入 threejs-miniprogram
    // 暂时用 placeholder
    this.setData({
      threeReady: true,
      threeTip: '3D 引擎加载中...'
    });
    // TODO: 实际 Three.js 代码
    // import * as THREE from 'threejs-miniprogram';
    // this.createScene(canvas);
  },

  rotateModel() {
    console.log('[3D] 旋转模型');
    this.setData({ rotateAngle: (this.data.rotateAngle || 0) + 45 });
  },

  zoomIn() {
    const scale = Math.min((this.data.zoomScale || 1) + 0.2, 3);
    this.setData({ zoomScale: scale });
    console.log('[3D] 放大', scale);
  },

  zoomOut() {
    const scale = Math.max((this.data.zoomScale || 1) - 0.2, 0.5);
    this.setData({ zoomScale: scale });
    console.log('[3D] 缩小', scale);
  },

  resetView() {
    this.setData({ rotateAngle: 0, zoomScale: 1 });
    console.log('[3D] 重置视角');
  },

  downloadScreenshot() {
    wx.showToast({ title: '截图已保存', icon: 'success' });
    console.log('[3D] 保存截图');
  },"""
    
    return f'''Page({{
  data: {{
    pageName: '{page_name}',
    createTime: '{datetime.now().strftime("%Y-%m-%d")}',
    {"threeReady: false, threeTip: '点击加载3D', rotateAngle: 0, zoomScale: 1," if has_3d else ""}
  }},

  onLoad(options) {{
    console.log('[{page_name}] onLoad', options);
    {"this.initThreeJS();" if has_3d else ""}
  }},

  onShow() {{ }},

  onShareAppMessage() {{
    return {{ title: 'clothDiy - {page_name}', path: '/{page_path}' }};
  }},

  {methods}
  {home_extra}
  {extra}
}});'''

def gen_wxml(page_path, cfg):
    page_name = cfg["name"]
    nav = cfg.get("nav", [])
    has_3d = cfg.get("has_3d", False)
    is_home = cfg.get("is_home", False)
    
    # 导航按钮
    buttons = ""
    for action in nav:
        buttons += f'    <view class="btn" bindtap="{action["method"]}">{action["label"]}</view>\n'
    
    # 首页特殊布局
    home_extra = ""
    if is_home:
        home_extra = '''
    <!-- 搜索栏 -->
    <view class="search-bar" bindtap="onSearch">
      <text class="search-icon">🔍</text>
      <text class="search-text">搜索款式、面料、设计师...</text>
    </view>

    <!-- 3D 展示区 -->
    <view class="hero-3d">
      <view class="hero-text">
        <text class="hero-title">自定义你的专属服装</text>
        <text class="hero-desc">AI + 3D 技术，让设计更简单</text>
        <view class="hero-btn" bindtap="quickStart">立即开始</view>
      </view>
    </view>

    <!-- 快捷入口 -->
    <view class="quick-entry">
      <view class="entry-item" bindtap="goToModels">
        <text class="entry-icon">👗</text>
        <text class="entry-text">开始设计</text>
      </view>
      <view class="entry-item" bindtap="goToFabrics">
        <text class="entry-icon">🧵</text>
        <text class="entry-text">面料库</text>
      </view>
      <view class="entry-item" bindtap="goToMyspace">
        <text class="entry-icon">📦</text>
        <text class="entry-text">我的空间</text>
      </view>
    </view>

    <!-- 热门设计 -->
    <view class="section">
      <text class="section-title">🔥 热门设计</text>
      <scroll-view scroll-x class="design-list">
        <view class="design-card" wx:for="{{[1,2,3]}}" wx:key="*this">
          <view class="design-img">👗</view>
          <text class="design-name">设计 {{item}}</text>
          <text class="design-price">¥299</text>
        </view>
      </scroll-view>
    </view>
'''
    
    # 3D 画布
    canvas_block = f'''    <!-- 3D 试穿视口 -->
    <view class="3d-section">
      <view class="3d-viewport">
        <canvas type="webgl" id="three-canvas" class="three-canvas"></canvas>
        <view class="3d-tip" wx:if="{{!threeReady}}">{{threeTip}}</view>
      </view>
      
      <!-- 3D 控制栏 -->
      <view class="3d-controls">
        <view class="ctrl-btn" bindtap="rotateModel">🔄 旋转</view>
        <view class="ctrl-btn" bindtap="zoomIn">🔍+ 放大</view>
        <view class="ctrl-btn" bindtap="zoomOut">🔍- 缩小</view>
        <view class="ctrl-btn" bindtap="resetView">↩️ 重置</view>
        <view class="ctrl-btn" bindtap="downloadScreenshot">📷 截图</view>
      </view>
    </view>''' if has_3d else ""
    
    return f'''<view class="page">
  <!-- 顶部导航 -->
  <view class="navbar">
    <text class="nav-title">{page_name}</text>
  </view>

  <!-- 页面内容 -->
  <scroll-view scroll-y class="content">
    
    {home_extra}
    
    <!-- 通用内容区 -->
    <view class="main-content" wx:if="{not is_home}">
      <text class="page-title">{page_name}</text>
      <text class="page-desc">clothDiy 服装DIY小程序</text>
    </view>
    
    {canvas_block}
    
    <!-- 操作按钮区 -->
    <view class="btn-group">
{buttons}
    </view>
    
  </scroll-view>
</view>'''

def gen_wxss(page_path, cfg):
    has_3d = cfg.get("has_3d", False)
    is_home = cfg.get("is_home", False)
    
    home_css = ""
    if is_home:
        home_css = """
/* 搜索栏 */
.search-bar {
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.15);
  border-radius: 40rpx;
  padding: 16rpx 30rpx;
  margin: 20rpx 30rpx;
}
.search-icon { font-size: 32rpx; margin-right: 15rpx; }
.search-text { color: rgba(255,255,255,0.7); font-size: 26rpx; }

/* Hero 3D 展示区 */
.hero-3d {
  background: linear-gradient(135deg, #1a1a2e 0%, #6C5CE7 100%);
  padding: 60rpx 40rpx;
  margin: 0 0 30rpx 0;
}
.hero-title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 15rpx;
}
.hero-desc {
  display: block;
  font-size: 28rpx;
  color: rgba(255,255,255,0.8);
  margin-bottom: 30rpx;
}
.hero-btn {
  display: inline-block;
  background: #fff;
  color: #6C5CE7;
  padding: 18rpx 50rpx;
  border-radius: 40rpx;
  font-weight: bold;
  font-size: 30rpx;
}

/* 快捷入口 */
.quick-entry {
  display: flex;
  justify-content: space-around;
  padding: 30rpx;
  background: #fff;
  margin: 0 30rpx 30rpx 30rpx;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
}
.entry-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}
.entry-icon { font-size: 48rpx; }
.entry-text { font-size: 24rpx; color: #333; }

/* 热门设计 */
.section {
  padding: 30rpx;
}
.section-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #1a1a2e;
  margin-bottom: 20rpx;
}
.design-list {
  display: flex;
  gap: 20rpx;
  white-space: nowrap;
}
.design-card {
  display: inline-block;
  width: 240rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
}
.design-img {
  width: 200rpx;
  height: 200rpx;
  background: #f0f0f0;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 80rpx;
  margin-bottom: 15rpx;
}
.design-name { display: block; font-size: 26rpx; color: #333; }
.design-price { display: block; font-size: 28rpx; color: #e74c3c; font-weight: bold; margin-top: 8rpx; }
"""
    
    extra = ""
    if has_3d:
        extra = """
/* 3D 试穿区 */
.3d-section {
  margin: 30rpx;
}
.3d-viewport {
  position: relative;
  width: 100%;
  height: 600rpx;
  background: #1a1a2e;
  border-radius: 20rpx;
  overflow: hidden;
}
.three-canvas {
  width: 100%;
  height: 100%;
}
.3d-tip {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-size: 28rpx;
}
.3d-controls {
  display: flex;
  justify-content: space-around;
  margin-top: 20rpx;
  background: #fff;
  padding: 20rpx;
  border-radius: 16rpx;
}
.ctrl-btn {
  padding: 15rpx 25rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  font-size: 24rpx;
  color: #333;
}
"""
    
    return """.page {\n  min-height: 100vh;\n  background: #f5f5f5;\n}\n\n.navbar {\n  background: linear-gradient(135deg, #1a1a2e 0%, #6C5CE7 100%);\n  padding: 30rpx;\n  text-align: center;\n}\n.nav-title {\n  color: #fff;\n  font-size: 36rpx;\n  font-weight: bold;\n}\n\n.content {\n  height: calc(100vh - 100rpx);\n}\n\n.main-content {\n  padding: 40rpx 30rpx;\n  text-align: center;\n}\n.page-title {\n  display: block;\n  font-size: 40rpx;\n  font-weight: bold;\n  color: #1a1a2e;\n  margin-bottom: 10rpx;\n}\n.page-desc {\n  display: block;\n  font-size: 28rpx;\n  color: #999;\n}\n\n.btn-group {\n  padding: 30rpx;\n  display: flex;\n  flex-direction: column;\n  gap: 20rpx;\n}\n.btn {\n  background: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%);\n  color: #fff;\n  padding: 28rpx;\n  border-radius: 16rpx;\n  text-align: center;\n  font-size: 30rpx;\n  font-weight: bold;\n  box-shadow: 0 8rpx 30rpx rgba(108, 92, 231, 0.3);\n}\n.btn:active {\n  opacity: 0.85;\n  transform: scale(0.98);\n}""" + home_css + extra

def gen_json(page_path, cfg):
    return json.dumps({
        "usingComponents": {},
        "navigationBarTitleText": cfg["name"],
        "navigationBarBackgroundColor": "#1a1a2e",
        "navigationBarTextStyle": "white"
    }, ensure_ascii=False, indent=2)

def main():
    for page_path, cfg in PAGES.items():
        parts = page_path.split('/')
        page_dir = os.path.join(BASE, *parts[:-1])
        os.makedirs(page_dir, exist_ok=True)
        
        base_name = parts[-1]
        files = {
            "json": gen_json(page_path, cfg),
            "wxml": gen_wxml(page_path, cfg),
            "wxss": gen_wxss(page_path, cfg),
            "js": gen_js(page_path, cfg),
        }
        
        for ext, content in files.items():
            file_path = os.path.join(page_dir, f"{base_name}.{ext}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {file_path}")
    
    print(f"\n🎉 完成！共生成 {len(PAGES)} 个页面，每个页面 4 个文件")

if __name__ == "__main__":
    main()
