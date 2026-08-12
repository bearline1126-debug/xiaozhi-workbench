#!/usr/bin/env bash
# scripts/push.sh
# 用途：用本地 secrets 文件里的 GitHub PAT 推送 master 到 origin。
#
# 首次使用（把 token 保存到 repo 外的本地 secrets 文件，**不进仓库 / 提交 / 公开页面**）：
#   mkdir -p "$HOME/.workbuddy/secrets"
#   echo 'ghp_你的GitHub_PAT_一行' > "$HOME/.workbuddy/secrets/github-push-token.txt"
#   chmod 600 "$HOME/.workbuddy/secrets/github-push-token.txt"
#
# 之后每次部署只要：
#   bash scripts/push.sh
#
# 软件到达最终版后，删除该 token 文件即可彻底清理：
#   rm "$HOME/.workbuddy/secrets/github-push-token.txt"

set -e

TOKEN_FILE="$HOME/.workbuddy/secrets/github-push-token.txt"

if [ ! -f "$TOKEN_FILE" ]; then
  echo "❌ 找不到 token 文件：$TOKEN_FILE"
  echo "   请先把 GitHub PAT 一行写入该文件，再重跑。详见本脚本顶部注释。"
  exit 1
fi

# 只取第一行、去空白
TOKEN="$(head -n 1 "$TOKEN_FILE" | tr -d '\r\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
if [ -z "$TOKEN" ]; then
  echo "❌ token 文件为空：$TOKEN_FILE"
  exit 1
fi

# 防御性检查：必须是 ghp_/github_pat_ 等 GitHub PAT 前缀，避免误把别的串当 token
case "$TOKEN" in
  ghp_*|github_pat_*) ;;
  *) echo "⚠️ token 看起来不像 GitHub PAT（应以 ghp_ 或 github_pat_ 开头），仍尝试推送…";;
esac

# 关键：用 -c url."https://TOKEN@github.com/".insteadOf 改写远程地址，绝不能反写
# （反写会把整个 github.com 重定向到带 token 的地址，导致所有 git 操作都试图用 token 认证）
git -c "url.https://${TOKEN}@github.com/.insteadOf=https://github.com/" push origin master
echo "✅ push 完成"