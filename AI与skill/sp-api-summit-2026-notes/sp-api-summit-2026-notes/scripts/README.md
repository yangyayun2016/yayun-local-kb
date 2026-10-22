# scripts

| 文件 | 用途 |
|---|---|
| `push-to-github.sh` | 初始化 git 仓库并推送到你自己的 GitHub 账号；推送前会二次确认 |

也可以不用脚本，手工执行：

```bash
cd sp-api-summit-2026-notes
git init && git branch -M main
git add -A
git commit -m "docs: 2026 SP-API 中国开发者大会资料整理 v2.1"
git remote add origin git@github.com:<你的用户名>/sp-api-summit-2026-notes.git
git push -u origin main
```

开启网页版：仓库 Settings → Pages → Source 选 `main` 分支、目录选 `/docs` → 保存。
