#!/usr/bin/env bash
# 把本目录初始化为 git 仓库并推送到你自己的 GitHub 账号。
#
# 用法：
#   1) 先在 GitHub 网页上新建一个空仓库（不要勾选 Add README / .gitignore / license）
#   2) 在本目录执行：
#        bash scripts/push-to-github.sh <你的用户名> <仓库名>
#      例：bash scripts/push-to-github.sh yourname sp-api-summit-2026-notes
#
# 需要本机已安装 git，并且已配置好 SSH key 或 GitHub CLI 登录。

set -euo pipefail

USER="${1:-}"
REPO="${2:-sp-api-summit-2026-notes}"

if [[ -z "$USER" ]]; then
  echo "用法: bash scripts/push-to-github.sh <GitHub用户名> [仓库名]"
  exit 1
fi

cd "$(dirname "$0")/.."

if [[ ! -d .git ]]; then
  git init
  git branch -M main
fi

git add -A
git commit -m "docs: 2026 SP-API 中国开发者大会资料整理 v2.1

- 9 份原始文档按业务主题合并去重为一份主文档
- 每条结论标注证据等级：现场 / 官方 / 实测 / 解读 / 待核实
- 42 张现场照片（压缩至长边 1800px）与索引
- 官方仓库核验要点、待核实清单 Q01-Q18、50 条链接目录
- 原始文档保留在 archive/" || echo "没有需要提交的变更"

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "git@github.com:${USER}/${REPO}.git"
else
  git remote add origin "git@github.com:${USER}/${REPO}.git"
fi

echo
echo "即将推送到 git@github.com:${USER}/${REPO}.git"
echo "如果你用 HTTPS 而不是 SSH，请先执行："
echo "  git remote set-url origin https://github.com/${USER}/${REPO}.git"
echo
read -r -p "确认推送？(y/N) " ans
[[ "$ans" == "y" || "$ans" == "Y" ]] || { echo "已取消"; exit 0; }

git push -u origin main

echo
echo "完成。若想开启网页版："
echo "  Settings → Pages → Source 选 main 分支、目录选 /docs → 保存"
echo "  几分钟后访问 https://${USER}.github.io/${REPO}/"
