# clothDiy 页面重构计划

## 一、页面重命名方案（标准微信小程序规范）

| 原名称 | 新路径 | 说明 |
|--------|--------|------|
| 首页 (Home) | `pages/index/index` | 首页，TabBar |
| 建模库 (Model Library) | `pages/models/models` | 建模库，TabBar |
| 面料与组件库 (Fabric Library) | `pages/fabrics/fabrics` | 面料库 |
| 动态试穿 (Dynamic Try-On) | `pages/tryon/tryon` | 3D试穿页 |
| 设计衣服 (Design) | `pages/design/design` | 衣服设计页（新增） |
| 确认订单 - 费用明细 | `pages/order/confirm` | 订单确认Step1 |
| 订单确认 - 支付页 | `pages/order/payment` | 订单支付页 |
| 订单预览 | `pages/order/preview` | 订单预览（新增） |
| 个人中心 - Profile | `pages/profile/profile` | 个人中心，TabBar |
| 我的空间 (My Space) | `pages/myspace/myspace` | 我的空间 |

**TabBar 配置（4个标签页）**：
- `pages/index/index` - 首页
- `pages/models/models` - 建模库
- `pages/myspace/myspace` - 我的空间
- `pages/profile/profile` - 个人中心

## 二、完整用户流程链路（闭环）

```
[首页]
  │
  ├─→ [建模库] ─→ [创建建模] (3D建模页面)
  │      │
  │      └─→ [设计衣服] ─→ [动态试穿] (查看效果)
  │                        │
  │                        └─→ [订单预览] ─→ [订单确认/支付]
  │                                            │
  │                                            └─→ [我的空间] (查看订单)
  │
  ├─→ [面料库] ──→ [设计衣服] (选择面料后设计)
  │
  └─→ [个人中心] ─→ [我的订单] ─→ [订单详情]
```

**详细流程**：
1. 用户打开首页 `pages/index/index`
2. 点击"开始设计" → 跳转 `pages/models/models` (建模库)
3. 选择/创建3D建模 → 跳转 `pages/design/design` (设计衣服)
4. 设计完成 → 跳转 `pages/tryon/tryon` (动态试穿，查看效果)
5. 满意后 → 跳转 `pages/order/preview` (订单预览)
6. 确认 → 跳转 `pages/order/confirm` (费用明细)
7. 支付 → 跳转 `pages/order/payment` (支付页)
8. 完成 → 跳转 `pages/myspace/myspace` (我的空间，查看订单)

## 三、执行步骤

### Step 1: 创建标准页面目录结构
- 创建所有标准路径的页面目录
- 写入正确的 `page.json` 注册页面

### Step 2: 生成/重写每个页面的代码
- `pages/index/index` - 首页（带3D展示区、快捷入口）
- `pages/models/models` - 建模库（列表+上传）
- `pages/design/design` - 设计页（选择面料、款式、颜色）
- `pages/tryon/tryon` - 试穿页（Three.js 3D试穿）
- `pages/fabrics/fabrics` - 面料库（列表+筛选）
- `pages/order/preview` - 订单预览（效果图+价格）
- `pages/order/confirm` - 订单确认（费用明细）
- `pages/order/payment` - 支付页（微信支付）
- `pages/myspace/myspace` - 我的空间（作品+订单）
- `pages/profile/profile` - 个人中心（用户信息+设置）

### Step 3: 实现页面间导航
每个页面的 JS 文件里实现：
- `goToModels()` → `wx.navigateTo({ url: '/pages/models/models' })`
- `goToDesign(modelId)` → `wx.navigateTo({ url: '/pages/design/design?modelId=xxx' })`
- `goToTryon(designId)` → `wx.navigateTo({ url: '/pages/tryon/tryon?designId=xxx' })`
- `goToOrderPreview()` → `wx.navigateTo({ url: '/pages/order/preview' })`
- `goToOrderConfirm()` → `wx.navigateTo({ url: '/pages/order/confirm' })`
- `goToPayment()` → `wx.navigateTo({ url: '/pages/order/payment' })`
- `goToMyspace()` → `wx.switchTab({ url: '/pages/myspace/myspace' })`

### Step 4: 配置 app.json
- 注册所有页面路径
- 配置 TabBar
- 配置 window 样式

### Step 5: 双AI审核
- 每个页面生成后，自动触发 UI 审核 + 功能测试
- 分数 < 80 则自动迭代修复

## 四、关键技术点

1. **页面传参**：使用 URL query 传递 `modelId`, `designId`, `orderId`
2. **TabBar 页面只能使用 `wx.switchTab` 跳转**
3. **非TabBar 页面使用 `wx.navigateTo`**
4. **返回使用 `wx.navigateBack`**
5. **3D 功能使用 threejs-miniprogram 适配库**

## 五、执行优先级

1. **P0**（必须完成）：首页、建模库、设计页、试穿页、订单页、我的空间
2. **P1**（重要）：面料库、个人中心、订单预览
3. **P2**（优化）：迭代修复、3D功能完善
