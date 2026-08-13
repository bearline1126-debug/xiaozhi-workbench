#!/bin/bash
# 用法： bash deploy_github.sh
# token 从 ~/.workbuddy/github-token.txt 读，一次粘贴永久用。
# 用户首次部署：把 token 粘到那个文件里，之后所有推送自动用同一个 token。

set -e
WORK_DIR="/c/Users/cheng/Documents/Codex/2026-08-10/skill-1-skill-skill-md-2/小彘的工作台 - v2-workbuddy"
TOKEN_FILE="/c/Users/cheng/.workbuddy/github-token.txt"

if [ ! -f "$TOKEN_FILE" ]; then
  echo "❌ 没找到 token 文件: $TOKEN_FILE"
  echo "   请先创建这个文件，里面粘贴你的 GitHub PAT。"
  echo "   旧 token 已经在之前对话里明文泄露过，记得去 https://github.com/settings/tokens 撤销。"
  exit 1
fi

# 从文件里抽取真正的 token（兼容文件里混入了说明注释的情况）：
# 匹配 ghp_/github_pat_ 开头的串，取长度最长的那一个当作真 token
TOKEN=$(grep -oE '(github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9]+)' "$TOKEN_FILE" \
  | awk '{ print length($0), $0 }' | sort -rn | head -1 | cut -d' ' -f2-)
if [[ -z "$TOKEN" ]]; then
  echo "❌ token 文件里没找到 ghp_/github_pat_ 形式的 token，请确认粘贴正确。"
  exit 1
fi
echo "✓ 已从文件中抽取到 token（前缀: ${TOKEN:0:12}..., 长度: ${#TOKEN}）"

cd "$WORK_DIR"

# 验证本地 token 是否能在 github 认证
echo "🔑 正在用本地 token 验证 GitHub 访问..."
# fine-grained PAT 用 Bearer，classic PAT 也可兼容
# 沙箱里 `curl -o /dev/null -w "%{http_code}"` 偶尔会因为"client returned ERROR on write"退出 23。
# 改成把响应体写到临时文件，最后再读 HTTP code。
HTTP_TMP=$(mktemp)
HTTP_CODE=$(curl -sS -H "Authorization: Bearer $TOKEN" -o "$HTTP_TMP" -w "%{http_code}" https://api.github.com/user 2>/dev/null || echo 000)
rm -f "$HTTP_TMP"
if [ "$HTTP_CODE" != "200" ]; then
  echo "❌ GitHub 校验失败 (HTTP $HTTP_CODE)。请检查 token 是否过期/撤销/权限不足。"
  exit 1
fi
echo "✅ 校验通过，开始推送..."

# 用 git config + insteadOf 把 token 注入到 URL，再 push
# 注意：insteadOf 是「把左边替换成右边」，左边是被替换的原始 URL
git -c url."https://$TOKEN@github.com/".insteadOf="https://github.com/" push origin master

echo "✅ 推送完成。"
