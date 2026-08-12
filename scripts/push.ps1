# scripts/push.ps1
# 用途：用本地 secrets 文件里的 GitHub PAT 推送 master 到 origin（PowerShell 版）。
#
# 首次使用（token 仅存于本机 repo 外的 secrets 文件，**不进仓库 / 提交 / 公开页面**）：
#   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.workbuddy\secrets"
#   Set-Content -Path "$env:USERPROFILE\.workbuddy\secrets\github-push-token.txt" -Value 'ghp_你的GitHub_PAT'
#
# 之后每次部署：
#   powershell -ExecutionPolicy Bypass -File scripts\push.ps1
#
# 软件最终版后：
#   Remove-Item "$env:USERPROFILE\.workbuddy\secrets\github-push-token.txt"

$ErrorActionPreference = "Stop"

$TokenFile = Join-Path $env:USERPROFILE ".workbuddy\secrets\github-push-token.txt"

if (-not (Test-Path $TokenFile)) {
    Write-Error "❌ 找不到 token 文件：$TokenFile`n   请先把 GitHub PAT 一行写入该文件，再重跑。详见本脚本顶部注释。"
    exit 1
}

$Token = ((Get-Content $TokenFile -Raw) -replace "`r`n","`n").Trim()
if ([string]::IsNullOrEmpty($Token)) {
    Write-Error "❌ token 文件为空：$TokenFile"
    exit 1
}

# 防御性检查
if ($Token -notmatch '^(ghp_|github_pat_)') {
    Write-Warning "⚠️ token 看起来不像 GitHub PAT（应以 ghp_ 或 github_pat_ 开头），仍尝试推送…"
}

# 关键改写方向：用带 token 的 URL 替换 https://github.com/，绝不能反写
git -c "url.https://${Token}@github.com/.insteadOf=https://github.com/" push origin master
Write-Host "✅ push 完成"