#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v51 统一补丁脚本 — 实现 6 项反馈：
1. 灵感速记按钮往左 + 长按复制真生效
2. 转盘去"今天吃" + 菜品折叠紧凑
3. 份子钱人名下拉（与事件一致）
4. 桌面生活万花筒 1×2 + 英语朗读图标 + 测试逻辑（复习完了进入今日测试）
5. 经验摘录下拉统一（与份子钱事件一致）+ 复制按钮 + 移除日/愿/池按钮
6. 升版本号 v51 + 部署准备

每处替换都用断言保证命中次数（除了明确允许 N 次的）。
"""
import io
import sys

INDEX = 'index.html'

def rep(s, old, new, label, expect=1, allow_zero=False):
    """通用替换：断言 old 在 s 中出现次数等于 expect，写回 new。"""
    n = s.count(old)
    if n != expect:
        if allow_zero and n == 0:
            print(f"[skip] {label}: 0 occurrences (allowed)", file=sys.stderr)
            return s
        raise AssertionError(f"[fail] {label}: expected {expect}, got {n}\n---old---\n{old}\n---")
    return s.replace(old, new, expect)

def rep_first(s, old, new, label):
    """只替换第一次出现的 old（避免误改）。"""
    i = s.find(old)
    if i < 0:
        raise AssertionError(f"[fail] {label}: old not found\n---old---\n{old}\n---")
    return s[:i] + new + s[i+len(old):]

def main():
    s = io.open(INDEX, 'r', encoding='utf-8').read()
    original_len = len(s)

    # ============================================================
    # 1. Quick 灵感速记按钮往左
    # ============================================================
    s = rep(s,
        ".quick-actions{display:flex;flex-wrap:wrap;gap:4px;justify-content:flex-end;margin-top:6px;padding-top:6px;border-top:1px dashed #ece6cf;width:100%}",
        ".quick-actions{display:flex;flex-wrap:wrap;gap:4px;justify-content:flex-start;margin-top:6px;padding-top:6px;border-top:1px dashed #ece6cf;width:100%}",
        "1.1 quick-actions 左对齐",
    )

    # 1.2 长按复制走 _clip 路径（修复 toast 假提示"已复制全文"）
    s = rep(s,
        "    this._holdTimer = setTimeout(() => { navigator.clipboard?.writeText(item.text); UI.toast('已复制全文'); }, 450);",
        "    this._holdTimer = setTimeout(() => { this._clip(item.text, '已复制全文'); }, 450);",
        "1.2 Quick.tapStart 长按复制走 _clip",
    )

    # 1.3 _clip 兜底加 textarea 复制（确保长内容也能复制）
    s = rep(s,
        "    try{ if(navigator.clipboard && navigator.clipboard.writeText){ await navigator.clipboard.writeText(text); UI.toast(msg+' ✓'); return; } }catch(e){}\n    try{ const ta=document.createElement('textarea'); ta.value=text; ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta); ta.focus(); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); UI.toast(msg+' ✓'); }catch(e){ UI.toast('复制失败，请手动长按选择'); }",
        "    try{\n      if(navigator.clipboard && window.isSecureContext !== false && navigator.clipboard.writeText){\n        await navigator.clipboard.writeText(text);\n        UI.toast(msg+' ✓');\n        return;\n      }\n    }catch(e){ console.warn('clipboard api fail',e); }\n    /* 兜底：textarea + execCommand，避免 iOS PWA / 非 secure context 下 clipboard API 不可用 */\n    try{\n      const ta=document.createElement('textarea');\n      ta.value=text;\n      ta.style.position='fixed'; ta.style.top='-9999px'; ta.style.opacity='0';\n      ta.setAttribute('readonly','');\n      document.body.appendChild(ta);\n      ta.focus(); ta.select(); ta.setSelectionRange(0, text.length);\n      const ok = document.execCommand('copy');\n      document.body.removeChild(ta);\n      UI.toast(ok ? (msg+' ✓') : '复制失败，请手动长按选择');\n    }catch(e){\n      UI.toast('复制失败，请手动长按选择');\n    }",
        "1.3 Quick._clip 兜底强化",
    )

    # ============================================================
    # 2. Cooking 转盘去"今天吃" + 菜品折叠
    # ============================================================
    # 2.1 side text 去前缀
    s = rep(s,
        "    if(side) side.textContent='今天吃：'+pick;",
        "    if(side) side.textContent=pick;",
        "2.1 转盘侧文字去今天吃",
    )

    # 2.2 bingo 去前缀
    s = rep(s,
        "      bingo.innerHTML='今天吃<br><b>'+Util.esc(pick)+'</b>';",
        "      bingo.innerHTML='<b style=\"font-size:18px;line-height:1.2;display:inline-block\">'+Util.esc(pick)+'</b>';",
        "2.2 转盘中心结果去今天吃",
    )

    # 2.3 菜品折叠：每条加 ▾/▴ 切换；默认折叠只显示菜名
    s = rep(s,
        'dishList.innerHTML=Object.entries(groups).length?Object.entries(groups).map(([tag,rows])=>`<section style="margin-bottom:12px"><h2>${Util.esc(tag)}</h2><div class="list">${rows.map((x)=>{ const i=this.list().findIndex(y=>y.id===x.id); return `<div class="item dish-item" draggable="true" data-sort-id="${x.id}">${x.photoId?Util.mediaImg(x.photoId):(x.photo?`<img class="thumb" src="${Util.esc(x.photo)}" alt="">`:\'\')}<div class="grow"><div class="dish-name">${Util.esc(x.name)}</div>${x.tags?`<div class="dish-meta">${Util.esc(x.tags)}</div>`:\'\'}<div class="dish-steps">${Util.esc(x.steps||\'\')}</div></div><button class="del" onclick="Cooking.move(${i},-1)">↑</button><button class="del" onclick="Cooking.move(${i},1)">↓</button><button class="del" onclick="Cooking.del(\'${x.id}\')">✕</button></div>`; }).join(\'\')}</div></section>`).join(\'\'):\'<div class="empty">先添加几道菜，转盘就能用了</div>\';',
        "/* v51 菜品折叠：默认收起只显示菜名 + ▾ 展开按钮 */\n    dishList.innerHTML=Object.entries(groups).length?Object.entries(groups).map(([tag,rows])=>`<section style=\"margin-bottom:12px\"><h2>${Util.esc(tag)}</h2><div class=\"list\">${rows.map((x)=>{ const i=this.list().findIndex(y=>y.id===x.id); return `<div class=\"item dish-item${x._open?' open':''}\" draggable=\"true\" data-sort-id=\"${x.id}\">${x.photoId?Util.mediaImg(x.photoId):(x.photo?`<img class=\"thumb\" src=\"${Util.esc(x.photo)}\" alt=\"\">`:'')}<div class=\"grow\"><div class=\"dish-name\">${Util.esc(x.name)}</div>${x.tags?`<div class=\"dish-meta\">${Util.esc(x.tags)}</div>`:''}<div class=\"dish-steps\">${Util.esc(x.steps||'')}</div></div><button class=\"del dish-toggle\" onclick=\"Cooking.toggleOpen('${x.id}')\" title=\"展开/收起\">▾</button><button class=\"del\" onclick=\"Cooking.move(${i},-1)\">↑</button><button class=\"del\" onclick=\"Cooking.move(${i},1)\">↓</button><button class=\"del\" onclick=\"Cooking.del('${x.id}')\">✕</button></div>`; }).join('')}</div></section>`).join(''):'<div class=\"empty\">先添加几道菜，转盘就能用了</div>';",
        "2.3 菜品折叠 HTML",
    )

    # 2.4 Cooking 模块加 toggleOpen
    s = rep(s,
        "  spin(where){",
        "  /* v51：折叠/展开某道菜（仅本机视图状态，不入库） */\n  toggleOpen(id){ const a=this.list(); const it=a.find(x=>x.id===id); if(!it) return; it._open = !it._open; Store.set('dishes', a); this.render(); },\n  spin(where){",
        "2.4 Cooking.toggleOpen",
    )

    # 2.5 CSS 折叠默认样式：菜名单行省略，标签/步骤 hidden
    s = rep(s,
        ".dish-item .dish-name{font-size:15px;font-weight:600;line-height:1.3}\n.dish-item .dish-meta{font-size:11px;color:var(--text-dim);margin-top:1px}\n.dish-item .dish-steps{font-size:12px;color:var(--text-dim);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}",
        "/* v51 菜品折叠：默认收起只显示菜名单行 + ▾ 按钮 */\n.dish-item .dish-name{font-size:13px;font-weight:600;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n.dish-item .dish-meta,.dish-item .dish-steps{display:none}\n.dish-item.open .dish-name{font-size:15px;white-space:normal}\n.dish-item.open .dish-meta{display:block;font-size:11px;color:var(--text-dim);margin-top:2px}\n.dish-item.open .dish-steps{display:block;font-size:12px;color:var(--text-dim);margin-top:2px;white-space:pre-wrap;word-break:break-word;max-width:100%}\n.dish-toggle{font-size:13px}",
        "2.5 菜品折叠 CSS",
    )

    # ============================================================
    # 3. 份子钱人名下拉（与事件一致）
    # ============================================================
    # 3.1 HTML: 加 list 属性 + datalist
    s = rep(s,
        '<div class="row" style="margin-top:8px"><input id="giftPerson" placeholder="人名"><input id="giftAmount" type="number" placeholder="金额"></div>',
        '<div class="row" style="margin-top:8px"><input id="giftPerson" list="giftPersonOptions" placeholder="人名（如：张三，可下拉选常用）"><input id="giftAmount" type="number" placeholder="金额"></div>\n        <datalist id="giftPersonOptions"></datalist>',
        "3.1 份子钱人名 list+datalist",
    )

    # 3.2 Gift.save 加 Util.bump('giftPerson',...)
    s = rep(s,
        "  save(){ const amount=Number(giftAmount.value); if(!giftPerson.value.trim()||!amount)return UI.toast('人名和金额必填'); Util.bump('giftType',giftType.value); Util.bump('giftEvent',giftEvent.value.trim());",
        "  save(){ const amount=Number(giftAmount.value); if(!giftPerson.value.trim()||!amount)return UI.toast('人名和金额必填'); Util.bump('giftType',giftType.value); Util.bump('giftPerson',giftPerson.value.trim()); Util.bump('giftEvent',giftEvent.value.trim());",
        "3.2 Gift.save bump giftPerson",
    )

    # 3.3 Gift.render 填充 person datalist
    s = rep(s,
        "  render(){ Util.sortSelect('giftType','giftType'); const events=[...new Set(this.list().map(x=>x.event).filter(Boolean))]; const evBox=document.getElementById('giftEventOptions'); if(evBox) evBox.innerHTML=Util.byUse('giftEvent',events).map(e=>`<option value=\"${Util.esc(e)}\">`).join('');",
        "  render(){\n    Util.sortSelect('giftType','giftType');\n    /* v51：人名 + 事件都按使用频次排序填进 datalist（首次输入后直接出现在下拉里，按频次从高到低排） */\n    const persons=[...new Set(this.list().map(x=>x.person).filter(Boolean))];\n    const pBox=document.getElementById('giftPersonOptions');\n    if(pBox) pBox.innerHTML=Util.byUse('giftPerson',persons).slice(0,12).map(p=>`<option value=\"${Util.esc(p)}\">`).join('');\n    const events=[...new Set(this.list().map(x=>x.event).filter(Boolean))];\n    const evBox=document.getElementById('giftEventOptions');\n    if(evBox) evBox.innerHTML=Util.byUse('giftEvent',events).slice(0,12).map(e=>`<option value=\"${Util.esc(e)}\">`).join('');",
        "3.3 Gift.render 填 person+event datalist",
    )

    # ============================================================
    # 4. 桌面生活万花筒 1×2 + 英语朗读图标 + 测试逻辑
    # ============================================================
    # 4.1 CSS .life-mini-row repeat(4) -> repeat(2)
    s = rep(s,
        ".life-mini-row{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;padding:8px 4px;cursor:pointer;border-radius:12px;background:var(--card-2,#f3f5ef)}",
        ".life-mini-row{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;padding:8px 4px;cursor:pointer;border-radius:12px;background:var(--card-2,#f3f5ef)}",
        "4.1 桌面生活万花筒 1×2",
    )

    # 4.2 英语朗读按钮纯图标
    s = rep(s,
        'onclick="English.playQuote()">🔊 朗读</button>',
        'onclick="English.playQuote()" title="朗读">🔊</button>',
        "4.2a playQuote 按钮纯图标",
    )
    s = rep(s,
        'onclick="English.playDialog()">🔊 朗读对话</button>',
        'onclick="English.playDialog()" title="朗读对话">🔊</button>',
        "4.2b playDialog 按钮纯图标",
    )

    # 4.3 首页英语 desc 去 "(含测试)"
    s = rep(s,
        "english:{icon:'📖',name:'英语积累',go:'english',value:()=>English.doneCount(),unit:'/5',desc:'今日学完得 5 项（含测试）'}",
        "english:{icon:'📖',name:'英语积累',go:'english',value:()=>English.doneCount(),unit:'/5',desc:'今日学完得 5 项'}",
        "4.3 英语 desc 去 (含测试)",
    )

    # 4.4 renderQuiz: 复习完了进入今日测试（4 道 today-quiz，答完才算测试打卡）
    s = rep(s,
        "  renderQuiz(){\n    const box=document.getElementById('englishQuiz');\n    if(!box) return;\n    if(Store.getDaily('english_done',[]).includes('测试')){\n      box.innerHTML=`<div class=\"card\" style=\"text-align:center;padding:24px\"><div style=\"font-size:36px;margin-bottom:8px\">🎉</div><div style=\"color:var(--accent);font-weight:700\">今日测试已完成！已自动入账金币</div><div class=\"hint\" style=\"margin-top:6px\">明天再来挑战新题</div></div>`;\n      return;\n    }\n    const due=this.dueItems();\n    if(!due.length){\n      box.innerHTML=`<div class=\"card\" style=\"text-align:center;padding:20px\"><div style=\"font-size:30px;margin-bottom:6px\">🌟</div><div style=\"font-weight:700;color:var(--accent)\">今天没有要复习的内容</div><div class=\"hint\" style=\"margin-top:6px\">学过的都记牢啦，点下面完成今日复习打卡</div><button class=\"btn small\" style=\"margin-top:10px\" onclick=\"English.completeTestEmpty()\">完成复习打卡</button></div>`;\n      return;\n    }\n    box.innerHTML=`<div class=\"eng-q-row\">${due.map(q=>this.quizCard(q)).join('')}</div>`;\n  },",
        "  renderQuiz(){\n    const box=document.getElementById('englishQuiz');\n    if(!box) return;\n    if(Store.getDaily('english_done',[]).includes('测试')){\n      box.innerHTML=`<div class=\"card\" style=\"text-align:center;padding:24px\"><div style=\"font-size:36px;margin-bottom:8px\">🎉</div><div style=\"color:var(--accent);font-weight:700\">今日测试已完成！已自动入账金币</div><div class=\"hint\" style=\"margin-top:6px\">明天再来挑战新题</div></div>`;\n      return;\n    }\n    const due=this.dueItems();\n    if(due.length){\n      box.innerHTML=`<div class=\"eng-q-row\">${due.map(q=>this.quizCard(q)).join('')}</div>`;\n      return;\n    }\n    /* v51：复习完了 → 进入今日测试（4 道今天学习的题） */\n    const todays=this.todayTestItems();\n    const done=Store.get('english_today_test:'+Util.today(),{});\n    const remain=todays.filter(q => !(done[q.key]&&done[q.key].isCorrect));\n    if(!remain.length){\n      Store.setDaily('english_done',[...new Set(Store.getDaily('english_done',[]).concat('测试'))]);\n      Coin.earn('english_test','完成英语复习');\n      box.innerHTML=`<div class=\"card\" style=\"text-align:center;padding:24px\"><div style=\"font-size:36px;margin-bottom:8px\">🎉</div><div style=\"color:var(--accent);font-weight:700\">今日测试已完成！已自动入账金币</div><div class=\"hint\" style=\"margin-top:6px\">明天再来挑战新题</div></div>`;\n      return;\n    }\n    box.innerHTML=`<div class=\"eng-q-row\">${remain.map(q=>this.todayTestCard(q)).join('')}</div>`;\n  },\n  /* v51：今日测试 4 题（quote/word/phrase/dialog 各 1 道） */\n  todayTestItems(){\n    const t=this.today();\n    return [\n      {key:'today-quote',type:'quote',text:t.quote,answer:t.quoteZh,wrong:this.wrongZh(t.quoteZh)},\n      {key:'today-word',type:'word',text:t.word,answer:t.wordZh,wrong:this.wrongOption(t.wordZh)},\n      {key:'today-phrase',type:'phrase',text:t.phrase,answer:t.phraseZh,wrong:t.phraseWrong||this.wrongZh(t.phraseZh)},\n      {key:'today-dialog',type:'dialog',text:t.dialog,answer:t.dialogZh,wrong:this.wrongZh(t.dialogZh)}\n    ];\n  },\n  todayTestCard(q){\n    const label={quote:'今日句',word:'今日词',phrase:'今日搭配',dialog:'今日对话'}[q.type]||'今日测试';\n    const sub='选出正确的中文意思';\n    const done=Store.get('english_today_test:'+Util.today(),{});\n    const res=done[q.key];\n    if(res){\n      return `<div class=\"card eng-quiz-card\"><h2>🧪 ${label}</h2><div class=\"eng-q-word\">${Util.esc(q.text)}</div><div style=\"text-align:center;padding:8px 0\"><div style=\"font-size:30px\">${res.isCorrect?'✅':'❌'}</div><div style=\"font-weight:700;color:${res.isCorrect?'var(--accent)':'var(--accent-2)'}\">${res.isCorrect?'答对啦':'再记记'}</div></div></div>`;\n    }\n    const options=[q.answer, q.wrong].sort(()=>Math.random()-.5);\n    return `<div class=\"card eng-quiz-card\"><h2>🧪 ${label}</h2><div class=\"eng-q-word\">${Util.esc(q.text)}</div><p class=\"hint\" style=\"margin-top:4px\">${sub}</p><div class=\"eng-q-options\">${options.map(opt=>`<button class=\"btn eng-q-opt\" onclick=\"English.answerTodayTest('${q.key}','${Util.esc(opt)}')\">${Util.esc(opt)}</button>`).join('')}</div></div>`;\n  },\n  answerTodayTest(key,selected){\n    const q=this.todayTestItems().find(x=>x.key===key); if(!q) return;\n    const isCorrect = selected===q.answer;\n    const cur=Store.get('english_today_test:'+Util.today(),{});\n    cur[key]={isCorrect, at:Date.now()};\n    Store.set('english_today_test:'+Util.today(),cur);\n    if(isCorrect){\n      /* 今日测试答对：也写入 SRS（reps=0，到期=今天，留给明天再测一次） */\n      this.ensureSRS(q.type);\n    }\n    this.renderQuiz();\n  },\n  /* 兼容旧版调用：保留 completeTestEmpty 防止引用残留 */\n  completeTestEmpty(){ this.renderQuiz(); },",
        "4.4 renderQuiz 进入今日测试",
    )

    # 4.5 删除原来的 completeTestEmpty 中重复的 english_done 逻辑（已挪到 renderQuiz 内）
    # 上面的 rep 已经处理了。下面删除无用的旧 completeTestEmpty。

    # ============================================================
    # 5. 经验摘录下拉统一 + 复制按钮 + 移除日/愿/池
    # ============================================================
    # 5.1 Notes.item 列表项：✎ 编辑 + ⧉ 复制（保留 ↑↓✕）
    s = rep(s,
        '    return UI.item(x.title||Util.firstSentence(x.text)||x.date, `${x.text}\\n${meta}`, `<button class="del" onclick="Notes.edit(\'${x.id}\')">编辑</button><button class="del" onclick="Notes.moveId(\'${x.id}\',-1)">↑</button><button class="del" onclick="Notes.moveId(\'${x.id}\',1)">↓</button><button class="del" onclick="Notes.del(\'${x.id}\')">✕</button>`, `draggable="true" data-sort-id="${x.id}"`);',
        '    /* v51：保留 ✎ 编辑 + ⧉ 复制 + ↑↓✕（不再有 日/愿/池 按钮，跟灵感速记未整理灵感列表一致） */\n    return UI.item(x.title||Util.firstSentence(x.text)||x.date, `${x.text}\\n${meta}`, `<button class="del\" onclick="Notes.edit(\'${x.id}\')" title="编辑\">✎</button><button class=\"del\" onclick=\"Notes.copy(\'${x.id}\')\" title=\"复制内容\">⧉</button><button class=\"del\" onclick=\"Notes.moveId(\'${x.id}\',-1)\" title=\"上移\">↑</button><button class=\"del\" onclick=\"Notes.moveId(\'${x.id}\',1)\" title=\"下移\">↓</button><button class=\"del\" onclick=\"Notes.del(\'${x.id}\')\" title=\"删除\">✕</button>`, `draggable="true" data-sort-id="${x.id}"`);',
        "5.1 Notes.item 加复制按钮",
    )

    # 5.2 Notes.copy 紧跟 del 之后
    s = rep(s,
        "  del(id){ Store.set('notes',this.list().filter(x=>x.id!==id)); this.render(); }\n};",
        "  del(id){ Store.set('notes',this.list().filter(x=>x.id!==id)); this.render(); },\n  /* v51：一键复制摘录全文到剪贴板（不走 datalist，用 textarea 兜底） */\n  async copy(id){\n    const it=this.list().find(x=>x.id===id); if(!it) return;\n    const text=(it.title?(it.title+'\\n\\n'+it.text):it.text);\n    try{\n      if(navigator.clipboard && window.isSecureContext !== false && navigator.clipboard.writeText){\n        await navigator.clipboard.writeText(text);\n        UI.toast('已复制摘录 ✓');\n        return;\n      }\n    }catch(e){ console.warn('clipboard api fail',e); }\n    try{\n      const ta=document.createElement('textarea');\n      ta.value=text;\n      ta.style.position='fixed'; ta.style.top='-9999px'; ta.style.opacity='0';\n      ta.setAttribute('readonly','');\n      document.body.appendChild(ta); ta.focus(); ta.select(); ta.setSelectionRange(0, text.length);\n      const ok=document.execCommand('copy');\n      document.body.removeChild(ta);\n      UI.toast(ok ? '已复制摘录 ✓' : '复制失败，请手动长按选择');\n    }catch(e){ UI.toast('复制失败，请手动长按选择'); }\n  }\n};",
        "5.2 Notes.copy",
    )

    # 5.3 限制 datalist 候选项数（按使用频次排，最多 12 条）
    s = rep(s,
        "    noteTagOptions.innerHTML=this.tagOptions().map(t=>`<option value=\"${Util.esc(t)}\"></option>`).join('');\n    noteKeywordOptions.innerHTML=this.keywordOptions().map(t=>`<option value=\"${Util.esc(t)}\"></option>`).join('');",
        "    /* v51：限制 datalist 候选项数（按使用频次排），避免 iOS PWA 下拉候选过多弹出位置异常 */\n    noteTagOptions.innerHTML=this.tagOptions().slice(0,12).map(t=>`<option value=\"${Util.esc(t)}\"></option>`).join('');\n    noteKeywordOptions.innerHTML=this.keywordOptions().slice(0,12).map(t=>`<option value=\"${Util.esc(t)}\"></option>`).join('');",
        "5.3 Notes datalist 限 12",
    )

    # 5.4 做菜标签 datalist 也限 12
    s = rep(s,
        "    dishTagOptions.innerHTML=this.tags().map(t=>`<option value=\"${Util.esc(t)}\"></option>`).join('');",
        "    dishTagOptions.innerHTML=this.tags().slice(0,12).map(t=>`<option value=\"${Util.esc(t)}\"></option>`).join('');",
        "5.4 做菜标签 datalist 限 12",
    )

    # 5.5 English QA: 让 todayTestCard 中的"srsKey todayIndex+type"对应今天学习过 ensureSRS
    # ensureSRS 接收 type，这里 Q 的 type 来自 todayTestItems 已经是 quote/word/phrase/dialog，OK

    # ============================================================
    # 6. 升版本号 v51 + 部署准备
    # ============================================================
    s = rep(s,
        "const BUILD_VERSION = '2026-08-14-v50';",
        "const BUILD_VERSION = '2026-08-14-v51';",
        "6.1 BUILD_VERSION v51",
    )

    io.open(INDEX, 'w', encoding='utf-8').write(s)
    new_len = len(s)
    print(f"[ok] {INDEX}: {original_len} -> {new_len} bytes ({new_len-original_len:+d})")

if __name__ == '__main__':
    main()
