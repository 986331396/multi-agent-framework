#!/usr/bin/env python3
"""生成 clothDiy 小程序所有标准页面代码 - 修复版"""
import os
import json
from datetime import datetime

BASE_DIR = "/Users/mac/Desktop/clothDiy/clothDiy_miniprogram"

# 页面配置：path 是相对于 pages/ 的路径（不含扩展名）
PAGES = {
    "index/index": {
        "name": "首页",
        "nav": [
            {"label": "开始设计", "method": "goToModels", "target": "/pages/models/models"},
            {"label": "面料库", "method": "goToFabrics", "target": "/pages/fabrics/fabrics"},
            {"label": "我的空间", "method": "goToMyspace", "target": "/pages/myspace/myspace", "isTab": True},
        ]
    },
    "models/models": {
        "name": "建模库",
        "nav": [
            {"label": "创建建模", "method": "goToDesign", "target": "/pages/design/design"},
            {"label": "首页", "method": "goToIndex", "target": "/pages/index/index", "isTab": True},
        ]
    },
    "design/design": {
        "name": "设计页",
        "nav": [
            {"label": "去试穿", "method": "goToTryon", "target": "/pages/tryon/tryon"},
            {"label": "返回", "method": "goBack", "target": ""},
        ]
    },
    "tryon/tryon": {
        "name": "动态试穿",
        "nav": [
            {"label": "下订单", "method": "goToOrderPreview", "target": "/pages/order/preview"},
            {"label": "重新设计", "method": "goBack", "target": ""},
        ],
        "has_3d": True
    },
    "fabrics/fabrics": {
        "name": "面料库",
        "nav": [
            {"label": "去设计", "method": "goToDesign", "target": "/pages/design/design"},
            {"label": "首页", "method": "goToIndex", "target": "/pages/index/index", "isTab": True},
        ]
    },
    "order/preview": {
        "name": "订单预览",
        "nav": [
            {"label": "确认订单", "method": "goToOrderConfirm", "target": "/pages/order/confirm"},
            {"label": "返回", "method": "goBack", "target": ""},
        ]
    },
    "order/confirm": {
        "name": "订单确认",
        "nav": [
            {"label": "去支付", "method": "goToPayment", "target": "/pages/order/payment"},
            {"label": "返回", "method": "goBack", "target": ""},
        ]
    },
    "order/payment": {
        "name": "支付页",
        "nav": [
            {"label": "支付完成", "method": "goToMyspace", "target": "/pages/myspace/myspace", "isTab": True},
            {"label": "返回", "method": "goBack", "target": ""},
        ]
    },
    "myspace/myspace": {
        "name": "我的空间",
        "nav": [
            {"label": "首页", "method": "goToIndex", "target": "/pages/index/index", "isTab": True},
            {"label": "我的订单", "method": "viewOrders", "target": ""},
        ]
    },
    "profile/profile": {
        "name": "个人中心",
        "nav": [
            {"label": "编辑资料", "method": "editProfile", "target": ""},
            {"label": "我的订单", "method": "viewOrders", "target": "/pages/myspace/myspace", "isTab": True},
        ]
    },
}

def gen_js(page_path, cfg):
    """生成 page.js"""
    page_name = cfg["name"]
    nav = cfg.get("nav", [])
    has_3d = cfg.get("has_3d", False)
    
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
            methods += f"\n  {method}() {{\n    console.log('{method}');\n  }},"
    
    extra = ""
    if has_3d:
        extra = """
  
  /* 3D 方法 */
  initThreeJS() {
    const query = wx.createSelectorQuery();
    query.select('#three-canvas')
      .node()
      .exec((res) => {
        if (res && res[0] && res[0].node) {
          const canvas = res[0].node;
          console.log('[3D] Canvas 节点获取成功', canvas);
          // TODO: 初始化 Three.js 场景
        }
      });
  },
  
  rotateModel() { console.log('[3D] 旋转模型'); },
  resetView() { console.log('[3D] 重置视角'); },
  downloadScreenshot() { console.log('[3D] 保存截图'); },"""
    
    return f'''Page({{
  data: {{
    pageName: '{page_name}',
    createTime: '{datetime.now().strftime("%Y-%m-%d")}',
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
  {extra}
}});'''

def gen_wxml(page_path, cfg):
    """生成 page.wxml"""
    page_name = cfg["name"]
    nav = cfg.get("nav", [])
    has_3d = cfg.get("has_3d", False)
    
    buttons = ""
    for action in nav:
        buttons += f'    <van-button type="primary" bindtap="{action["method"]}" style="margin:20rpx 0;width:80%;">{{action["label"]}}</van-button>\n'
    
    canvas_block = f'''    <view class="3d-viewport">
      <canvas type="webgl" id="three-canvas" style="width:100%;height:500rpx;"></canvas>
    </view>''' if has_3d else ""
    
    return f'''<view class="page">
  <view class="header">
    <text class="title">{page_name}</text>
  </view>
  <view class="body">
    <text class="subtitle">clothDiy 服装DIY</text>
    <view class="btn-group">
{buttons}
    </view>
{canvas_block}
  </view>
</view>'''

def gen_wxss(page_path, cfg):
    """生成 page.wxss"""
    has_3d = cfg.get("has_3d", False)
    extra = ""
    if has_3d:
        extra = """
.3d-viewport {
  margin: 30rpx 0;
  border-radius: 16rpx;
  overflow: hidden;
  background: #1a1a2e;
}
#three-canvas {
  width: 100%;
  height: 500rpx;
}
"""
    return f""".page {{
  min-height: 100vh;
  background: #f5f5f5;
}}
.header {{
  background: linear-gradient(135deg, #1a1a2e, #6C5CE7);
  padding: 30rpx;
  text-align: center;
}}
.title {{
  color: #fff;
  font-size: 36rpx;
  font-weight: bold;
}}
.body {{
  padding: 40rpx 30rpx;
}}
.subtitle {{
  display: block;
  text-align: center;
  color: #999;
  margin-bottom: 40rpx;
}}
.btn-group {{
  display: flex;
  flex-direction: column;
  align-items: center;
}}
.btn-group van-button {{
  margin: 15rpx 0 !important;
}}{extra}"""

def gen_json(page_path, cfg):
    """生成 page.json"""
    return json.dumps({
        "usingComponents": {
            "van-button": "@vant/weapp/button/index",
            "van-icon": "@vant/weapp/icon/index",
        },
        "navigationBarTitleText": cfg["name"]
    }, ensure_ascii=False, indent=2)

def main():
    for page_path, cfg in PAGES.items():
        page_dir = os.path.join(BASE_DIR, "pages", os.path.dirname(page_path))
        os.makedirs(page_dir, exist_ok=True)
        
        base_name = os.path.basename(page_path)
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
    
    print(f"\n🎉 完成！生成 {len(PAGES)} 个页面")

if __name__ == "__main__":
    main()
