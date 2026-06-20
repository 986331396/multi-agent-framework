#!/usr/bin/env python3
"""
生成 clothDiy 小程序所有标准页面代码
- 正确命名：pages/index/index.js
- 完整导航链路
- 双AI审核就绪
"""

import os
import json

BASE_DIR = "/Users/mac/Desktop/clothDiy/clothDiy_miniprogram"

PAGES = {
    "pages/index/index": {
        "name": "首页",
        "nav_actions": [
            {"label": "开始设计", "target": "pages/models/models", "method": "goToModels"},
            {"label": "面料库", "target": "pages/fabrics/fabrics", "method": "goToFabrics"},
            {"label": "我的空间", "target": "pages/myspace/myspace", "method": "goToMyspace", "isTab": True},
        ]
    },
    "pages/models/models": {
        "name": "建模库",
        "nav_actions": [
            {"label": "创建建模", "target": "pages/design/design", "method": "goToDesign"},
            {"label": "首页", "target": "pages/index/index", "method": "goToIndex", "isTab": True},
        ]
    },
    "pages/design/design": {
        "name": "设计页",
        "nav_actions": [
            {"label": "去试穿", "target": "pages/tryon/tryon", "method": "goToTryon"},
            {"label": "返回建模库", "target": "pages/models/models", "method": "goBack"},
        ]
    },
    "pages/tryon/tryon": {
        "name": "动态试穿",
        "nav_actions": [
            {"label": "下订单", "target": "pages/order/preview", "method": "goToOrderPreview"},
            {"label": "重新设计", "target": "pages/design/design", "method": "goBack"},
        ]
    },
    "pages/fabrics/fabrics": {
        "name": "面料库",
        "nav_actions": [
            {"label": "去设计", "target": "pages/design/design", "method": "goToDesign"},
            {"label": "首页", "target": "pages/index/index", "method": "goToIndex", "isTab": True},
        ]
    },
    "pages/order/preview": {
        "name": "订单预览",
        "nav_actions": [
            {"label": "确认订单", "target": "pages/order/confirm", "method": "goToOrderConfirm"},
            {"label": "返回试穿", "target": "pages/tryon/tryon", "method": "goBack"},
        ]
    },
    "pages/order/confirm": {
        "name": "订单确认",
        "nav_actions": [
            {"label": "去支付", "target": "pages/order/payment", "method": "goToPayment"},
            {"label": "返回预览", "target": "pages/order/preview", "method": "goBack"},
        ]
    },
    "pages/order/payment": {
        "name": "支付页",
        "nav_actions": [
            {"label": "支付完成", "target": "pages/myspace/myspace", "method": "goToMyspace"},
            {"label": "返回确认", "target": "pages/order/confirm", "method": "goBack"},
        ]
    },
    "pages/myspace/myspace": {
        "name": "我的空间",
        "nav_actions": [
            {"label": "首页", "target": "pages/index/index", "method": "goToIndex", "isTab": True},
            {"label": "我的订单", "target": "pages/myspace/myspace", "method": "viewOrders"},
        ]
    },
    "pages/profile/profile": {
        "name": "个人中心",
        "nav_actions": [
            {"label": "编辑资料", "target": "pages/profile/profile", "method": "editProfile"},
            {"label": "我的订单", "target": "pages/myspace/myspace", "method": "goToMyspace", "isTab": True},
        ]
    },
}

def gen_json(page_path, page_name):
    """生成 page.json"""
    content = {
        "usingComponents": {
            "van-icon": "@vant/weapp/icon/index",
            "van-button": "@vant/weapp/button/index",
            "van-card": "@vant/weapp/card/index",
            "van-tag": "@vant/weapp/tag/index",
            "van-tab": "@vant/weapp/tab/index",
            "van-tabs": "@vant/weapp/tabs/index",
            "van-image": "@vant/weapp/image/index",
        },
        "navigationBarTitleText": page_name
    }
    return json.dumps(content, ensure_ascii=False, indent=2)

def gen_wxml(page_path, page_name, nav_actions):
    """生成 page.wxml - 简化版，确保能运行"""
    nav_buttons = ""
    for action in nav_actions:
        nav_buttons += f'  <van-button type="primary" bindtap="{action["method"]}">{action["label"]}</van-button>\n'
    
    return f'''<view class="page-container">
  <!-- 顶部导航 -->
  <view class="navbar">
    <text class="nav-title">{page_name}</text>
  </view>

  <!-- 页面内容 -->
  <view class="content-area">
    <view class="welcome-section">
      <text class="page-title">{page_name}</text>
      <text class="page-desc">clothDiy 服装DIY小程序</text>
    </view>

    <!-- 功能按钮区 -->
    <view class="action-buttons">
{nav_buttons}
    </view>

    <!-- 3D展示区（试穿页专用） -->
    {"<view class=\"3d-viewport\"><canvas type=\"webgl\" id=\"three-canvas\"></canvas></view>" if "tryon" in page_path else "<view class=\"demo-card\"><text>页面内容区域</text></view>"}
  </view>
</view>'''

def gen_wxss(page_path, page_name):
    """生成 page.wxss"""
    is_tryon = "tryon" in page_path
    extra_css = ""
    if is_tryon:
        extra_css = """
/* 3D视口 */
.3d-viewport {
  width: 100%;
  height: 500rpx;
  background: #1a1a2e;
  border-radius: 16rpx;
  overflow: hidden;
  margin: 20rpx 0;
}
#three-canvas {
  width: 100%;
  height: 100%;
}
"""
    return f'''.page-container {{
  min-height: 100vh;
  background: #f5f5f5;
}}

.navbar {{
  background: linear-gradient(135deg, #1a1a2e 0%, #6C5CE7 100%);
  padding: 20rpx 30rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.nav-title {{
  color: white;
  font-size: 36rpx;
  font-weight: bold;
}}

.content-area {{
  padding: 30rpx;
}}

.welcome-section {{
  text-align: center;
  margin-bottom: 40rpx;
}}
.page-title {{
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #1a1a2e;
  margin-bottom: 10rpx;
}}
.page-desc {{
  display: block;
  font-size: 28rpx;
  color: #666;
}}

.action-buttons {{
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin: 30rpx 0;
}}

.demo-card {{
  background: white;
  border-radius: 16rpx;
  padding: 30rpx;
  margin: 20rpx 0;
  text-align: center;
  color: #999;
}}
{extra_css}'''

def gen_js(page_path, page_name, nav_actions):
    """生成 page.js - 包含完整导航逻辑"""
    # 生成导航方法
    methods = ""
    for action in nav_actions:
        method = action["method"]
        target = action["target"]
        is_tab = action.get("isTab", False)
        
        if method == "goBack":
            methods += """
  goBack() {
    wx.navigateBack({ delta: 1 });
  },"""
        elif is_tab:
            methods += f"""
  {method}() {{
    wx.switchTab({{ url: '/{target}' }});
  }},"""
        else:
            methods += f"""
  {method}() {{
    wx.navigateTo({{ url: '/{target}' }});
  }},"""
    
    # 3D相关方法（试穿页）
    extra_methods = ""
    if "tryon" in page_path:
        extra_methods = """
  
  /* 3D相关方法 */
  initThreeJS() {
    console.log('[3D] 初始化Three.js场景');
    // TODO: 实际Three.js小程序适配代码
    // 1. 引入 threejs-miniprogram
    // 2. 创建场景、相机、渲染器
    // 3. 加载模型
    // 4. 实现拖拽旋转、缩放
  },
  
  rotateModel() {
    console.log('[3D] 旋转模型');
  },
  
  resetView() {
    console.log('[3D] 重置视角');
  },
  
  downloadScreenshot() {
    console.log('[3D] 保存截图');
  },"""
    
    return f'''Page({{
  data: {{
    pageName: '{page_name}',
    createTime: '{__import__("datetime").datetime.now().strftime("%Y-%m-%d")}',
  }},

  onLoad(options) {{
    console.log('[{page_name}] 页面加载', options);
    {"this.initThreeJS();" if "tryon" in page_path else ""}
  }},

  onShow() {{
    console.log('[{page_name}] 页面显示');
  }},

  onShareAppMessage() {{
    return {{
      title: 'clothDiy - {page_name}',
      path: '/{page_path}'
    }};
  }},

  // 导航方法
  {methods}
  {extra_methods}
  
  // 通用方法
  onShareTimeline() {{
    return {{
      title: 'clothDiy - 服装DIY小程序'
    }};
  }}
}});'''

def main():
    for page_path, config in PAGES.items():
        page_name = config["name"]
        nav_actions = config["nav_actions"]
        
        # 确保目录存在
        page_dir = os.path.join(BASE_DIR, page_path)
        os.makedirs(page_dir, exist_ok=True)
        
        # 生成四个文件
        files = {
            "json": gen_json(page_path, page_name),
            "wxml": gen_wxml(page_path, page_name, nav_actions),
            "wxss": gen_wxss(page_path, page_name),
            "js": gen_js(page_path, page_name, nav_actions),
        }
        
        for ext, content in files.items():
            file_path = os.path.join(page_dir, f"{os.path.basename(page_path)}.{ext}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 生成: {file_path}")
    
    print(f"\n🎉 全部完成！共生成 {len(PAGES)} 个页面，每个页面4个文件")

if __name__ == "__main__":
    main()
