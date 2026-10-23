# 亚马逊广告优化板块网站

这是一个可直接发布到 Cloudflare Pages 的静态网站。

固定项目名：

```bash
amazon-ads-ai-optimizer-20260626
```

固定网址创建后会是：

```bash
https://amazon-ads-ai-optimizer-20260626.pages.dev
```

以后只要继续部署到同一个 `project-name`，网址不变，页面内容会更新。

## 发布流程

1. 首次授权 Cloudflare：

```bash
npm.cmd run login
```

2. 首次发布或后续更新：

```bash
npm.cmd run deploy
```

如果 `npm` 在 PowerShell 里被系统策略拦截，使用 `npm.cmd`。

当前固定网址：

```bash
https://amazon-ads-ai-optimizer-20260626.pages.dev
```
