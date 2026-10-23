# Codex + Cloudflare 固定网址方法

目标：让 Codex 生成的 HTML 不只停留在本地文件，而是发布成可以长期分享和反复更新的固定网址。

## 核心逻辑

- Cloudflare Pages 项目名固定。
- 每次把新的 HTML、CSS、JS 部署到同一个项目。
- 访问者始终打开同一个 `https://项目名.pages.dev` 地址。

## 本项目使用的固定项目名

```bash
amazon-ads-ai-optimizer-20260626
```

## 首次授权

```bash
npm.cmd run login
```

这一步会打开 Cloudflare 登录授权页面，需要人工登录、注册或授权。

## 发布

```bash
npm.cmd run deploy
```

发布成功后，Cloudflare 会返回正式访问链接。后续更新仍然运行同一个命令。

本项目的正式访问链接：

```bash
https://amazon-ads-ai-optimizer-20260626.pages.dev
```
