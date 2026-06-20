#!/usr/bin/env python3
"""
clothDiy 微信小程序 - UI严格还原生成器
基于9张UI设计图的像素级还原
生成时间: 2026-06-20
"""

import os

BASE = "/Users/mac/Desktop/clothDiy/clothDiy_miniprogram"

# ============================================================
# 全局 CSS 设计系统
# ============================================================
DESIGN_SYSTEM_CSS = """
/* ========================================
   clothDiy Design System - 深色科技风
   基于 UI 设计图提取
   ======================================== */

page {
  background-color: #0a0a14;
  color: #e5e5e5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  min-height: 100vh;
}

/* ---- 变量定义（小程序不支持var时使用实际值） ---- */

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(20, 20, 35, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.3);
}

.glass-card-light {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16rpx;
  padding: 24rpx;
}

/* 导航栏 */
.navbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 88rpx;
  background: rgba(10, 10, 20, 0.95);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30rpx;
  z-index: 1000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.navbar-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #e5e5e5;
}
.navbar-right {
  display: flex;
  align-items: center;
  gap: 20rpx;
}
.navbar-icon {
  width: 44rpx;
  height: 44rpx;
  color: #888899;
}

/* 页面内容区（给导航栏留空间） */
.page-container {
  padding-top: 88rpx;
  padding-bottom: 120rpx; /* 给TabBar留空间 */
  min-height: 100vh;
}

/* 搜索框 */
.search-bar {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12rpx;
  height: 72rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  color: #555566;
  font-size: 26rpx;
}

/* 标签 */
.tag-active {
  display: inline-block;
  background: #3b82f6;
  color: #fff;
  padding: 8rpx 24rpx;
  border-radius: 8rpx;
  font-size: 22rpx;
}
.tag-inactive {
  display: inline-block;
  background: rgba(255, 255, 255, 0.06);
  color: #888899;
  padding: 8rpx 24rpx;
  border-radius: 8rpx;
  font-size: 22rpx;
}

/* 状态标签 */
.tag-status {
  display: inline-block;
  font-size: 18rpx;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
  letter-spacing: 2rpx;
}
.tag-draft { background: rgba(255,255,255,0.08); color: #888899; }
.tag-finalized { background: rgba(16,185,129,0.15); color: #10b981; }
.tag-recently { background: rgba(59,130,246,0.15); color: #3b82f6; }
.tag-hot { background: rgba(236,72,153,0.15); color: #ec4899; }

/* 按钮 */
.btn-primary {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: #fff;
  border-radius: 12rpx;
  padding: 18rpx 36rpx;
  font-size: 26rpx;
  font-weight: 600;
  text-align: center;
  border: none;
}
.btn-primary::after { border: none; }

.btn-outline {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e5e5e5;
  border-radius: 12rpx;
  padding: 16rpx 32rpx;
  font-size: 24rpx;
  text-align: center;
}
.btn-outline::after { border: none; }

.btn-small {
  background: rgba(255, 255, 255, 0.06);
  color: #e5e5e5;
  border-radius: 8rpx;
  padding: 10rpx 24rpx;
  font-size: 22rpx;
}

/* 图标按钮 */
.icon-btn {
  width: 76rpx;
  height: 76rpx;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #aaaabb;
  font-size: 36rpx;
}
.icon-btn-active {
  background: #7c3aed;
  border-color: #7c3aed;
  color: #fff;
}

/* 文字样式 */
.text-primary { color: #e5e5e5; }
.text-secondary { color: #888899; }
.text-tertiary { color: #555566; }
.text-accent { color: #7c3aed; }
.text-price { color: #e5e5e5; font-weight: bold; }

.title-lg { font-size: 34rpx; font-weight: bold; color: #e5e5e5; }
.title-md { font-size: 28rpx; font-weight: 600; color: #e5e5e5; }
.title-sm { font-size: 26rpx; font-weight: 500; color: #e5e5e5; }
.body-text { font-size: 26rpx; color: #e5e5e5; line-height: 1.6; }
.caption { font-size: 22rpx; color: #888899; }
.micro { font-size: 20rpx; color: #555566; }

/* 分割线 */
.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin: 20rpx 0;
}

/* Section标题 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 30rpx 0 20rpx;
}
.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #e5e5e5;
}
.section-more {
  font-size: 24rpx;
  color: #7c3aed;
}

/* Flex工具 */
.flex { display: flex; }
.flex-row { flex-direction: row; }
.flex-col { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.justify-center { justify-content: center; }
.gap-sm { gap: 12rpx; }
.gap-md { gap: 20rpx; }
.gap-lg { gap: 28rpx; }

/* 安全区 */
.safe-bottom { padding-bottom: env(safe-area-inset-bottom); }
"""


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ {path}")


def write_page(page_name, wxml, wxss, js, json_content="{}"):
    base = f"{BASE}/pages/{page_name}"
    write_file(f"{base}/{page_name}.wxml", wxml)
    write_file(f"{base}/{page_name}.wxss", wxss)
    write_file(f"{base}/{page_name}.js", js)
    write_file(f"{base}/{page_name}.json", json_content)


# ============================================================
# PAGE 1: 首页 (index) - 基于UI图
# ============================================================
def gen_index():
    page = "index"
    wxml = '''<!-- clothDiy 首页 - 严格按照UI设计图 -->
<view class="page-container">
  <!-- 导航栏 -->
  <view class="navbar">
    <view class="navbar-title">衣配定制</view>
    <view class="navbar-right">
      <text class="navbar-icon">🔔</text>
      <image class="avatar-small" src="/images/avatar-default.png" mode="aspectFill" />
    </view>
  </view>

  <!-- 当前系列卡片 -->
  <view style="padding:30rpx;">
    <view class="glass-card" style="background:linear-gradient(145deg,rgba(124,58,237,0.12),rgba(59,130,246,0.08));border-color:rgba(124,58,237,0.2);">
      <text class="micro" style="color:#888899;">当前系列</text>
      <view class="title-lg" style="margin:8rpx 0;">真红交响曲 V2</view>
      <view style="display:flex;gap:12rpx;margin-top:16rpx;">
        <view class="tag-active" style="background:#7c3aed;font-size:20rpx;padding:6rpx 16rpx;">4K精细</view>
        <view tag-inactive style="font-size:20rpx;padding:6rpx 16rpx;background:rgba(255,255,255,0.06);border-radius:8rpx;color:#888899;">智能缩放</view>
      </view>
    </view>
  </view>

  <!-- 核心3D展示区 - 占屏幕约45%高度 -->
  <view style="padding:0 30rpx;">
    <view class="hero-3d-area">
      <!-- 3D视口占位 - 实际使用canvas-three渲染 -->
      <view class="hero-viewport">
        <image src="/images/hero-model.png" mode="aspectFit" class="hero-model-img" />
        <!-- 场景光效装饰 -->
        <view class="hero-glow-left"></view>
        <view class="hero-glow-right"></view>
        <!-- 地面网格线效果 -->
        <view class="hero-grid"></view>
      </view>
      <!-- 右侧控制按钮组 -->
      <view class="hero-controls">
        <view class="icon-btn" bindtap="rotateHeroModel">
          <text>🔄</text>
        </view>
        <view class="icon-btn" bindtap="zoomHeroModel">
          <text>🔍</text>
        </view>
      </view>
    </view>
  </view>

  <!-- 功能模块区域 -->
  <view style="padding:20rpx 30rpx;">
    <!-- 数字建模卡片 -->
    <view class="glass-card func-card" bindtap="goToModels">
      <view class="func-card-left">
        <view class="func-icon" style="background:linear-gradient(135deg,#7c3aed,#a78bfa);">
          <text style="font-size:32rpx;color:#fff;">✦</text>
        </view>
        <view>
          <view class="title-md">数字建模</view>
          <text class="caption">基于精确的生理数据生成超逼真模型。</text>
        </view>
      </view>
      <view class="btn-outline" style="padding:12rpx 24rpx;font-size:22rpx;">去建模</view>
    </view>

    <!-- 创意工坊卡片 -->
    <view class="glass-card func-card" style="margin-top:20rpx;" bindtap="goToDesign">
      <view class="func-card-left">
        <view class="func-icon" style="background:linear-gradient(135deg,#3b82f6,#60a5fa);">
          <text style="font-size:32rpx;color:#fff;">▷</text>
        </view>
        <view>
          <view class="title-md">创意工坊</view>
          <text class="caption">访问织造引擎，自定义面料和剪裁。</text>
        </view>
      </view>
      <view class="btn-outline" style="padding:12rpx 24rpx;font-size:22rpx;">去设计</view>
    </view>

    <!-- 导入自定义卡片 -->
    <view class="glass-card func-card" style="margin-top:20rpx;" bindtap="importModel">
      <view class="func-card-left">
        <view class="func-icon" style="background:linear-gradient(135deg,#06b6d4,#67e8f9);">
          <text style="font-size:32rpx;color:#fff;">⊕</text>
        </view>
        <view>
          <view class="title-md">导入自定义</view>
          <text class="caption">OBJ / FBX</text>
        </view>
      </view>
    </view>
  </view>

  <!-- 最近资产 -->
  <view style="padding:0 30rpx;">
    <view class="section-header">
      <view class="section-title">最近资产</view>
      <text class="section-more" bindtap="goToMyspace">查看全部 ></text>
    </view>
    <scroll-view scroll-x="true" style="white-space:nowrap;margin-top:16rpx;">
      <view style="display:inline-flex;gap:16rpx;">
        <view class="asset-thumb" wx:for="{{recentAssets}}" wx:key="id">
          <image src="{{item.thumb}}" mode="aspectFill" class="asset-img" />
          <text class="micro" style="margin-top:8rpx;display:block;text-align:center;">{{item.name}}</text>
        </view>
      </view>
    </scroll-view>
  </view>
</view>
'''

    wxss = DESIGN_SYSTEM_CSS + """
/* ===== 首页专属样式 ===== */

/* Hero 3D 展示区 */
.hero-3d-area {
  position: relative;
  width: 100%;
  height: 520rpx;
  border-radius: 24rpx;
  overflow: hidden;
  margin-top: 10rpx;
}

.hero-viewport {
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at center, #151525 0%, #0a0a14 70%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.hero-model-img {
  width: 70%;
  height: 80%;
  opacity: 0.95;
}

/* 光效装饰 */
.hero-glow-left {
  position: absolute;
  left: -50rpx;
  top: 15%;
  width: 120rpx;
  height: 400rpx;
  background: linear-gradient(180deg, rgba(124,58,237,0.25), transparent);
  filter: blur(40rpx);
  pointer-events: none;
}
.hero-glow-right {
  position: absolute;
  right: -50rpx;
  top: 15%;
  width: 120rpx;
  height: 400rpx;
  background: linear-gradient(180deg, rgba(59,130,246,0.2), transparent);
  filter: blur(40rpx);
  pointer-events: none;
}

/* 透视网格线效果 */
.hero-grid {
  position: absolute;
  bottom: 60rpx;
  left: 50%;
  transform: translateX(-50%) perspective(500rpx) rotateX(60deg);
  width: 80%;
  height: 200rpx;
  background-image:
    linear-gradient(rgba(124,58,237,0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(124,58,237,0.08) 1px, transparent 1px);
  background-size: 40rpx 40rpx;
  opacity: 0.5;
  pointer-events: none;
}

/* 控制按钮 */
.hero-controls {
  position: absolute;
  right: 24rpx;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

/* 功能模块卡片 */
.func-card {
  display: flex !important;
  align-items: center;
  justify-content: space-between !important;
}
.func-card-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
  flex: 1;
}
.func-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* 资产缩略图 */
.asset-thumb {
  display: inline-block;
  width: 180rpx;
  flex-shrink: 0;
}
.asset-img {
  width: 180rpx;
  height: 180rpx;
  border-radius: 16rpx;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
}

/* 小头像 */
.avatar-small {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
}
"""

    js = '''// clothDiy 首页 - 严格按照UI设计图
const app = getApp();

Page({
  data: {
    recentAssets: [
      { id: 1, name: '波浪皮革', thumb: '/assets/fabric-wave.png' },
      { id: 2, name: '金属纽扣', thumb: '/assets/btn-metal.png' },
      { id: 3, name: '丝绸纹理', thumb: '/assets/fabric-silk.png' },
      { id: 4, name: '3D人体', thumb: '/assets/model-body.png' }
    ]
  },

  onLoad() {
    this.loadRecentAssets();
  },

  onShow() {
    // 刷新最近资产
  },

  // 加载最近资产
  loadRecentAssets() {
    // TODO: 从后端API加载用户最近的资产数据
  },

  // 导航: 去建模库
  goToModels() {
    wx.navigateTo({ url: '/pages/models/models' });
  },

  // 导航: 去设计页
  goToDesign() {
    wx.navigateTo({ url: '/pages/design/design' });
  },

  // 导航: 我的空间
  goToMyspace() {
    wx.navigateTo({ url: '/pages/myspace/myspace' });
  },

  // 导航: 去3D试穿
  goToTryon() {
    wx.navigateTo({ url: '/pages/tryon/tryon' });
  },

  // Hero模型旋转
  rotateHeroModel() {
    wx.navigateTo({ url: '/pages/tryon/tryon' });
  },

  // Hero模型放大
  zoomHeroModel() {
    wx.navigateTo({ url: '/pages/tryon/tryon' });
  },

  // 导入自定义模型
  importModel() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['obj', 'fbx', 'gltf', 'glb'],
      success: (res) => {
        const file = res.tempFiles[0];
        console.log('导入文件:', file.name);
        // TODO: 上传到后端处理
        wx.showToast({ title: '导入成功', icon: 'success' });
      }
    });
  },

  onShareAppMessage() {
    return {
      title: '衣配定制 - AI服装DIY平台',
      path: '/pages/index/index'
    };
  }
});
'''

    json_content = '{\n  "usingComponents": {},\n  "navigationBarTitleText": ""\n}'
    write_page(page, wxml, wxss, js, json_content)


# ============================================================
# PAGE 2: 动态试穿 (tryon) - 基于UI图
# ============================================================
def gen_tryon():
    page = "tryon"
    wxml = '''<!-- 动态试穿页 - 全屏3D视口 + 双侧工具栏 -->
<view class="page-container" style="padding:0;padding-bottom:120rpx;">
  <!-- 导航栏 -->
  <view class="navbar">
    <view class="navbar-title">动态试穿</view>
    <view class="navbar-right">
      <text class="navbar-icon">🔔</text>
      <image class="avatar-small" src="/images/avatar-default.png" mode="aspectFill"/>
    </view>
  </view>

  <!-- 全屏3D试穿视口 -->
  <view class="tryon-viewport-wrapper">
    <!-- 顶部紫色光晕边框 -->
    <view class="tryon-glow-border"></view>

    <!-- 3D Canvas 视口 -->
    <canvas type="webgl" id="tryon-canvas" class="tryon-canvas"
            bindtouchstart="onTouchStart" bindtouchmove="onTouchMove" bindtouchend="onTouchEnd"></canvas>

    <!-- 加载提示 -->
    <view class="tryon-loading" wx:if="{{!threeReady}}">
      <text class="caption">正在初始化 3D 引擎...</text>
    </view>

    <!-- 左侧工具栏 -->
    <view class="toolbar-left">
      <view class="icon-btn toolbar-btn" bindtap="rotateModel">
        <text>🔄</text>
      </view>
      <view class="icon-btn toolbar-btn" bindtap="zoomIn">
        <text>🔍+</text>
      </view>
      <view class="icon-btn toolbar-btn" bindtap="switchPersonMode">
        <text>👤</text>
      </view>
      <view class="icon-btn toolbar-btn" bindtap="searchModel">
        <text>🔎</text>
      </view>
    </view>

    <!-- 右侧工具栏 -->
    <view class="toolbar-right">
      <view class="icon-btn toolbar-btn" bindtap="toggleWalkMode">
        <text>🚶</text>
      </view>
      <view class="icon-btn toolbar-btn" bindtap="toggleBodyView">
        <text>🧑</text>
      </view>
      <view class="icon-btn toolbar-btn" bindtap="resetCamera">
        <text>↻</text>
      </view>
      <view class="icon-btn icon-btn-active toolbar-btn" bindtap="takeScreenshot">
        <text>📷</text>
      </view>
    </view>
  </view>
</view>
'''

    wxss = DESIGN_SYSTEM_CSS + """
/* ===== 动态试穿专属样式 ===== */

.page-container { padding: 0 !important; padding-top: 88rpx !important; }

.tryon-viewport-wrapper {
  position: relative;
  width: 100vw;
  height: calc(100vh - 208rpx); /* 减去导航栏+TabBar */
  background: #080810;
  overflow: hidden;
}

/* 顶部紫色光晕边框 */
.tryon-glow-border {
  position: absolute;
  top: 0; left: 5%; right: 5%; height: 4rpx;
  background: linear-gradient(90deg, transparent, #7c3aed, #3b82f6, #7c3aed, transparent);
  box-shadow: 0 0 30rpx rgba(124,58,237,0.5);
  z-index: 10;
  pointer-events: none;
}

/* 3D Canvas */
.tryon-canvas {
  width: 100%;
  height: 100%;
}

/* 加载提示 */
.tryon-loading {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 5;
}

/* 工具栏通用 */
.toolbar-btn {
  width: 80rpx !important;
  height: 80rpx !important;
  font-size: 36rpx !important;
}

/* 左侧工具栏 */
.toolbar-left {
  position: absolute;
  left: 24rpx;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  z-index: 20;
}

/* 右侧工具栏 */
.toolbar-right {
  position: absolute;
  right: 24rpx;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  z-index: 20;
}

.avatar-small {
  width: 48rpx; height: 48rpx;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
}
"""

    js = '''// clothDiy 动态试穿 - Three.js 3D视口
const app = getApp();

Page({
  data: {
    threeReady: false,
    currentModel: null,
    clothingModel: null,
    cameraDistance: 5,
    rotationY: 0,
    personMode: 'body' // body | walk
  },

  onLoad(options) {
    // 接收传递的模型ID
    if (options.modelId) {
      this.setData({ modelId: options.modelId });
    }
    if (options.clothingId) {
      this.setData({ clothingId: options.clothingId });
    }
  },

  onReady() {
    this.initThreeJS();
  },

  // 初始化Three.js场景
  initThreeJS() {
    try {
      const info = wx.createSelectorQuery().in(this).select('#tryon-canvas');
      info.fields({ node: true, size: true }).res((res) => {
        const canvas = res.node;
        const renderer = wx.createWebGLContext(
          canvas.id,
          { alpha: true, antialias: true }
        );

        // 渲染循环
        const renderLoop = () => {
          this.renderFrame(canvas, renderer);
          canvas.requestAnimationFrame(renderLoop);
        };
        canvas.requestAnimationFrame(renderLoop);

        this.setData({
          threeReady: true,
          canvas: canvas,
          glRenderer: renderer,
          canvasWidth: res.width,
          canvasHeight: res.height
        });

        console.log('✅ 3D 试穿引擎初始化完成');
      }).exec();
    } catch (e) {
      console.error('3D初始化失败:', e);
      this.setData({ threeReady: false });
    }
  },

  // 渲染帧
  renderFrame(canvas, renderer) {
    // 实际渲染逻辑由 threejs-miniprogram 库完成
    // 这里保留接口供后续集成
  },

  // === 工具栏操作 ===

  // 旋转模型
  rotateModel() {
    this.triggerEventToGL('rotate_toggle');
  },

  // 放大
  zoomIn() {
    this.setData({ cameraDistance: Math.max(2, this.data.cameraDistance - 0.5) });
    this.triggerEventToGL('zoom_in', this.data.cameraDistance);
  },

  // 缩小 (双指或按钮)
  zoomOut() {
    this.setData({ cameraDistance: Math.min(10, this.data.cameraDistance + 0.5) });
    this.triggerEventToGL('zoom_out', this.data.cameraDistance);
  },

  // 切换人物模式
  switchPersonMode() {
    const modes = ['body', 'walk', 'skeleton'];
    const idx = modes.indexOf(this.data.personMode);
    this.setData({ personMode: modes[(idx + 1) % modes.length] });
    this.triggerEventToGL('person_mode', this.data.personMode);
  },

  // 切换走秀模式
  toggleWalkMode() {
    this.triggerEventToGL('walk_mode_toggle');
  },

  // 切换身体视图
  toggleBodyView() {
    this.triggerEventToGL('body_view_toggle');
  },

  // 重置相机
  resetCamera() {
    this.setData({ cameraDistance: 5, rotationY: 0 });
    this.triggerEventToGL('camera_reset');
  },

  // 截图
  takeScreenshot() {
    wx.showToast({ title: '截图保存中...', icon: 'loading' });
    // TODO: canvas.toTempFilePath 保存截图
    setTimeout(() => {
      wx.showToast({ title: '截图已保存', icon: 'success' });
    }, 800);
  },

  // 搜索模型
  searchModel() {
    wx.navigateBack();
  },

  // === 触摸交互 ===
  onTouchStart(e) {
    this.touchStartX = e.touches[0].clientX;
    this.touchStartY = e.touches[0].clientY;
  },

  onTouchMove(e) {
    if (!this.touchStartX) return;
    const dx = e.touches[0].clientX - this.touchStartX;
    const dy = e.touches[0].clientY - this.touchStartY;
    this.setData({ rotationY: this.data.rotationY + dx * 0.01 });
    this.triggerEventToGL('rotate_delta', dx * 0.005);
    this.touchStartX = e.touches[0].clientX;
    this.touchStartY = e.touches[0].clientY;
  },

  onTouchEnd() {
    this.touchStartX = null;
    this.touchStartY = null;
  },

  // 向GL层发送事件
  triggerEventToGL(eventType, data) {
    console.log('[Tryon]', eventType, data || '');
  },

  // 下订单
  goOrderPreview() {
    wx.navigateTo({ url: '/pages/order/preview?from=tryon' });
  },

  // 返回
  goBack() {
    wx.navigateBack();
  },

  onShareAppMessage() {
    return { title: '动态试穿 - clothDiy', path: '/pages/tryon/tryon' };
  }
});
'''

    json_content = '{\n  "usingComponents": {},\n  "navigationBarTitleText": ""\n}'
    write_page(page, wxml, wxss, js, json_content)


# ============================================================
# PAGE 3: 建模库 (models) - 基于UI图
# ============================================================
def gen_models():
    page = "models"
    wxml = '''<!-- 数字人库/建模库 - 模型列表页 -->
<view class="page-container">
  <!-- 导航栏 -->
  <view class="navbar">
    <view style="display:flex;align-items:center;gap:16rpx;">
      <text bindtap="goBack" style="font-size:36rpx;color:#e5e5e5;">&lt;</text>
      <view class="navbar-title">数字人库</view>
    </view>
    <text class="navbar-icon" style="font-size:36rpx;">⚙️</text>
  </view>

  <!-- 搜索与筛选 -->
  <view style="padding:24rpx 30rpx 0;">
    <!-- 搜索框 -->
    <view class="search-bar">
      <text style="margin-right:12rpx;color:#555566;">🔍</text>
      <input placeholder="搜索人体名称、属性" placeholder-class="search-placeholder"
             style="flex:1;color:#e5e5e5;font-size:26rpx;"
             bindconfirm="onSearch" value="{{searchKeyword}}" />
    </view>

    <!-- 性别筛选 + 新建按钮 -->
    <view style="display:flex;justify-content:space-between;align-items:center;margin-top:24rpx;">
      <scroll-view scroll-x="true" style="white-space:nowrap;">
        <view style="display:inline-flex;gap:16rpx;">
          <view class="tag-active" wx:for="{{genderTabs}}" wx:key="value"
                data-value="{{item.value}}" bindtap="switchGender"
                style="{{currentGender===item.value?'':'background:rgba(255,255,255,0.06);color:#888899;'}}">
            {{item.label}}
          </view>
        </view>
      </scroll-view>
      <view class="btn-small" catchtap="createNewAI" style="background:#3b82f6;color:#fff;border-radius:8rpx;padding:10rpx 20rpx;font-size:22rpx;flex-shrink:0;">+ 新建AI</view>
    </view>
  </view>

  <!-- 模型卡片列表 -->
  <scroll-view scroll-y="true" style="height:calc(100vh - 380rpx);" bindscrolltolower="loadMore">
    <view style="padding:24rpx 30rpx;">
      <view class="model-card glass-card" wx:for="{{modelList}}" wx:key="id"
            bindtap="selectModel" data-id="{{item.id}}">
        <!-- 3D模型预览图 -->
        <view class="model-preview-wrap">
          <image src="{{item.previewImage}}" mode="aspectFit" class="model-preview-img" />
          <!-- 收藏按钮 -->
          <view class="model-favorite" catchtap="toggleFavorite" data-id="{{item.id}}">
            <text style="font-size:32rpx;{{item.isFavorite?'color:#ec4899;':'color:#888899;'}}">{{item.isFavorite?'❤️':'🤍'}}</text>
          </view>
          <!-- 状态标签 -->
          <view class="tag-status {{item.status==='RECENTLY_AI'?'tag-recently':''}} {{item.status==='HOT'?'tag-hot':''}}"
               wx:if="{{item.status}}">{{item.status}}</view>
        </view>
        <!-- 卡片信息 -->
        <view class="model-info">
          <view class="title-sm">{{item.name}}</view>
          <view style="display:flex;justify-content:space-between;align-items:center;margin-top:12rpx;">
            <text class="micro">{{item.polyCount}} Polygons</text>
            <view class="btn-outline" style="padding:10rpx 28rpx;font-size:22rpx;" catchtap="joinModel" data-id="{{item.id}}">Join Model</view>
          </view>
        </view>
      </view>

      <!-- 加载更多提示 -->
      <view wx:if="{{loadingMore}}" style="text-align:center;padding:30rpx;">
        <text class="caption">加载中...</text>
      </view>
      <view wx:if="{{noMoreData && modelList.length > 0}}" style="text-align:center;padding:30rpx;">
        <text class="micro">— 已加载全部 —</text>
      </view>
      <!-- 空状态 -->
      <view wx:if="{{modelList.length === 0 && !loading}}" style="text-align:center;padding:100rpx 0;">
        <text style="font-size:60rpx;">📭</text>
        <view class="caption" style="margin-top:20rpx;">暂无模型</view>
        <view class="btn-primary" style="margin-top:24rpx;display:inline-block;" bindtap="createNewAI">创建第一个模型</view>
      </view>
    </view>
  </scroll-view>
</view>
'''

    wxss = DESIGN_SYSTEM_CSS + """
/* ===== 建模库专属样式 ===== */
.search-placeholder { color: #555566; font-size: 26rpx; }

.model-card {
  padding: 0 !important;
  overflow: hidden;
  margin-bottom: 24rpx;
}

.model-preview-wrap {
  position: relative;
  width: 100%;
  height: 420rpx;
  background: rgba(10, 10, 20, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.model-preview-img {
  width: 75%;
  height: 90%;
}

/* 收藏按钮 */
.model-favorite {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  width: 56rpx;
  height: 56rpx;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10rpx);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 状态标签定位在预览图上 */
.model-info {
  padding: 20rpx 24rpx;
}
"""

    js = '''// clothDiy 建模库/数字人库
const app = getApp();

Page({
  data: {
    searchKeyword: '',
    currentGender: 'all',
    genderTabs: [
      { label: '全部', value: 'all' },
      { label: 'Male', value: 'male' },
      { label: 'Female', value: 'female' }
    ],
    modelList: [],
    loading: true,
    loadingMore: false,
    noMoreData: false,
    page: 1
  },

  onLoad() {
    this.loadModels();
  },

  onShow() {
    // 刷新收藏状态等
  },

  // 加载模型列表
  loadModels(refresh = true) {
    if (refresh) {
      this.setData({ loading: true, modelList: [], page: 1, noMoreData: false });
    }

    // 模拟数据（实际从API获取）
    setTimeout(() => {
      this.setData({
        modelList: [
          { id: 1, name: 'Standard Male v2.4', polyCount: '120K', previewImage: '/assets/model-male1.png', isFavorite: false, status: 'RECENTLY_AI', gender: 'male' },
          { id: 2, name: 'Athletic Female #1', polyCount: '85K', previewImage: '/assets/model-female1.png', isFavorite: true, status: '', gender: 'female' },
          { id: 3, name: 'Anatomical Base 82', polyCount: '250K', previewImage: '/assets/model-base.png', isFavorite: false, status: 'HOT', gender: 'male' },
          { id: 4, name: 'Fashion Male Slim', polyCount: '68K', previewImage: '/assets/model-slim.png', isFavorite: false, status: '', gender: 'male' },
          { id: 5, name: 'Elegant Female Curvy', polyCount: '92K', previewImage: '/assets/model-curvy.png', isFavorite: true, status: '', gender: 'female' },
          { id: 6, name: 'Anime Style Base', polyCount: '45K', previewImage: '/assets/model-anime.png', isFavorite: false, status: 'NEW', gender: 'female' }
        ],
        loading: false
      });
    }, 600);
  },

  // 性别筛选切换
  switchGender(e) {
    const val = e.currentTarget.dataset.value;
    this.setData({ currentGender: val });
    this.loadModels(true);
  },

  // 搜索
  onSearch(e) {
    this.setData({ searchKeyword: e.detail.value });
    this.loadModels(true);
  },

  // 选择模型 -> 进入试穿
  selectModel(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/tryon/tryon?modelId=${id}` });
  },

  // Join Model
  joinModel(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/tryon/tryon?modelId=${id}` });
  },

  // 收藏切换
  toggleFavorite(e) {
    const id = e.currentTarget.dataset.id;
    const list = this.data.modelList.map(m =>
      m.id === id ? { ...m, isFavorite: !m.isFavorite } : m
    );
    this.setData({ modelList: list });
  },

  // 创建新AI模型
  createNewAI() {
    wx.navigateTo({ url: '/pages/design/design?action=new_model' });
  },

  // 加载更多
  loadMore() {
    if (this.data.loadingMore || this.data.noMoreData) return;
    this.setData({ loadingMore: true });
    // TODO: API分页加载
    setTimeout(() => {
      this.setData({ loadingMore: false, noMoreData: true });
    }, 500);
  },

  goBack() {
    wx.navigateBack();
  }
});
'''

    json_content = '{\n  "usingComponents": {},\n  "navigationBarTitleText": ""\n}'
    write_page(page, wxml, wxss, js, json_content)


# ============================================================
# PAGE 4: 面料与组件库 (fabrics) - 基于UI图
# ============================================================
def gen_fabrics():
    page = "fabrics"
    wxml = '''<!-- 面料与组件库 - 材质网格展示 -->
<view class="page-container">
  <!-- 导航栏 -->
  <view class="navbar">
    <view class="navbar-title">面料与组件库</view>
    <text class="navbar-icon">🔔</text>
  </view>

  <!-- 搜索与筛选 -->
  <view style="padding:24rpx 30rpx 0;">
    <view class="search-bar">
      <text style="margin-right:12rpx;color:#555566;">🔍</text>
      <input placeholder="搜索面料/组件" placeholder-class="search-placeholder"
             style="flex:1;color:#e5e5e5;font-size:26rpx;" bindconfirm="onSearch" />
    </view>

    <!-- 分类筛选 -->
    <view style="display:flex;justify-content:space-between;align-items:center;margin-top:24rpx;">
      <scroll-view scroll-x="true" style="white-space:nowrap;flex:1;">
        <view style="display:inline-flex;gap:16rpx;">
          <view wx:for="{{categories}}" wx:key="value"
                class="{{currentCategory===item.value?'tag-active':'tag-inactive'}}"
                data-value="{{item.value}}" bindtap="switchCategory">{{item.label}}</view>
        </view>
      </scroll-view>
      <view class="btn-small" style="background:#7c3aed;color:#fff;border-radius:8rpx;padding:10rpx 20rpx;font-size:22rpx;flex-shrink:0;margin-left:16rpx;">NEW</view>
    </view>
  </view>

  <!-- 材质网格 -->
  <scroll-view scroll-y="true" style="height:calc(100vh - 360rpx);">
    <view style="padding:24rpx 30rpx;display:flex;flex-wrap:wrap;gap:20rpx;">
      <view class="fabric-card" wx:for="{{fabricList}}" wx:key="id" bindtap="selectFabric" data-id="{{item.id}}">
        <view class="fabric-img-wrap">
          <image src="{{item.image}}" mode="aspectFill" class="fabric-img" />
          <view class="fabric-tag" wx:if="{{item.badge}}">{{item.badge}}</view>
        </view>
        <view class="fabric-info">
          <text class="micro fabric-sku">{{item.sku}}</text>
          <text class="fabric-name">{{item.name}}</text>
          <text class="caption fabric-desc">{{item.desc}}</text>
          <text class="fabric-price">{{item.price}}</text>
        </view>
      </view>
    </view>
  </scroll-view>
</view>
'''

    wxss = DESIGN_SYSTEM_CSS + """
.fabric-card { width: calc(50% - 10rpx); }
.fabric-img-wrap { position: relative; width: 100%; aspect-ratio: 1; border-radius: 12rpx; overflow: hidden; background: rgba(255,255,255,0.03); }
.fabric-img { width: 100%; height: 100%; }
.fabric-tag { position: absolute; top: 12rpx; left: 12rpx; background: rgba(236,72,153,0.9); color: #fff; font-size: 18rpx; padding: 4rpx 12rpx; border-radius: 6rpx; }
.fabric-info { padding: 16rpx 4rpx 0; }
.fabric-sku { display: block; margin-bottom: 4rpx; }
.fabric-name { display: block; font-size: 25rpx; color: #e5e5e5; font-weight: 500; margin-bottom: 4rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fabric-desc { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-bottom: 8rpx; }
.fabric-price { display: block; font-size: 28rpx; color: #e5e5e5; font-weight: bold; }
.search-placeholder { color: #555566; }
"""

    js = '''// clothDiy 面料与组件库
Page({
  data: {
    currentCategory: 'all',
    categories: [
      { label: '全部', value: 'all' },
      { label: '纹理', value: 'texture' },
      { label: '金属', value: 'metal' },
      { label: '透明材质', value: 'transparent' },
      { label: '纽扣', value: 'button' }
    ],
    fabricList: []
  },

  onLoad() { this.loadFabrics(); },

  loadFabrics() {
    setTimeout(() => {
      this.setData({
        fabricList: [
          { id: 1, sku: 'SKU-A01', name: '柔光波浪皮革', desc: '高级羊皮质感，柔软触感', price: '¥68+', image: '/assets/fabric-wave.png', badge: '推荐', category: 'texture' },
          { id: 2, sku: 'SKU-B02', name: '磨砂黑金属膜', desc: '未来感哑光金属涂层', price: '¥55a', image: '/assets/fabric-metal.png', badge: '', category: 'metal' },
          { id: 3, sku: 'SKU-C03', name: '奢华天丝金箔绒', desc: '含1%金箔纤维，奢华光泽感', price: '¥550a', image: '/assets/fabric-gold.png', badge: '推荐', category: 'texture' },
          { id: 4, sku: 'SKU-D04', name: '素光透明纽扣板', desc: '高透光亚克力材质', price: '¥5+', image: '/assets/fabric-clear.png', badge: '', category: 'button' },
          { id: 5, sku: 'SKU-E05', name: '螺纹工装尼龙', desc: '耐磨防水，户外级品质', price: '¥89a', image: '/assets/fabric-nylon.png', badge: '', category: 'texture' },
          { id: 6, sku: 'SKU-F06', name: '幻彩变光丝绸', desc: '随角度变色的高级丝绸', price: '¥220a', image: '/assets/fabric-silk2.png', badge: 'NEW', category: 'transparent' },
          { id: 7, sku: 'SKU-G07', name: '红外穿透织物', desc: '特殊功能面料', price: '¥448a', image: '/assets/fabric-tech.png', badge: '', category: 'transparent' },
          { id: 8, sku: 'SKU-H08', name: '碳纤维编织纹', desc: '轻量高强度复合材料', price: '¥320a', image: '/assets/fabric-carbon.png', badge: '', category: 'metal' }
        ]
      });
    }, 400);
  },

  switchCategory(e) {
    this.setData({ currentCategory: e.currentTarget.dataset.value });
    this.loadFabrics();
  },

  selectFabric(e) {
    const id = e.currentTarget.dataset.id;
    // 将选中的面料加入当前设计
    app.globalData.currentDesignFabric = id;
    wx.showToast({ title: '已添加到设计', icon: 'success' });
  },

  onSearch(e) {
    console.log('搜索:', e.detail.value);
  }
});
'''

    json_content = '{\n  "usingComponents": {},\n  "navigationBarTitleText": ""\n}'
    write_page(page, wxml, wxss, js, json_content)


# ============================================================
# PAGE 5: 订单确认 (order/confirm) - 基于UI图
# ============================================================
def gen_order_confirm():
    page = "order/confirm"
    wxml = '''<!-- 订单确认/创意工坊 - 费用明细+支付 -->
<view class="page-container">
  <!-- 导航栏 -->
  <view class="navbar">
    <view class="navbar-title">创意工坊</view>
    <view class="navbar-right">
      <text class="navbar-icon">🔔</text>
      <image class="avatar-small" src="/images/avatar-default.png" mode="aspectFill"/>
    </view>
  </view>

  <!-- 步骤条 -->
  <view style="padding:30rpx 30rpx 10rpx;">
    <view class="step-bar">
      <view class="step-item {{step>=1?'step-done':''}}">
        <view class="step-circle {{step>=1?'active':''}}">{{step>1?'✓':'1'}}</view>
        <text>报价</text>
      </view>
      <view class="step-line {{step>=2?'active':''}}"></view>
      <view class="step-item {{step>=2?'step-done':''}}">
        <view class="step-circle {{step>=2?'active':''}}">2</view>
        <text>支付</text>
      </view>
      <view class="step-line {{step>=3?'active':''}}"></view>
      <view class="step-item">
        <view class="step-circle">3</view>
        <text>生产</text>
      </view>
    </view>
  </view>

  <!-- 设计预览 -->
  <view style="padding:0 30rpx;">
    <view class="glass-card" style="text-align:center;padding:30rpx;">
      <view style="position:relative;display:inline-block;">
        <image src="/assets/design-preview-shirt.png" mode="aspectFit" style="width:320rpx;height:380rpx;" />
        <!-- 右上角控制按钮 -->
        <view style="position:absolute;top:0;right:-20rpx;display:flex;gap:12rpx;">
          <view class="icon-btn" style="width:56rpx;height:56rpx;"><text style="font-size:24rpx;">🔄</text></view>
          <view class="icon-btn" style="width:56rpx;height:56rpx;"><text style="font-size:24rpx;">⛶</text></view>
        </view>
      </view>
      <view class="title-sm" style="margin-top:16rpx;">{{orderInfo.designName}}</view>
    </view>
  </view>

  <!-- 费用清单明细 -->
  <view style="padding:20rpx 30rpx 0;">
    <view class="glass-card">
      <view style="display:flex;align-items:center;gap:12rpx;margin-bottom:24rpx;">
        <text style="font-size:28rpx;">📋</text>
        <view class="title-md">费用清单明细</view>
      </view>

      <!-- 费用项 -->
      <view class="cost-item" wx:for="{{orderInfo.costItems}}" wx:key="name">
        <view class="cost-item-left">
          <view class="cost-icon-wrap">{{index===0?'☰':index===1?'🧵':'🔧'}}</view>
          <view>
            <view class="body-text" style="font-weight:500;">{{item.name}}</view>
            <text class="caption">{{item.spec}}</text>
          </view>
        </view>
        <view class="cost-item-right">
          <text class="text-price" style="font-size:28rpx;">¥{{item.price}}</text>
          <text class="micro" wx:if="{{item.detail}}">{{item.detail}}</text>
        </view>
      </view>
    </view>
  </view>

  <!-- 收货地址 -->
  <view style="padding:20rpx 30rpx 0;">
    <view class="glass-card-light" style="display:flex;justify-content:space-between;align-items:center;">
      <view style="display:flex;gap:16rpx;flex:1;">
        <text style="font-size:28rpx;">📍</text>
        <view>
          <view style="display:flex;align-items:center;gap:12rpx;">
            <text class="body-text" style="font-size:26rpx;">收货地址</text>
            <text class="section-more" style="font-size:22rpx;" bindtap="editAddress">修改</text>
          </view>
          <text class="caption">{{address.name}} ({{address.phone}})</text>
          <text class="caption" style="display:block;">{{address.detail}}</text>
        </view>
      </view>
    </view>
  </view>

  <!-- 支付方式 -->
  <view style="padding:24rpx 30rpx 0;">
    <text class="caption" style="display:block;margin-bottom:16rpx;">支付方式</text>
    <view style="display:flex;gap:16rpx;">
      <view class="pay-method {{payMethod==='wechat'?'selected':''}}" bindtap="selectPay" data-method="wechat">
        <text style="font-size:36rpx;">💬</text>
        <text class="micro">微信支付</text>
      </view>
      <view class="pay-method {{payMethod==='alipay'?'selected':''}}" bindtap="selectPay" data-method="alipay">
        <text style="font-size:36rpx;">💳</text>
        <text class="micro">支付宝</text>
      </view>
      <view class="pay-method {{payMethod==='bank'?'selected':''}}" bindtap="selectPay" data-method="bank">
        <text style="font-size:36rpx;">🏦</text>
        <text class="micro">银行卡</text>
      </view>
    </view>
  </view>

  <!-- 价格汇总 -->
  <view style="padding:24rpx 30rpx;">
    <view class="glass-card-light">
      <view class="price-row">
        <text class="body-text">小计</text>
        <text class="body-text">¥{{orderInfo.subtotal}}</text>
      </view>
      <view class="price-row">
        <text class="body-text">预计税费 ({{orderInfo.taxRate}})</text>
        <text class="body-text">¥{{orderInfo.taxAmount}}</text>
      </view>
      <view class="divider" style="margin:16rpx 0;"></view>
      <view class="price-row" style="align-items:flex-end;">
        <text class="body-text">总价 (Total)</text>
        <text style="font-size:44rpx;font-weight:bold;color:#e5e5e5;">¥{{orderInfo.total}}</text>
      </view>
    </view>
  </view>

  <!-- 确认支付按钮 -->
  <view style="padding:0 30rpx 40rpx;">
    <view class="btn-primary" style="height:96rpx;line-height:96rpx;font-size:30rpx;border-radius:16rpx;" bindtap="confirmPay">
      <text>✅ 确认并支付 ¥{{orderInfo.total}}</text>
    </view>
  </view>
</view>
'''

    wxss = DESIGN_SYSTEM_CSS + """
/* 步骤条 */
.step-bar { display: flex; align-items: center; justify-content: center; }
.step-item { display: flex; align-items: center; gap: 8rpx; flex-direction: column; }
.step-circle { width: 48rpx; height: 48rpx; border-radius: 50%; border: 2px solid #555566; display: flex; align-items: center; justify-content: center; font-size: 22rpx; color: #555566; }
.step-circle.active { border-color: #7c3aed; background: #7c3aed; color: #fff; }
.step-item text { font-size: 22rpx; color: #555566; margin-top: 6rpx; }
.step-item.step-done text { color: #7c3aed; }
.step-line { width: 80rpx; height: 2px; background: #333344; margin: 0 12rpx; margin-bottom: 30rpx; }
.step-line.active { background: #7c3aed; }

/* 费用项 */
.cost-item { display: flex; justify-content: space-between; align-items: flex-start; padding: 20rpx 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.cost-item:last-child { border-bottom: none; }
.cost-item-left { display: flex; gap: 16rpx; flex: 1; }
.cost-icon-wrap { width: 52rpx; height: 52rpx; background: rgba(255,255,255,0.05); border-radius: 10rpx; display: flex; align-items: center; justify-content: center; font-size: 24rpx; flex-shrink: 0; }
.cost-item-right { text-align: right; }

/* 支付方式 */
.pay-method { flex: 1; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16rpx; padding: 20rpx 0; display: flex; flex-direction: column; align-items: center; gap: 8rpx; }
.pay-method.selected { border-color: #7c3aed; background: rgba(124,58,237,0.08); }

/* 价格行 */
.price-row { display: flex; justify-content: space-between; padding: 8rpx 0; }

.avatar-small { width: 48rpx; height: 48rpx; border-radius: 50%; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.15); }
"""

    js = '''// clothDyi 订单确认/创意工坊
const app = getApp();

Page({
  data: {
    step: 2,
    payMethod: 'wechat',
    orderInfo: {
      designName: 'Custom_Suit_V2',
      costItems: [
        { name: '100% 桑蚕丝 (重磅)', spec: '面料 A - 珍珠白', price: '450.00', detail: '¥150.00 × 3.0 米' },
        { name: '天然贝母纽扣', spec: '辅料 B - 12mm', price: '48.00', detail: '¥8.00 × 6 个' },
        { name: '工艺制作费', spec: '高定缝制工坊', price: '800.00', detail: '固定金额' }
      ],
      subtotal: '1,298.00',
      taxRate: '13%',
      taxAmount: '168.74',
      total: '1,466.74'
    },
    address: {
      name: '张伟',
      phone: '+86 138****8888',
      detail: '上海市浦东新区张江高科技园区 碧波路 888 号'
    }
  },

  onLoad(options) {
    if (options.orderId) {
      this.loadOrderDetail(options.orderId);
    }
  },

  loadOrderDetail(orderId) {
    console.log('加载订单详情:', orderId);
    // TODO: 从API加载
  },

  selectPay(e) {
    this.setData({ payMethod: e.currentTarget.dataset.method });
  },

  editAddress() {
    wx.chooseAddress({
      success: (res) => {
        this.setData({
          address: {
            name: res.userName,
            phone: res.telNumber,
            detail: `${res.provinceName}${res.cityName}${res.countyName}${res.detailInfo}`
          }
        });
      }
    });
  },

  confirmPay() {
    wx.showModal({
      title: '确认支付',
      content: `确认支付 ¥${this.data.orderInfo.total}？`,
      confirmColor: '#7c3aed',
      success: (res) => {
        if (res.confirm) {
          this.doPayment();
        }
      }
    });
  },

  doPayment() {
    wx.showLoading({ title: '支付中...' });
    // TODO: 调用微信支付API
    setTimeout(() => {
      wx.hideLoading();
      wx.redirectTo({ url: '/pages/myspace/myspace?tab=orders&status=paid' });
    }, 1500);
  },

  goBack() { wx.navigateBack(); }
});
'''

    json_content = '{\n  "usingComponents": {},\n  "navigationBarTitleText": ""\n}'
    write_page(page, wxml, wxss, js, json_content)


# ============================================================
# PAGE 6: 我的空间 (myspace) - 基于UI图
# ============================================================
def gen_myspace():
    page = "myspace"
    wxml = '''<!-- 我的空间 - 我的设计/资产列表 -->
<view class="page-container">
  <!-- 导航栏 -->
  <view class="navbar">
    <view class="navbar-title">我的空间</view>
    <view class="navbar-right">
      <text class="navbar-icon">🔔</text>
      <image class="avatar-small" src="/images/avatar-default.png" mode="aspectFill"/>
    </view>
  </view>

  <!-- Tab切换 -->
  <view style="padding:24rpx 30rpx 0;">
    <view style="display:flex;gap:16rpx;">
      <view class="tab-switch {{activeTab==='designs'?'active':''}}" bindtap="switchTab" data-tab="designs">我的设计</view>
      <view class="tab-switch {{activeTab==='assets'?'active':''}}" bindtap="switchTab" data-tab="assets">我的资产</view>
    </view>
  </view>

  <!-- 设计列表 -->
  <scroll-view scroll-y="true" style="height:calc(100vh - 340rpx);">
    <view style="padding:24rpx 30rpx;">
      <!-- 设计卡片 -->
      <view class="design-card glass-card" wx:for="{{designList}}" wx:key="id" bindtap="openDesign" data-id="{{item.id}}">
        <!-- 状态标签 -->
        <view style="margin-bottom:16rpx;">
          <view class="tag-status {{item.status==='DRAFT'?'tag-draft':'tag-finalized'}}">{{item.status}}</view>
        </view>
        <!-- 3D预览图 -->
        <view class="design-preview-wrap">
          <image src="{{item.previewImage}}" mode="aspectContain" class="design-preview-img" />
          <view class="design-action-btn" wx:if="{{item.status==='DRAFT'}}" catchtap="editDesign" data-id="{{item.id}}">
            <text style="font-size:28rpx;color:#888899;">✏️</text>
          </view>
          <view class="design-action-btn" wx:else catchtap="viewDesign" data-id="{{item.id}}">
            <text style="font-size:28rpx;color:#888899;">👁</text>
          </view>
        </view>
        <!-- 信息 -->
        <view style="margin-top:16rpx;">
          <view class="title-md">{{item.name}}</view>
          <text class="caption" style="display:block;margin-top:6rpx;">{{item.updatedAt}}</text>
          <text class="micro" style="display:block;margin-top:4rpx;">{{item.material}}</text>
        </view>
      </view>
    </view>
  </scroll-view>

  <!-- 浮动新建按钮 -->
  <view class="floating-btn" bindtap="createNew">
    <text style="color:#fff;font-size:26rpx;">+ Create New</text>
  </view>
</view>
'''

    wxss = DESIGN_SYSTEM_CSS + """
.tab-switch { padding: 14rpx 36rpx; border-radius: 12rpx; font-size: 26rpx; color: #888899; background: rgba(255,255,255,0.04); }
.tab-switch.active { background: #4f46e5; color: #fff; }

.design-card { padding: 24rpx !important; margin-bottom: 24rpx; }
.design-preview-wrap { position: relative; width: 100%; height: 360rpx; background: rgba(10,10,20,0.6); border-radius: 12rpx; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.design-preview-img { width: 85%; height: 90%; }
.design-action-btn { position: absolute; top: 16rpx; right: 16rpx; width: 56rpx; height: 56rpx; background: rgba(0,0,0,0.4); backdrop-filter: blur(10rpx); border-radius: 50%; display: flex; align-items: center; justify-content: center; }

.floating-btn { position: fixed; bottom: 160rpx; right: 30rpx; background: linear-gradient(135deg, #4f46e5, #7c3aed); padding: 20rpx 36rpx; border-radius: 40rpx; box-shadow: 0 8rpx 32rpx rgba(79,70,229,0.35); z-index: 100; }
.floating-btn::after { border: none; }

.avatar-small { width: 48rpx; height: 48rpx; border-radius: 50%; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.15); }
"""

    js = '''// clothDiy 我的空间
Page({
  data: {
    activeTab: 'designs',
    designList: []
  },

  onLoad(options) {
    if (options.tab) this.setData({ activeTab: options.tab });
    this.loadDesigns();
  },

  onShow() { this.loadDesigns(); },

  switchTab(e) { this.setData({ activeTab: e.currentTarget.dataset.tab }); },

  loadDesigns() {
    setTimeout(() => {
      this.setData({
        designList: [
          { id: 101, name: 'Cyber-Tech Shell V1', status: 'DRAFT', updatedAt: 'Updated 2 hours ago', material: 'Polyester Blend', previewImage: '/assets/design-jacket.png' },
          { id: 102, name: 'Neo-Minimalist Gown', status: 'FINALIZED', updatedAt: 'Finalized Jan 12, 2024', material: 'Silk Tech Blend', previewImage: '/assets/design-dress.png' },
          { id: 103, name: 'Urban Utility Rig', status: 'DRAFT', updatedAt: 'Updated 3 days ago', material: 'Heavy Cotton Twill', previewImage: '/assets/design-hoodie.png' }
        ]
      });
    }, 300);
  },

  openDesign(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/order/confirm?designId=${id}` });
  },

  editDesign(e) {
    wx.navigateTo({ url: `/pages/design/design?designId=${e.currentTarget.dataset.id}` });
  },

  viewDesign(e) { /* 查看详情 */ },

  createNew() {
    wx.navigateTo({ url: '/pages/design/design?action=new' });
  }
});
'''

    json_content = '{\n  "usingComponents": {},\n  "navigationBarTitleText": ""\n}'
    write_page(page, wxml, wxss, js, json_content)


# ============================================================
# PAGE 7: 个人中心 (profile) - 基于UI图
# ============================================================
def gen_profile():
    page = "profile"
    wxml = '''<!-- 个人中心 - 用户信息+设置 -->
<view class="page-container">
  <!-- 导航栏 -->
  <view class="navbar">
    <view class="navbar-title">个人中心</view>
    <text class="navbar-icon">🔔</text>
  </view>

  <!-- 用户信息卡 -->
  <view style="padding:40rpx 30rpx;text-align:center;">
    <view style="position:relative;display:inline-block;">
      <image src="/images/avatar-default.png" mode="aspectFill" class="profile-avatar" />
      <view class="verify-badge">
        <text style="color:#3b82f6;font-size:24rpx;">✔️</text>
      </view>
    </view>
    <view class="profile-name">Alex Chen</view>
    <view style="display:flex;justify-content:center;gap:12rpx;margin-top:12rpx;">
      <view class="member-tag member-vip">高级会员</view>
      <view class="member-tag member-enterprise">企业用户(TIER)</view>
    </view>
    <view class="btn-primary profile-edit-btn" style="margin-top:24rpx;display:inline-block;padding:16rpx 48rpx;" bindtap="editProfile">✏️ 编辑个人资料</view>
  </view>

  <!-- 统计卡片 -->
  <view style="padding:0 30rpx;display:flex;gap:16rpx;">
    <view class="stat-card glass-card" style="flex:1;text-align:center;padding:28rpx 16rpx;">
      <text style="font-size:44rpx;color:#7c3aed;font-weight:bold;">24</text>
      <text class="caption" style="display:block;margin-top:8rpx;">我的设计</text>
    </view>
    <view class="stat-card glass-card" style="flex:1;text-align:center;padding:28rpx 16rpx;">
      <text style="font-size:44rpx;color:#3b82f6;font-weight:bold;">5</text>
      <text class="caption" style="display:block;margin-top:8rpx;">我的模型</text>
    </view>
    <view class="stat-card glass-card" style="flex:1;text-align:center;padding:28rpx 16rpx;">
      <text style="font-size:44rpx;color:#06b6d4;font-weight:bold;">3</text>
      <text class="caption" style="display:block;margin-top:8rpx;">进行中的订单</text>
    </view>
  </view>

  <!-- 设置菜单 -->
  <view style="padding:30rpx 30rpx 0;">
    <text class="micro" style="display:block;margin-bottom:16rpx;color:#555566;letter-spacing:2rpx;">账户设置</text>
    <view class="glass-card-light" style="padding:0;">
      <view class="menu-item" wx:for="{{menuList}}" wx:key="label" bindtap="onMenuTap" data-index="{{index}}">
        <view style="display:flex;align-items:center;gap:20rpx;">
          <text style="font-size:32rpx;">{{item.icon}}</text>
          <text class="body-text">{{item.label}}</text>
        </view>
        <text style="color:#555566;font-size:28rpx;">></text>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-btn" bindtap="logout">
      <text style="color:#ef4444;">🚪 Logout</text>
    </view>
  </view>
</view>
'''

    wxss = DESIGN_SYSTEM_CSS + """
.profile-avatar { width: 160rpx; height: 160rpx; border-radius: 50%; border: 3px solid rgba(124,58,237,0.4); }
.verify-badge { position: absolute; bottom: 4rpx; right: 4rpx; width: 40rpx; height: 40rpx; background: #12121a; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #3b82f6; }
.profile-name { font-size: 40rpx; font-weight: bold; color: #e5e5e5; margin-top: 16rpx; }
.member-tag { font-size: 20rpx; padding: 6rpx 16rpx; border-radius: 8rpx; }
.member-vip { background: rgba(124,58,237,0.15); color: #a78bfa; }
.member-enterprise { background: rgba(59,130,246,0.15); color: #60a5fa; }
.profile-edit-btn { border-radius: 40rpx !important; }

.stat-card .glass-card { padding: 28rpx 16rpx !important; }

.menu-item { display: flex; justify-content: space-between; align-items: center; padding: 28rpx 24rpx; border-bottom: 1px solid rgba(255,255,255,0.04); }
.menu-item:last-child { border-bottom: none; }
.menu-item:active { background: rgba(255,255,255,0.02); }

.logout-btn { margin-top: 30rpx; text-align: center; padding: 24rpx; background: rgba(255,255,255,0.03); border-radius: 16rpx; border: 1px solid rgba(239,68,68,0.15); }
"""

    js = '''// clothDiy 个人中心
Page({
  data: {
    userInfo: {},
    menuList: [
      { icon: '🛡️', label: 'Account Security', action: 'security' },
      { icon: '💳', label: 'Payment Methods', action: 'payment' },
      { icon: '🔒', label: 'Privacy Settings', action: 'privacy' },
      { icon: '🔔', label: 'Notification Preferences', action: 'notification' },
      { icon: '❓', label: 'Help & Support', action: 'help' },
      { icon: 'ℹ️', label: 'About Forge 3D', action: 'about' }
    ],
    stats: { designs: 24, models: 5, orders: 3 }
  },

  onLoad() { this.loadUserInfo(); },

  loadUserInfo() {
    // TODO: 从app.globalData或API加载用户信息
    this.setData({ userInfo: { name: 'Alex Chen', avatar: '/images/avatar-default.png' } });
  },

  editProfile() {
    wx.showToast({ title: '开发中...', icon: 'none' });
  },

  onMenuTap(e) {
    const action = this.data.menuList[e.currentTarget.dataset.index].action;
    console.log('菜单操作:', action);
    wx.showToast({ title: `即将开放: ${action}`, icon: 'none' });
  },

  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出当前账号吗？',
      confirmColor: '#ef4444',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorageSync();
          wx.reLaunch({ url: '/pages/index/index' });
        }
      }
    });
  }
});
'''

    json_content = '{\n  "usingComponents": {},\n  "navigationBarTitleText": ""\n}'
    write_page(page, wxml, wxss, js, json_content)


# ============================================================
# 全局配置更新
# ============================================================
def update_global_config():
    """更新 app.json、app.js、app.wxss 等"""

    # app.json - 5个TabBar + 正确页面注册
    app_json = '''{
  "pages": [
    "pages/index/index",
    "pages/models/models",
    "pages/design/design",
    "pages/tryon/tryon",
    "pages/fabrics/fabrics",
    "pages/order/confirm",
    "pages/myspace/myspace",
    "pages/profile/profile"
  ],
  "window": {
    "backgroundColor": "#0a0a14",
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#0a0a14",
    "navigationBarTextStyle": "white",
    "navigationStyle": "custom"
  },
  "tabBar": {
    "color": "#555566",
    "selectedColor": "#7c3aed",
    "backgroundColor": "#0a0a14",
    "borderStyle": "black",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "走秀",
        "iconPath": "images/tab-runway.png",
        "selectedIconPath": "images/tab-runway-active.png"
      },
      {
        "pagePath": "pages/models/models",
        "text": "建模",
        "iconPath": "images/tab-model.png",
        "selectedIconPath": "images/tab-model-active.png"
      },
      {
        "pagePath": "pages/design/design",
        "text": "工坊",
        "iconPath": "images/tab-studio.png",
        "selectedIconPath": "images/tab-studio-active.png"
      },
      {
        "pagePath": "pages/order/confirm",
        "text": "订单",
        "iconPath": "images/tab-order.png",
        "selectedIconPath": "images/tab-order-active.png"
      },
      {
        "pagePath": "pages/myspace/myspace",
        "text": "资产",
        "iconPath": "images/tab-assets.png",
        "selectedIconPath": "images/tab-assets-active.png"
      }
    ]
  },
  "sitemapLocation": "sitemap.json"
}'''
    write_file(f"{BASE}/app.json", app_json)

    # app.wxss - 全局深色设计系统
    app_wxss = '''/* ========================================
   clothDiy Global Styles - 深色科技风
   ======================================== */

page {
  background-color: #0a0a14;
  color: #e5e5e5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* 全局滚动条隐藏 */
::-webkit-scrollbar { display: none; }

view, text, image { box-sizing: border-box; }
'''
    write_file(f"{BASE}/app.wxss", app_wxss)

    # app.js - 全局数据和流程管理
    app_js = '''/**
 * clothDiy App - 全局状态管理 & 流程控制
 *
 * 用户完整流程链路:
 * 首页 → 建模库 → 创建建模 → 设计衣服 → 动态试穿 → 下订单 → 订单确认 → 支付 → 我的空间
 */
App({
  globalData: {
    // 用户信息
    userInfo: null,

    // 当前设计流程状态
    currentFlow: {
      step: 'home',       // home | models | design | tryon | order | payment | done
      selectedModel: null,   // 选中的3D模型ID
      currentDesign: null,   // 当前设计ID
      selectedFabrics: [],   // 选中的面料
      orderDraft: {}         // 订单草稿
    },

    // API 配置
    apiBaseUrl: 'https://api.clothdiy.com/v1'
  },

  onLaunch() {
    console.log('🎨 clothDiy App Launched');

    // 检查登录状态
    this.checkLoginStatus();

    // 更新系统信息
    const sysInfo = wx.getSystemInfoSync();
    this.globalData.systemInfo = sysInfo;
    this.globalData.statusBarHeight = sysInfo.statusBarHeight;
  },

  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    if (token) {
      this.globalData.userInfo = wx.getStorageSync('userInfo') || null;
    }
  },

  // 流程导航辅助
  setFlowStep(step, data = {}) {
    Object.assign(this.globalData.currentFlow, { step }, data);
  },

  getFlowStep() {
    return this.globalData.currentFlow.step;
  }
});
'''
    write_file(f"{BASE}/app.js", app_js)

    print("  ✅ 全局配置更新完成 (app.json/app.js/app.wxss)")


# ============================================================
# 主执行入口
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("  clothDiy UI 严格还原生成器")
    print("  基于UI设计图 | 深色科技风主题")
    print("=" * 60)

    print("\n[1/8] 生成首页 (index)...")
    gen_index()

    print("\n[2/8] 生成动态试穿 (tryon)...")
    gen_tryon()

    print("\n[3/8] 生成建模库 (models)...")
    gen_models()

    print("\n[4/8] 生成面料库 (fabrics)...")
    gen_fabrics()

    print("\n[5/8] 生成订单确认 (order/confirm)...")
    gen_order_confirm()

    print("\n[6/8] 生成我的空间 (myspace)...")
    gen_myspace()

    print("\n[7/8] 生成个人中心 (profile)...")
    gen_profile()

    print("\n[8/8] 更新全局配置...")
    update_global_config()

    print("\n" + "=" * 60)
    print("  ✅ 所有页面已按UI设计图重新生成!")
    print("  📋 请在微信开发者工具中刷新查看")
    print("=" * 60)
