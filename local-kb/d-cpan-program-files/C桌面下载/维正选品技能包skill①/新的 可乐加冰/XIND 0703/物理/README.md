# Geo Consistency (Local)

一个 Chrome Manifest V3 扩展：让**浏览器可见的地区画像**（地理位置 / 时区 / 语言）与**当前出口 IP** 保持一致。
典型场景是使用 VPN / 代理时，浏览器仍暴露真实时区、语言、地理坐标，造成画像不一致——本扩展消除这种不一致。

## 隐私模型（Privacy Model）

- **无 telemetry、无 analytics、无账号系统、无远程配置。** 扩展不会向任何“自有”服务器上报数据。
- **不读取网页内容。** 注入脚本只覆盖 `navigator` / `Intl` / `Date` 上的少数 API，不读取、不收集、不发送页面 DOM、表单或输入。
- **只本地存储。** 所有设置与计算出的 override 仅存于 `chrome.storage.local`，不同步、不外发。
- **外部请求仅用于：**
  1. 出口 IP + IP 地理定位：`ipapi.co`、`ipwho.is`、`ipinfo.io`（按顺序 fallback）；
  2. 住宅道路坐标匹配：OpenStreetMap Overpass（`overpass-api.de`）。
  这些请求只发送“查询我的出口 IP 对应的位置”所必需的内容；不携带页面信息，不携带可标识用户的 token（除非你**主动**在设置里填入可选的 ipinfo token）。
- ipinfo token 为**可选**，留空即跳过；填入后仅用于向 ipinfo.io 发起该次查询。

## 工作原理（Pipeline）

1. **出口 IP 检测**：后台 service worker 通过 Chrome 网络栈 `fetch` IP geolocation provider，得到浏览器实际出口 IP 及其国家码、城市/地区/国家、经纬度、ISP、IANA 时区。多 provider 依次 fallback。
2. **坐标选择**：不直接使用 IP 中心点。优先用 Overpass 查询附近 `highway=residential` 住宅道路节点并选一个合理坐标；失败时用 `jitter` 在精度半径内随机偏移作为安全兜底。
3. **locale 推断**：由 `国家码 + 时区` 推断 `navigator.language` / `navigator.languages` / `Accept-Language`（多语言国家按时区细分，如蒙特利尔→fr-CA）。
4. **页面覆盖**：
   - `navigator.geolocation.getCurrentPosition / watchPosition / clearWatch`
   - `navigator.permissions.query({name:'geolocation'})` → `granted`
   - `Date.prototype.getTimezoneOffset`（按调用者 Date 实例、DST-aware）
   - `Intl.DateTimeFormat` 的默认 timeZone 与 `resolvedOptions().timeZone`
   - `navigator.language` / `navigator.languages`
   - `Intl.DateTimeFormat / NumberFormat / Collator` 的默认 locale
5. **Accept-Language 请求头**：语言开关开启时，用 `chrome.declarativeNetRequest` 动态规则改写外发的 `Accept-Language`。

### 注入时序（为什么可靠）

- `inject.js` 以 `world: "MAIN"`、`run_at: "document_start"` 注入，**同步安装所有 hook**，先于页面脚本执行；
- override 的**具体值**由 `content.js`（ISOLATED world）读取 `chrome.storage.local` 后，经 DOM 属性 + 事件跨 world 传入；
- 在值到达前，每个 hook 透明回退到原始行为，因此不会出现“hook 未装好就被页面调用”的竞态。

## 安装（开发者模式）

1. `chrome://extensions` → 打开右上角 **开发者模式**；
2. **加载已解压的扩展程序** → 选择本目录；
3. 点击工具栏图标打开 popup → **Refresh now** 生成首个画像。
> 需要 Chrome 111+（`world: "MAIN"` 内容脚本）。

## 设置项（Popup）

- Location / Timezone / Language 三个独立开关；
- 精度：Precise(~50m) / Neighborhood(~500m) / District(~1.5km) / City(~5km)；
- 刷新间隔（分钟，最小 5）；
- 可选 ipinfo token；
- 手动刷新。

## 测试

```bash
npm test        # node --test
```

覆盖：时区 DST 偏移（含南半球、半小时区、DST 边界翻转）、locale 推断（含时区覆盖）、provider 解析归一化、geo（haversine/jitter/住宅节点选取）、manifest 注入顺序与“capture-before-patch”。

> `lib/tz.js` 的 DST 偏移函数与 `inject.js` 内的同名实现是**同一逻辑的镜像**（页面 MAIN world 无法 import ES 模块），修改时需同步。

## 已知限制

- 仅覆盖常见指纹面（`getTimezoneOffset`、`Intl.*.resolvedOptions`、`navigator` 语言、geolocation）。`Date.prototype.toString` 等使用引擎内建 tz 名称的路径不在覆盖范围内。
- WebRTC / 系统级 DNS 泄漏等不属于本扩展范畴，应由 VPN / 浏览器隐私设置处理。
- provider 与 Overpass 为第三方公共服务，可能限流；已内置超时与 fallback。
