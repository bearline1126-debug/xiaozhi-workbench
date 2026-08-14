#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v49 全量补丁：一次性应用用户在「小彘的工作台」上提出的 10 项反馈。
所有 old/new 均按当前 index.html 实际内容精确匹配（raw 字符串保留反斜杠）。
任一替换次数 != 1 立即报错退出，绝不静默写坏文件。
"""
import io
import sys

INDEX = 'index.html'
SW = 'sw.js'

with io.open(INDEX, 'r', encoding='utf-8') as f:
    s = f.read()
with io.open(SW, 'r', encoding='utf-8') as f:
    sw = f.read()

fails = []
def rep(old, new, label=''):
    global s
    n = s.count(old)
    if n != 1:
        fails.append('[%s] 期望 1 次，实际 %d 次' % (label, n))
        print('!! 失败 [%s] 期望 1 次，实际 %d 次' % (label, n))
        return
    s = s.replace(old, new, 1)
    print('OK  [%s]' % label)

# ============================================================
# 1. 升级 BUILD_VERSION
rep(
r"""const BUILD_VERSION = '2026-08-13-v48';""",
r"""const BUILD_VERSION = '2026-08-14-v49';""",
'BUILD_VERSION')

# ============================================================
# 2. Migrate.ensureSeeds：只种一次，绝不复活已删默认习惯（修 #8）
rep(
r"""  ensureSeeds(){
    const items = Store.get('tracker_items');
    if(!items) return;
    let changed = false;
    Tracker.defaults().forEach(s => { if(!items.some(x => x.id === s.id)){ items.push(s); changed = true; } });
    if(changed) Store.set('tracker_items', items);
  },""",
r"""  /* 关键修复(v49)：习惯只「种一次」。之前每次启动都跑 ensureSeeds，把用户删掉的默认习惯
     重新塞回 tracker_items，导致「删不干净」。现在用 _trackerSeeded 标志：首次把默认 7 条补齐，
     之后绝不再动这张表（用户删了就删了）。 */
  ensureSeeds(){
    if(Store.get('_trackerSeeded')) return;
    let items = Store.get('tracker_items');
    if(!items) items = [];
    const defaults = Tracker.defaults();
    const next = items.slice();
    defaults.forEach(def => { if(!next.some(x => x.id === def.id)) next.push(def); });
    if(next.length !== items.length) Store.set('tracker_items', next);
    Store.set('_trackerSeeded', 1);
  },""",
'Migrate.ensureSeeds')

# ============================================================
# 3. DragSort：长按/拖动后变灰(.dragging)必须能恢复（修 #7）
rep(
r"""      source.addEventListener('touchend', e => {
        clearTimeout(timer);
        if(cancelled){ cancelled = false; return; }
        if(!dragging){
          /* 只是长按浮出（或长按后没拖动）：保留 editing，按钮可点；背景点击会清除 */
          release();
          return;
        }
        dragging = false; el.classList.remove('dragging'); DragSort.clearHints(); release();
        const t = e.changedTouches[0];
        const target = DragSort.pointTarget(t, selector, attrName, el);
        if(target && target !== el){
          const from = idOf(el), to = idOf(target);
          if(from && to && from !== to) onMove(from, to, target, el);
        }
        /* 不移除 editing：拖动后也可立即点按钮；背景点击会清除 */
      });
      source.addEventListener('touchcancel', () => { clearTimeout(timer); if(dragging){ dragging = false; el.classList.remove('dragging'); DragSort.clearHints(); } cancelled = false; release(); });""",
r"""      /* 全局兜底(v49)：任何一次触摸/指针结束或取消后，清掉可能残留的 .dragging(变灰) 与 .drop-hint，
         彻底解决「长按/拖动后变灰不恢复」 */
      if(!DragSort._globalCleanBound){
        DragSort._globalCleanBound = true;
        const sweep = () => { document.querySelectorAll('.dragging').forEach(n => n.classList.remove('dragging')); DragSort.clearHints(); };
        document.addEventListener('touchend', sweep);
        document.addEventListener('touchcancel', sweep);
        document.addEventListener('pointerup', sweep);
        document.addEventListener('mouseup', sweep);
      }
      source.addEventListener('touchend', e => {
        clearTimeout(timer);
        if(cancelled){ cancelled = false; release(); return; }
        if(!dragging){
          el.classList.remove('dragging');
          release();
          return;
        }
        dragging = false; el.classList.remove('dragging'); DragSort.clearHints(); release();
        const t = e.changedTouches[0];
        const target = DragSort.pointTarget(t, selector, attrName, el);
        if(target && target !== el){
          const from = idOf(el), to = idOf(target);
          if(from && to && from !== to) onMove(from, to, target, el);
        }
      });
      source.addEventListener('touchcancel', () => { clearTimeout(timer); if(dragging){ dragging = false; } el.classList.remove('dragging'); DragSort.clearHints(); cancelled = false; release(); });""",
'DragSort.touchend/cancel')

# ============================================================
# 4. 视觉灵感「全部图片」补封面（用最新图，修 #1）
rep(
r"""    /* 「全部图片」入口：跨分类查看所有收藏 */
    const allCount = list.length;
    const allCard = `<div class="visual-cat visual-cat-all" onclick="Visual.openAlbum('__all__')">
        <div class="vc-head"><span class="vc-title">🖼 全部图片</span><span class="vc-count">${allCount}</span></div>
        <div class="vc-thumb"><div style="font-size:30px;color:#9bb07f">▦</div></div>
        <div class="vc-foot">看所有分类的收藏</div>
      </div>`;""",
r"""    /* 「全部图片」入口：用最新保存的那张图作封面（v49 修：之前只有占位符 ▦） */
    const allCount = list.length;
    const allLatest = list[0];
    const allMedia = allLatest ? (Array.isArray(allLatest.media) ? allLatest.media[0] : (allLatest.mediaId ? {id:allLatest.mediaId} : null)) : null;
    const allThumb = allMedia ? `<img class="thumb" data-media="${allMedia.id}" alt="">` : '<div style="font-size:30px;color:#9bb07f">▦</div>';
    const allFoot = allLatest ? ('共 ' + allCount + ' 条 · 最近：' + Util.esc(allLatest.tag || '收藏') + ' ' + allLatest.date) : '看所有分类的收藏';
    const allCard = `<div class="visual-cat visual-cat-all" onclick="Visual.openAlbum('__all__')">
        <div class="vc-head"><span class="vc-title">🖼 全部图片</span><span class="vc-count">${allCount}</span></div>
        <div class="vc-thumb">${allThumb}</div>
        <div class="vc-foot">${allFoot}</div>
      </div>`;""",
'Visual.allCard')

# ============================================================
# 5. 关闭 Chrome 保存密码弹窗：3 个 password 输入改 text + webkit-text-security 掩码（修 #2）
rep(
r"""    <input type="password" id="unlockPassword" placeholder="输入密码">""",
r"""    <input type="text" id="unlockPassword" placeholder="输入密码" autocomplete="off" data-lpignore="true" data-1p-ignore="true" data-form-type="other" style="-webkit-text-security:disc;text-security:disc">""",
'pw.unlockPassword')
rep(
r"""        <input type="password" id="key_ai" placeholder="API key">""",
r"""        <input type="text" id="key_ai" placeholder="API key" autocomplete="off" data-lpignore="true" data-1p-ignore="true" data-form-type="other" style="-webkit-text-security:disc;text-security:disc;font-family:monospace">""",
'pw.key_ai')
rep(
r"""        <input type="password" id="newPassword" placeholder="设置本地密码">""",
r"""        <input type="text" id="newPassword" placeholder="设置本地密码" autocomplete="new-password" data-lpignore="true" data-1p-ignore="true" data-form-type="other" style="-webkit-text-security:disc;text-security:disc">""",
'pw.newPassword')

# ============================================================
# 6. 首页英语卡片计数 /5（修 #3 计数）
rep(
r"""      english:{icon:'📖',name:'英语积累',go:'english',value:()=>English.doneCount(),unit:'/4',desc:'今天的学习进度'},""",
r"""      english:{icon:'📖',name:'英语积累',go:'english',value:()=>English.doneCount(),unit:'/5',desc:'今日学完得 5 项（含测试）'},""",
'Home.tileInfo.english')
rep(
r"""    if(eng.length<4) out.push({t:`英语今天完成 ${eng.length}/4`,d:'每日一句、单词、搭配、对话',tag:'英语',cls:'',go:'english'});""",
r"""    if(eng.length<5) out.push({t:`英语今天完成 ${eng.length}/5`,d:'每日一句、单词、搭配、对话、测试',tag:'英语',cls:'',go:'english'});""",
'Home.todoItems.english')

# ============================================================
# 7. 生活万花筒首页缩小成单行 4 项 + 点进（修 #4）
rep(
r"""  compact(){
    const d=this.data(31);
    return `<div class="grid">
      <div class="tile"><h3>今日必做</h3><div class="big">${d.taskDone}<small>/${d.taskTotal}</small></div></div>
      <div class="tile"><h3>英语学习</h3><div class="big">${d.englishDays}<small>天</small></div></div>
      <div class="tile"><h3>🪙 金币</h3><div class="big" style="color:#d4a017">${d.coinTotal}<small>枚</small></div></div>
      <div class="tile"><h3>会做几道菜</h3><div class="big">${d.dishes}<small>道</small></div></div>
    </div>`;""",
r"""  /* 桌面「生活万花筒」小卡：4 个数字一行显示，点一下直接进生活万花筒页（v49 修） */
  compact(){
    const d=this.data(31);
    return `<div class="life-mini-row" onclick="App.go('lifeAnalysis')" title="点开看完整生活万花筒">
      <div class="life-mini-cell"><div class="lm-num">${d.taskDone}<small>/${d.taskTotal}</small></div><div class="lm-cap">今日必做</div></div>
      <div class="life-mini-cell"><div class="lm-num">${d.englishDays}<small>天</small></div><div class="lm-cap">英语</div></div>
      <div class="life-mini-cell"><div class="lm-num" style="color:#d4a017">${d.coinTotal}<small>枚</small></div><div class="lm-cap">🪙 金币</div></div>
      <div class="life-mini-cell"><div class="lm-num">${d.dishes}<small>道</small></div><div class="lm-cap">会做的菜</div></div>
    </div>`;""",
'LifeAnalysis.compact')
rep(
r"""    if(id==='life') return `<div id="homeLifeSummary"></div><button class="btn ghost" style="margin-top:10px;width:100%" onclick="App.go('lifeAnalysis')">查看完整分析</button>`;""",
r"""    if(id==='life') return `<div id="homeLifeSummary"></div>`;""",
'Home.widgetBody.life')

# ============================================================
# 8. 灵感速记：左下角加 ✎ 编辑 / ⧉ 复制 按钮（修 #6）
rep(
r"""        <div class="quick-actions">
          <button class="quick-act" onclick="Quick.toTask('${x.id}')" title="加到明天必做">＋ 日</button>
          <button class="quick-act" onclick="Quick.toWish('${x.id}')" title="成为心愿/挂行动">↗ 愿</button>
          <button class="quick-act" onclick="Quick.toPool('${x.id}')" title="放入灵感池">📥 池</button>
          <button class="del" onclick="Quick.del('${x.id}')" title="删除">✕</button>
        </div>""",
r"""        <div class="quick-actions">
          <button class="quick-act" onclick="Quick.editStart('${x.id}')" title="编辑这条灵感">✎</button>
          <button class="quick-act" onclick="Quick.copy('${x.id}')" title="复制这条灵感">⧉</button>
          <button class="quick-act" onclick="Quick.toTask('${x.id}')" title="加到明天必做">＋ 日</button>
          <button class="quick-act" onclick="Quick.toWish('${x.id}')" title="成为心愿/挂行动">↗ 愿</button>
          <button class="quick-act" onclick="Quick.toPool('${x.id}')" title="放入灵感池">📥 池</button>
          <button class="del" onclick="Quick.del('${x.id}')" title="删除">✕</button>
        </div>""",
'Quick.render.actions')
rep(
r"""        <div class="quick-actions">
          <button class="quick-act" onclick="Quick.toUnPool('${x.id}')" title="恢复到未整理灵感" style="color:#779679">↺ 还原</button>
          <button class="del" onclick="Quick.delPool('${x.id}')" title="删除">✕</button>
        </div>""",
r"""        <div class="quick-actions">
          <button class="quick-act" onclick="Quick.editPoolStart('${x.id}')" title="编辑">✎</button>
          <button class="quick-act" onclick="Quick.copyPool('${x.id}')" title="复制">⧉</button>
          <button class="quick-act" onclick="Quick.toUnPool('${x.id}')" title="恢复到未整理灵感" style="color:#779679">↺ 还原</button>
          <button class="del" onclick="Quick.delPool('${x.id}')" title="删除">✕</button>
        </div>""",
'Quick.render.poolActions')
rep(
r"""  render(){
    /* 未整理灵感：上方满行文本，下方一行放池/愿/日/✕ 按钮 */""",
r"""  /* 一键复制灵感内容到剪贴板（v49：左下角 ⧉ 按钮，替代时灵时不灵的长按复制） */
  async copy(id){ const it=this.list().find(x=>x.id===id); if(!it) return; await this._clip(it.text,'已复制灵感'); },
  async copyPool(id){ const it=this.poolList().find(x=>x.id===id); if(!it) return; await this._clip(it.text,'已复制灵感'); },
  async _clip(text,msg){
    try{ if(navigator.clipboard && navigator.clipboard.writeText){ await navigator.clipboard.writeText(text); UI.toast(msg+' ✓'); return; } }catch(e){}
    try{ const ta=document.createElement('textarea'); ta.value=text; ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta); ta.focus(); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); UI.toast(msg+' ✓'); }catch(e){ UI.toast('复制失败，请手动长按选择'); }
  },
  render(){
    /* 未整理灵感：上方满行文本，下方一行放池/愿/日/✕ 按钮 */""",
'Quick.copy.methods')

# ============================================================
# 9. 经验摘录保存后 +1 金币（修 #10）
rep(
r"""    } else {
      Store.set('notes',[{id:Util.uid(),date:Util.today(),title,text,tags,keywords},...this.list()]);
      UI.toast('摘录已保存');
    }
    noteTitle.value=noteText.value=noteTags.value=noteKeywords.value='';
    this.render();
  },""",
r"""    } else {
      Store.set('notes',[{id:Util.uid(),date:Util.today(),title,text,tags,keywords},...this.list()]);
      UI.toast('摘录已保存');
    }
    /* v49：写经验摘录 +1 金币（Coin.earn 内部已限制每天最多 1 次） */
    Coin.earn('notes','写经验摘录');
    noteTitle.value=noteText.value=noteTags.value=noteKeywords.value='';
    this.render();
  },""",
'Notes.add.coin')

# ============================================================
# 10. Coin.sources 增加 notes（修 #10）
rep(
r"""    english_test:{name:'完成英语测试',icon:'🧪',desc:'完成了今天的单词+搭配测试'},""",
r"""    english_test:{name:'完成英语测试',icon:'🧪',desc:'完成了今天的单词+搭配测试'},
    notes:{name:'写经验摘录',icon:'📒',desc:'在经验摘录里写了一篇笔记'},""",
'Coin.sources.notes')

# ============================================================
# 11. 份子钱：编辑 / 再记一笔 / 事件下拉（修 #9）
rep(
r"""        <div class="row" style="margin-top:8px"><input id="giftEvent" placeholder="事件，如：婚礼/生日/乔迁"><input id="giftDate" type="date"></div>
        <textarea id="giftNote" placeholder="备注"></textarea>
        <button class="btn" style="margin-top:10px;width:100%" onclick="Gift.add()">保存记录</button>""",
r"""        <div class="row" style="margin-top:8px"><input id="giftEvent" list="giftEventOptions" placeholder="事件，如：婚礼/生日/乔迁（可下拉选常用）"><input id="giftDate" type="date"></div>
        <datalist id="giftEventOptions"></datalist>
        <textarea id="giftNote" placeholder="备注"></textarea>
        <button class="btn" id="giftSaveBtn" style="margin-top:10px;width:100%" onclick="Gift.save()">保存记录</button>
        <button class="btn ghost" id="giftCancelEdit" style="margin-top:8px;width:100%;display:none" onclick="Gift.cancelEdit()">取消编辑</button>""",
'Gift.html')
rep(
r"""const Gift = {
  list(){ return Store.get('gifts',[]); },
  add(){ const amount=Number(giftAmount.value); if(!giftPerson.value.trim()||!amount)return UI.toast('人名和金额必填'); Util.bump('giftType',giftType.value); Store.set('gifts',[{id:Util.uid(),type:giftType.value,person:giftPerson.value.trim(),amount,event:giftEvent.value.trim(),date:giftDate.value||Util.today(),note:giftNote.value.trim()},...this.list()]); giftPerson.value=giftAmount.value=giftEvent.value=giftNote.value=''; giftDate.value=''; this.render(); },
  render(){ Util.sortSelect('giftType','giftType'); const list=this.list(); const sumIn=list.filter(x=>x.type==='in').reduce((s,x)=>s+x.amount,0); const sumOut=list.filter(x=>x.type==='out').reduce((s,x)=>s+x.amount,0); giftIn.textContent='¥'+sumIn; giftOut.textContent='¥'+sumOut; giftNet.textContent='¥'+(sumIn-sumOut); giftCount.textContent=list.length; const q=(giftSearch.value||'').trim(); const rows=q?list.filter(x=>(x.person+x.event+x.note).includes(q)):list; giftList.innerHTML=rows.length?rows.map(x=>UI.item(`${x.type==='in'?'收到':'付出'} · ${x.person} · ¥${x.amount}`,`${x.date} · ${x.event||'未写事件'}\n${x.note||''}`,`<button class="del" onclick="Gift.del('${x.id}')">✕</button>`,`draggable="true" data-sort-id="${x.id}"`)).join(''):'<div class="empty">暂无记录</div>'; DragSort.bind('#giftList [data-sort-id]','gifts',()=>Gift.render()); },
  del(id){ Store.set('gifts',this.list().filter(x=>x.id!==id)); this.render(); }
};""",
r"""const Gift = {
  list(){ return Store.get('gifts',[]); },
  _editing:null,
  save(){ const amount=Number(giftAmount.value); if(!giftPerson.value.trim()||!amount)return UI.toast('人名和金额必填'); Util.bump('giftType',giftType.value); Util.bump('giftEvent',giftEvent.value.trim()); const rec={id:this._editing||Util.uid(),type:giftType.value,person:giftPerson.value.trim(),amount,event:giftEvent.value.trim(),date:giftDate.value||Util.today(),note:giftNote.value.trim()}; const next=this._editing?this.list().map(x=>x.id===this._editing?rec:x):[rec,...this.list()]; Store.set('gifts',next); this._editing=null; giftPerson.value=giftAmount.value=giftEvent.value=giftNote.value=''; giftDate.value=''; this.render(); UI.toast('已保存'); },
  /* 编辑：把这条记录填回表单 */
  edit(id){ const x=this.list().find(n=>n.id===id); if(!x)return; this._editing=id; giftType.value=x.type; giftPerson.value=x.person||''; giftAmount.value=x.amount||''; giftEvent.value=x.event||''; giftDate.value=x.date||''; giftNote.value=x.note||''; this.render(); giftPerson.scrollIntoView({behavior:'smooth',block:'center'}); UI.toast('正在编辑，改完点「保存记录」'); },
  /* 再记一笔：复制这条账单到表单（新 id），用户改细节即可直接存为新记录 */
  duplicate(id){ const x=this.list().find(n=>n.id===id); if(!x)return; this._editing=null; giftType.value=x.type; giftPerson.value=x.person||''; giftAmount.value=x.amount||''; giftEvent.value=x.event||''; giftDate.value=Util.today(); giftNote.value=x.note||''; this.render(); giftPerson.focus(); UI.toast('已复制账单，改一下细节就能再记一笔'); },
  cancelEdit(){ this._editing=null; giftPerson.value=giftAmount.value=giftEvent.value=giftNote.value=''; giftDate.value=''; this.render(); },
  render(){ Util.sortSelect('giftType','giftType'); const events=[...new Set(this.list().map(x=>x.event).filter(Boolean))]; const evBox=document.getElementById('giftEventOptions'); if(evBox) evBox.innerHTML=Util.byUse('giftEvent',events).map(e=>`<option value="${Util.esc(e)}">`).join(''); const list=this.list(); const sumIn=list.filter(x=>x.type==='in').reduce((s,x)=>s+x.amount,0); const sumOut=list.filter(x=>x.type==='out').reduce((s,x)=>s+x.amount,0); giftIn.textContent='¥'+sumIn; giftOut.textContent='¥'+sumOut; giftNet.textContent='¥'+(sumIn-sumOut); giftCount.textContent=list.length; const cancel=document.getElementById('giftCancelEdit'); if(cancel) cancel.style.display=this._editing?'block':'none'; const saveBtn=document.getElementById('giftSaveBtn'); if(saveBtn) saveBtn.textContent=this._editing?'更新记录':'保存记录'; const q=(giftSearch.value||'').trim(); const rows=q?list.filter(x=>(x.person+x.event+x.note).includes(q)):list; giftList.innerHTML=rows.length?rows.map(x=>UI.item(`${x.type==='in'?'收到':'付出'} · ${x.person} · ¥${x.amount}`,`${x.date} · ${x.event||'未写事件'}\n${x.note||''}`,`<button class="del" onclick="Gift.edit('${x.id}')">✎</button><button class="del" onclick="Gift.duplicate('${x.id}')" title="再记一笔">↻</button><button class="del" onclick="Gift.del('${x.id}')">✕</button>`,`draggable="true" data-sort-id="${x.id}"`)).join(''):'<div class="empty">暂无记录</div>'; DragSort.bind('#giftList [data-sort-id]','gifts',()=>Gift.render()); },
  del(id){ Store.set('gifts',this.list().filter(x=>x.id!==id)); this.render(); }
};""",
'Gift.module')

# ============================================================
# 12. 转盘：指针不随盘转 + 中心 bingo 结果 + 菜品紧凑（修 #5）
rep(
r""".wheel-wrap{display:grid;grid-template-columns:118px 1fr;gap:12px;align-items:center}""",
r""".wheel-wrap{display:grid;grid-template-columns:124px 1fr;gap:12px;align-items:center}""",
'CSS.wheel-wrap')
rep(
r""".wheel:before{content:"";position:absolute;top:-16px;left:42px;border-left:10px solid transparent;border-right:10px solid transparent;border-top:18px solid var(--accent-2);z-index:2}""",
r""".wheel-box{position:relative;width:122px;height:122px}
.wheel-pointer{position:absolute;top:-6px;left:50%;transform:translateX(-50%);width:0;height:0;border-left:9px solid transparent;border-right:9px solid transparent;border-top:16px solid var(--accent-2);z-index:3;filter:drop-shadow(0 1px 1px rgba(0,0,0,.25))}""",
'CSS.wheel-pointer')
rep(
r""".wheel-mini-disk::after{content:'';position:absolute;top:-4px;left:50%;transform:translateX(-50%);width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-top:9px solid #b00020}""",
r""".wheel-mini-box{position:relative;width:96px;height:96px}
.wheel-mini-pointer{position:absolute;top:-4px;left:50%;transform:translateX(-50%);width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-top:9px solid #b00020;z-index:3}""",
'CSS.wheel-mini-pointer')
rep(
r""".ai-box{white-space:pre-wrap;line-height:1.62;font-size:14px;color:var(--text)}
.empty{text-align:center;color:var(--text-dim);font-size:13px;padding:18px 0;line-height:1.5}""",
r""".ai-box{white-space:pre-wrap;line-height:1.62;font-size:14px;color:var(--text)}
.empty{text-align:center;color:var(--text-dim);font-size:13px;padding:18px 0;line-height:1.5}
/* v49：转盘结果 bingo 效果 + 生活万花筒单行 + 菜品紧凑 */
.wheel-result-bingo{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%) scale(.2);opacity:0;pointer-events:none;z-index:4;background:rgba(255,255,255,.94);border:2px solid var(--accent-2);border-radius:14px;padding:8px 12px;max-width:88%;text-align:center;font-weight:700;font-size:15px;color:#3a4a3f;box-shadow:0 6px 18px rgba(38,54,40,.28);transition:transform .45s cubic-bezier(.2,1.4,.4,1),opacity .3s}
.wheel-result-bingo.show{opacity:1;pointer-events:auto;transform:translate(-50%,-50%) scale(1)}
.wheel-result-bingo.small{font-size:12px;padding:5px 8px}
.life-mini-row{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;padding:8px 4px;cursor:pointer;border-radius:12px;background:var(--card-2,#f3f5ef)}
.life-mini-cell{text-align:center;display:flex;flex-direction:column;gap:2px;min-width:0}
.lm-num{font-size:18px;font-weight:800;color:var(--accent);line-height:1.05}
.lm-num small{font-size:11px;font-weight:600;color:var(--text-dim)}
.lm-cap{font-size:10px;color:var(--text-dim)}
.dish-item .dish-name{font-size:15px;font-weight:600;line-height:1.3}
.dish-item .dish-meta{font-size:11px;color:var(--text-dim);margin-top:1px}
.dish-item .dish-steps{font-size:12px;color:var(--text-dim);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}""",
'CSS.newstyles')
rep(
r"""        <div class="wheel-wrap">
          <div class="wheel" id="cookWheel"></div>
          <div><button class="btn" onclick="Cooking.spin('cook')">转一下</button><div class="hint" id="cookSpinResult">等待选择</div></div>
        </div>""",
r"""        <div class="wheel-wrap">
          <div class="wheel-box">
            <div class="wheel-pointer"></div>
            <div class="wheel" id="cookWheel"></div>
            <div class="wheel-result-bingo" id="cookBingo" onclick="App.go('cooking')"></div>
          </div>
          <div><button class="btn" onclick="Cooking.spin('cook')">转一下</button><div class="hint" id="cookSpinResult">等待选择</div></div>
        </div>""",
'HTML.cookWheel')
rep(
r"""    if(id==='wheel') return `<div class="wheel-mini"><div class="wheel-mini-disk" id="homeWheel"></div><button class="btn ghost small" id="homeWheelSpin" onclick="Cooking.spin('home')">转一下</button><div class="hint" id="homeSpinResult">—</div></div>`;""",
r"""    if(id==='wheel') return `<div class="wheel-mini"><div class="wheel-mini-box"><div class="wheel-mini-pointer"></div><div class="wheel-mini-disk" id="homeWheel"></div><div class="wheel-result-bingo small" id="homeBingo" onclick="App.go('cooking')"></div></div><button class="btn ghost small" id="homeWheelSpin" onclick="Cooking.spin('home')">转一下</button><div class="hint" id="homeSpinResult">—</div></div>`;""",
'HTML.homeWheel')
rep(
r"""  spin(where){ const names=[...new Set(this.wheel().concat(this.list().map(x=>x.name)))]; if(!names.length)return UI.toast('先添加几个转盘菜名'); const pick=names[Math.floor(Math.random()*names.length)]; this.rotation += 720 + Math.floor(Math.random()*360); const wheel=document.getElementById(where==='home'?'homeWheel':'cookWheel'); if(wheel) wheel.style.transform='rotate('+this.rotation+'deg)'; document.getElementById(where==='home'?'homeSpinResult':'cookSpinResult').textContent='今天吃：'+pick; }""",
r"""  spin(where){
    const names=[...new Set(this.wheel().concat(this.list().map(x=>x.name)))];
    if(!names.length) return UI.toast('先添加几个转盘菜名');
    const pick=names[Math.floor(Math.random()*names.length)];
    this.rotation += 720 + Math.floor(Math.random()*360);
    const wheel=document.getElementById(where==='home'?'homeWheel':'cookWheel');
    if(wheel) wheel.style.transform='rotate('+this.rotation+'deg)';
    const side=document.getElementById(where==='home'?'homeSpinResult':'cookSpinResult');
    if(side) side.textContent='今天吃：'+pick;
    /* bingo：结果在转盘中心从小放大出现，点一下进做菜栏（v49 修：之前指针跟着转、结果只显示在下方） */
    const bingo=document.getElementById(where==='home'?'homeBingo':'cookBingo');
    if(bingo){
      bingo.innerHTML='今天吃<br><b>'+Util.esc(pick)+'</b>';
      bingo.classList.remove('show'); void bingo.offsetWidth;
      setTimeout(()=>bingo.classList.add('show'), 200);
      clearTimeout(this._bingoTimer);
      this._bingoTimer=setTimeout(()=>bingo.classList.remove('show'), 4200);
    }
  }""",
'Cooking.spin')
rep(
r"""return `<div class="item" draggable="true" data-sort-id="${x.id}">${x.photoId?Util.mediaImg(x.photoId):(x.photo?`<img class="thumb" src="${Util.esc(x.photo)}" alt="">`:'')}<div class="grow"><div class="title">${Util.esc(x.name)}</div><div class="desc">${Util.esc((x.tags?x.tags+'\n':'')+(x.steps||''))}</div></div><button class="del" onclick="Cooking.move(${i},-1)">↑</button><button class="del" onclick="Cooking.move(${i},1)">↓</button><button class="del" onclick="Cooking.del('${x.id}')">✕</button></div>`;""",
r"""return `<div class="item dish-item" draggable="true" data-sort-id="${x.id}">${x.photoId?Util.mediaImg(x.photoId):(x.photo?`<img class="thumb" src="${Util.esc(x.photo)}" alt="">`:'')}<div class="grow"><div class="dish-name">${Util.esc(x.name)}</div>${x.tags?`<div class="dish-meta">${Util.esc(x.tags)}</div>`:''}<div class="dish-steps">${Util.esc(x.steps||'')}</div></div><button class="del" onclick="Cooking.move(${i},-1)">↑</button><button class="del" onclick="Cooking.move(${i},1)">↓</button><button class="del" onclick="Cooking.del('${x.id}')">✕</button></div>`;""",
'Cooking.dishList')

# ============================================================
# 13. 英语积累深度优化（修 #3）：dialogZh / 真人美式嗓 / 每日一句朗读 / SRS 3-7-14 连对4次 / AI分析
# 13a. content 三条加 dialogZh
rep(
r"""    {quote:'Get busy living or get busy dying.',quoteZh:'要么忙着活，要么忙着死。',word:'profound',wordZh:'深刻的；意义深远的',example:'Her words had a profound effect on how I see failure.',phrase:'be supposed to do sth.',phraseZh:'应该做某事',phraseEx:'You are supposed to hand in your homework by Friday.',phraseWrong:'被禁止做某事',dialog:'A: How is your paper going?\nB: Slowly, but I finally found the main argument.',writing:'我今天完成了一个很小但重要的步骤。',answer:'I completed a small but important step today.'},""",
r"""    {quote:'Get busy living or get busy dying.',quoteZh:'要么忙着活，要么忙着死。',word:'profound',wordZh:'深刻的；意义深远的',example:'Her words had a profound effect on how I see failure.',phrase:'be supposed to do sth.',phraseZh:'应该做某事',phraseEx:'You are supposed to hand in your homework by Friday.',phraseWrong:'被禁止做某事',dialog:'A: How is your paper going?\nB: Slowly, but I finally found the main argument.',dialogZh:'A：你的论文进展如何？\nB：慢是慢了点，但我总算找到了核心论点。',writing:'我今天完成了一个很小但重要的步骤。',answer:'I completed a small but important step today.'},""",
'English.content.0')
rep(
r"""    {quote:'No act of kindness, no matter how small, is ever wasted.',quoteZh:'任何善意，不论多小，都不会被浪费。',word:'resilient',wordZh:'有韧性的；能恢复的',example:'Children are remarkably resilient when they feel safe.',phrase:'make sense',phraseZh:'讲得通；有意义',phraseEx:'His explanation finally makes sense to me now.',phraseWrong:'毫无意义',dialog:'A: Could you explain that in simpler words?\nB: Sure. The idea is that habits reduce decision fatigue.',writing:'我正在学习用更简单的话解释复杂问题。',answer:'I am learning to explain complex ideas in simpler words.'},""",
r"""    {quote:'No act of kindness, no matter how small, is ever wasted.',quoteZh:'任何善意，不论多小，都不会被浪费。',word:'resilient',wordZh:'有韧性的；能恢复的',example:'Children are remarkably resilient when they feel safe.',phrase:'make sense',phraseZh:'讲得通；有意义',phraseEx:'His explanation finally makes sense to me now.',phraseWrong:'毫无意义',dialog:'A: Could you explain that in simpler words?\nB: Sure. The idea is that habits reduce decision fatigue.',dialogZh:'A：能用更简单的话解释一下吗？\nB：当然。核心想法是：习惯能减少决策疲劳。',writing:'我正在学习用更简单的话解释复杂问题。',answer:'I am learning to explain complex ideas in simpler words.'},""",
'English.content.1')
rep(
r"""    {quote:'Clarity comes from action, not thought.',quoteZh:'清晰来自行动，而不只是思考。',word:'deliberate',wordZh:'深思熟虑的；刻意的',example:'He took a deliberate step back to rethink the plan.',phrase:'focus on',phraseZh:'专注于',phraseEx:'I need to focus on what matters most right now.',phraseWrong:'忽略；不关注',dialog:'A: What is your priority today?\nB: I only have three: write, walk, and rest.',writing:'今天我只专注三件最重要的事情。',answer:'Today I will focus only on the three most important things.'}""",
r"""    {quote:'Clarity comes from action, not thought.',quoteZh:'清晰来自行动，而不只是思考。',word:'deliberate',wordZh:'深思熟虑的；刻意的',example:'He took a deliberate step back to rethink the plan.',phrase:'focus on',phraseZh:'专注于',phraseEx:'I need to focus on what matters most right now.',phraseWrong:'忽略；不关注',dialog:'A: What is your priority today?\nB: I only have three: write, walk, and rest.',dialogZh:'A：你今天的优先级是什么？\nB：我只有三件：写、散步、休息。',writing:'今天我只专注三件最重要的事情。',answer:'Today I will focus only on the three most important things.'}""",
'English.content.2')
# 13b. 复习块 -> SRS 方法
rep(
r"""  /* 待复习：答错的，明天再出 */
  reviewQueue(){ return Store.get('english_review',[]); },
  addToReview(item){ const q=this.reviewQueue(); q.push({...item,dueDate:Util.today()}); Store.set('english_review',q); },
  /* 获取某类测试题：优先出该类型待复习（答错的），否则出今天对应的词 */
  getQuiz(type){
    const review = this.reviewQueue().find(x=>x.type===type && x.dueDate<=Util.today());
    if(review) return review; /* 复习题自带 answer/wrong */
    const d=this.today();
    if(type==='word') return {type:'word', text:d.word, answer:d.wordZh, wrong:this.wrongOption(d.wordZh), example:d.example};
    return {type:'phrase', text:d.phrase, answer:d.phraseZh, wrong:d.phraseWrong||'无关选项', example:d.phraseEx||''};
  },
  wrongOption(correct){
    const pool=['随意的；偶然的','明显的；清楚的','逐渐的；渐进的','必要的；必需的','充足的；足够的'];
    return pool.find(x=>x!==correct) || '其他含义';
  },""",
r"""  /* ===== v49：SRS 间隔复习（3/7/14 天，连对 4 次进「已学库」）===== */
  srs(){ return Store.get('english_srs',{}); },
  srsGet(key){ return this.srs()[key]; },
  srsSet(key,val){ const all=this.srs(); all[key]=val; Store.set('english_srs',all); },
  srsKey(type){ return this.todayIndex()+':'+type; },
  todayIndex(){ return new Date().getDate() % this.content.length; },
  /* 用户点「完成学习」时，为这类内容建一条 SRS 复习条目（首次出现才建，初始到期=明天） */
  ensureSRS(type){
    const d=this.today();
    const info={quote:{text:d.quote,answer:d.quoteZh,wrong:this.wrongZh(d.quoteZh)},word:{text:d.word,answer:d.wordZh,wrong:this.wrongOption(d.wordZh)},phrase:{text:d.phrase,answer:d.phraseZh,wrong:d.phraseWrong||this.wrongZh(d.phraseZh)},dialog:{text:d.dialog,answer:d.dialogZh,wrong:this.wrongZh(d.dialogZh)}}[type];
    if(!info) return;
    const key=this.srsKey(type);
    if(!this.srsGet(key)) this.srsSet(key,{key,type,text:info.text,answer:info.answer,wrong:info.wrong,reps:0,due:Util.dateAdd(Util.today(),1),mastered:false});
  },
  wrongZh(correct){ const pool=['随意的；偶然的','明显的；清楚的','逐渐的；渐进的','必要的；必需的','充足的；足够的','被禁止做某事','毫无意义','忽略；不关注']; return pool.find(x=>x!==correct) || '其他含义'; },
  wrongOption(correct){
    const pool=['随意的；偶然的','明显的；清楚的','逐渐的；渐进的','必要的；必需的','充足的；足够的'];
    return pool.find(x=>x!==correct) || '其他含义';
  },
  /* 今天该复习的条目：没掌握且已到期 */
  dueItems(){ const t=Util.today(); return Object.values(this.srs()).filter(x=>!x.mastered && x.due<=t); },
  /* 连对次数 -> 下次间隔天数（3/7/14）；连对满 4 次即掌握 */
  nextInterval(reps){ return ({1:3,2:7,3:14})[reps] || 14; },""",
'English.srs')
# 13c. render（加每日一句朗读 + 对话中文）
rep(
r"""  render(){
    const d=this.today();
    const doneList=Store.getDaily('english_done',[]);
    const doneFn=name=>doneList.includes(name);
    englishCards.innerHTML=[
      `<div class="card"><h2>💬 每日一句</h2><div class="desc">${Util.esc(d.quote)}<br>${Util.esc(d.quoteZh)}</div>${doneFn('每日一句')?'<div style="margin-top:10px;color:var(--accent);font-weight:700;font-size:13px">✅ 已完成</div>':`<button class="btn small" style="margin-top:10px" onclick="English.done('每日一句')">完成学习</button>`}</div>`,
      `<div class="card"><h2>🔤 每日单词</h2><div class="desc">${Util.esc(d.word)}<br>${Util.esc(d.wordZh)}</div><div class="hint" style="margin-top:6px">例句：${Util.esc(d.example||'')}</div>${doneFn('每日单词')?'<div style="margin-top:10px;color:var(--accent);font-weight:700;font-size:13px">✅ 已完成</div>':`<button class="btn small" style="margin-top:10px" onclick="English.done('每日单词')">完成学习</button>`}</div>`,
      `<div class="card"><h2>🧩 固定搭配</h2><div class="desc">${Util.esc(d.phrase)} · ${Util.esc(d.phraseZh)}</div>${d.phraseEx?`<div class="hint" style="margin-top:6px">例句：${Util.esc(d.phraseEx)}</div>`:''}${doneFn('固定搭配')?'<div style="margin-top:10px;color:var(--accent);font-weight:700;font-size:13px">✅ 已完成</div>':`<button class="btn small" style="margin-top:10px" onclick="English.done('固定搭配')">完成学习</button>`}</div>`,
      `<div class="card"><h2>🗣️ 每日对话</h2><div class="desc">${Util.esc(d.dialog).replace(/\n/g,'<br>')}</div>${doneFn('每日对话')?'<div style="margin-top:10px;color:var(--accent);font-weight:700;font-size:13px">✅ 已完成</div>':`<div style="display:flex;gap:6px;margin-top:10px"><button class="btn small" onclick="English.playDialog()">播放</button><button class="btn small ghost" onclick="English.done('每日对话')">完成学习</button></div>`}</div>`
    ].join('');
    /* 测试卡片 */
    this.renderQuiz();
    englishWritingPrompt.textContent=d.writing;
    englishResult.textContent='';
  },""",
r"""  render(){
    const d=this.today();
    const doneList=Store.getDaily('english_done',[]);
    const doneFn=name=>doneList.includes(name);
    englishCards.innerHTML=[
      `<div class="card"><h2>💬 每日一句</h2><div class="desc">${Util.esc(d.quote)}<br><span style="color:var(--text-dim)">${Util.esc(d.quoteZh)}</span></div>${doneFn('每日一句')?'<div style="margin-top:10px;color:var(--accent);font-weight:700;font-size:13px">✅ 已完成</div>':`<div style="display:flex;gap:6px;margin-top:10px"><button class="btn small" onclick="English.playQuote()">🔊 朗读</button><button class="btn small ghost" onclick="English.done('每日一句')">完成学习</button></div>`}</div>`,
      `<div class="card"><h2>🔤 每日单词</h2><div class="desc">${Util.esc(d.word)}<br>${Util.esc(d.wordZh)}</div><div class="hint" style="margin-top:6px">例句：${Util.esc(d.example||'')}</div>${doneFn('每日单词')?'<div style="margin-top:10px;color:var(--accent);font-weight:700;font-size:13px">✅ 已完成</div>':`<button class="btn small" style="margin-top:10px" onclick="English.done('每日单词')">完成学习</button>`}</div>`,
      `<div class="card"><h2>🧩 固定搭配</h2><div class="desc">${Util.esc(d.phrase)} · ${Util.esc(d.phraseZh)}</div>${d.phraseEx?`<div class="hint" style="margin-top:6px">例句：${Util.esc(d.phraseEx)}</div>`:''}${doneFn('固定搭配')?'<div style="margin-top:10px;color:var(--accent);font-weight:700;font-size:13px">✅ 已完成</div>':`<button class="btn small" style="margin-top:10px" onclick="English.done('固定搭配')">完成学习</button>`}</div>`,
      `<div class="card"><h2>🗣️ 每日对话</h2><div class="desc">${Util.esc(d.dialog).replace(/\n/g,'<br>')}<br><span style="color:var(--text-dim)">${Util.esc(d.dialogZh).replace(/\n/g,'<br>')}</span></div>${doneFn('每日对话')?'<div style="margin-top:10px;color:var(--accent);font-weight:700;font-size:13px">✅ 已完成</div>':`<div style="display:flex;gap:6px;margin-top:10px"><button class="btn small" onclick="English.playDialog()">🔊 朗读对话</button><button class="btn small ghost" onclick="English.done('每日对话')">完成学习</button></div>`}</div>`
    ].join('');
    /* 测试卡片 */
    this.renderQuiz();
    englishWritingPrompt.textContent=d.writing;
    englishResult.textContent='';
  },""",
'English.render')
# 13d. renderQuiz
rep(
r"""  renderQuiz(){
    const box=document.getElementById('englishQuiz');
    if(!box) return;
    if(Store.getDaily('english_done',[]).includes('测试')){
      box.innerHTML=`<div class="card" style="text-align:center;padding:24px"><div style="font-size:36px;margin-bottom:8px">🎉</div><div style="color:var(--accent);font-weight:700">今日测试已完成！已自动入账金币</div><div class="hint" style="margin-top:6px">明天再来挑战新题</div></div>`;
      return;
    }
    const st=Store.getDaily('english_quiz',{word:null,phrase:null});
    box.innerHTML=`<div class="eng-q-row">${this.quizCard(this.getQuiz('word'), st.word) + this.quizCard(this.getQuiz('phrase'), st.phrase)}</div>`;
  },""",
r"""  renderQuiz(){
    const box=document.getElementById('englishQuiz');
    if(!box) return;
    if(Store.getDaily('english_done',[]).includes('测试')){
      box.innerHTML=`<div class="card" style="text-align:center;padding:24px"><div style="font-size:36px;margin-bottom:8px">🎉</div><div style="color:var(--accent);font-weight:700">今日测试已完成！已自动入账金币</div><div class="hint" style="margin-top:6px">明天再来挑战新题</div></div>`;
      return;
    }
    const due=this.dueItems();
    if(!due.length){
      box.innerHTML=`<div class="card" style="text-align:center;padding:20px"><div style="font-size:30px;margin-bottom:6px">🌟</div><div style="font-weight:700;color:var(--accent)">今天没有要复习的内容</div><div class="hint" style="margin-top:6px">学过的都记牢啦，点下面完成今日复习打卡</div><button class="btn small" style="margin-top:10px" onclick="English.completeTestEmpty()">完成复习打卡</button></div>`;
      return;
    }
    box.innerHTML=`<div class="eng-q-row">${due.map(q=>this.quizCard(q)).join('')}</div>`;
  },""",
'English.renderQuiz')
# 13e. quizCard
rep(
r"""  quizCard(q, res){
    const label = q.type==='word' ? '单词测试' : '搭配测试';
    const sub = q.type==='word' ? '今天学的单词' : '今天的固定搭配';
    if(res){
      return `<div class="card eng-quiz-card">
        <h2>🧪 ${label}</h2>
        <div class="eng-q-word">${Util.esc(q.text)}</div>
        <div style="text-align:center;padding:8px 0 4px">
          <div style="font-size:32px">${res.isCorrect?'✅':'❌'}</div>
          <div style="font-weight:700;color:${res.isCorrect?'var(--accent)':'var(--accent-2)'};font-size:16px">${res.isCorrect?'答对了，已收进学会库':'答错了，已记下，明天再练'}</div>
          <div style="margin-top:6px;font-size:14px"><b>${Util.esc(q.text)}</b> = ${Util.esc(q.answer)}</div>
        </div>
      </div>`;
    }
    const options=[q.answer, q.wrong].sort(()=>Math.random()-.5);
    return `<div class="card eng-quiz-card">
      <h2>🧪 ${label}</h2>
      <div class="eng-q-word">${Util.esc(q.text)}</div>
      <p class="hint" style="margin-top:4px">${sub}：选择正确的中文意思</p>
      <div class="eng-q-options">
        ${options.map(opt=>`<button class="btn eng-q-opt" onclick="English.answerQuiz('${q.type}','${Util.esc(opt)}')">${Util.esc(opt)}</button>`).join('')}
      </div>
    </div>`;
  },""",
r"""  quizCard(q){
    const label={quote:'句子复习',word:'单词复习',phrase:'搭配复习',dialog:'对话复习'}[q.type]||'复习';
    const sub={quote:'这句话的中文意思是？',word:'这个单词的中文意思是？',phrase:'这个搭配的中文意思是？',dialog:'这段对话的中文意思是？'}[q.type]||'选择正确的中文意思';
    const res=q._res;
    if(res){
      return `<div class="card eng-quiz-card">
        <h2>🧪 ${label}</h2>
        <div class="eng-q-word">${Util.esc(q.text)}</div>
        <div style="text-align:center;padding:8px 0 4px">
          <div style="font-size:32px">${res.isCorrect?'✅':'❌'}</div>
          <div style="font-weight:700;color:${res.isCorrect?'var(--accent)':'var(--accent-2)'};font-size:16px">${res.isCorrect?'答对啦，进度 +1':'答错了，明天再练'}</div>
          <div style="margin-top:6px;font-size:14px"><b>${Util.esc(q.text)}</b> = ${Util.esc(q.answer)}</div>
        </div>
      </div>`;
    }
    const options=[q.answer, q.wrong].sort(()=>Math.random()-.5);
    return `<div class="card eng-quiz-card">
      <h2>🧪 ${label}</h2>
      <div class="eng-q-word">${Util.esc(q.text)}</div>
      <p class="hint" style="margin-top:4px">${sub}</p>
      <div class="eng-q-options">
        ${options.map(opt=>`<button class="btn eng-q-opt" onclick="English.answerQuiz('${q.key}','${Util.esc(opt)}')">${Util.esc(opt)}</button>`).join('')}
      </div>
      <div class="hint" style="margin-top:6px">已连对 ${q.reps}/4 · 还差 ${Math.max(0,4-q.reps)} 次进「已学库」</div>
    </div>`;
  },""",
'English.quizCard')
# 13f. answerQuiz
rep(
r"""  answerQuiz(type, selected){
    const q=this.getQuiz(type);
    const isCorrect = selected===q.answer;
    const st=Store.getDaily('english_quiz',{word:null,phrase:null});
    st[type]={selected, isCorrect};
    Store.setDaily('english_quiz', st);
    if(isCorrect) this.addMastered({text:q.text, type, date:Util.today()});
    else this.addToReview({text:q.text, type, answer:q.answer, wrong:q.wrong});
    this.renderQuiz();
    this.checkTestComplete();
  },""",
r"""  answerQuiz(key, selected){
    const q=this.srsGet(key); if(!q) return;
    const isCorrect = selected===q.answer;
    if(isCorrect){
      q.reps += 1;
      if(q.reps >= 4){ q.mastered = true; this.addMastered({text:q.text, type:q.type, date:Util.today()}); }
      else { q.due = Util.dateAdd(Util.today(), this.nextInterval(q.reps)); }
    } else { q.reps = 0; q.due = Util.today(); }
    this.srsSet(key, q);
    this.renderQuizFresh(key, isCorrect);
    this.checkTestComplete();
  },""",
'English.answerQuiz')
# 13g. checkTestComplete（含 completeTestEmpty + renderQuizFresh）
rep(
r"""  checkTestComplete(){
    const st=Store.getDaily('english_quiz',{word:null,phrase:null});
    if(st.word && st.phrase && !Store.getDaily('english_done',[]).includes('测试')){
      Store.setDaily('english_done',[...new Set(Store.getDaily('english_done',[]).concat('测试'))]);
      Coin.earn('english_test','完成英语测试');
      this.render();
      Home.render();
    }
  },""",
r"""  completeTestEmpty(){ if(Store.getDaily('english_done',[]).includes('测试')) return; Store.setDaily('english_done',[...new Set(Store.getDaily('english_done',[]).concat('测试'))]); this.render(); Home.render(); UI.toast('✅ 复习打卡完成'); },
  checkTestComplete(){
    if(!this.dueItems().length && !Store.getDaily('english_done',[]).includes('测试')){
      Store.setDaily('english_done',[...new Set(Store.getDaily('english_done',[]).concat('测试'))]);
      Coin.earn('english_test','完成英语复习');
      this.render(); Home.render();
    }
  },
  renderQuizFresh(key, isCorrect){
    const q=this.srsGet(key); if(!q){ this.renderQuiz(); return; }
    if(q.mastered || q.due > Util.today()){
      const due=this.dueItems();
      if(!due.length){ this.renderQuiz(); return; }
      const box=document.getElementById('englishQuiz'); if(box) box.innerHTML=`<div class="eng-q-row">${due.map(x=>this.quizCard(x)).join('')}</div>`;
      return;
    }
    const shown=this.dueItems().map(x=> x.key===key ? {...x, _res:{isCorrect}} : x);
    const box=document.getElementById('englishQuiz'); if(box) box.innerHTML=`<div class="eng-q-row">${shown.map(x=>this.quizCard(x)).join('')}</div>`;
  },""",
'English.checkTestComplete')
# 13h. reveal + playDialog -> 加 aiAnalyze / pickVoice / speak / playQuote
rep(
r"""  reveal(){ englishResult.textContent='参考翻译：\n'+this.today().answer+'\n\n你的答案：\n'+(englishAnswer.value||'还没写'); },
  playDialog(){ if(!('speechSynthesis' in window)) return UI.toast('当前浏览器不支持朗读'); speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(this.today().dialog.replace(/^A:|^B:/gm,'')); u.lang='en-US'; u.rate=.9; speechSynthesis.speak(u); },""",
r"""  reveal(){ englishResult.textContent='参考翻译：\n'+this.today().answer+'\n\n你的答案：\n'+(englishAnswer.value||'还没写'); },
  /* AI 分析我的翻译（v49） */
  async aiAnalyze(){
    const prompt='我是正在自学英语的学习者。\\n【今天的翻译练习】'+this.today().writing+'\\n【参考答案（英文）】'+this.today().answer+'\\n【我的翻译】'+(englishAnswer.value||'(空)')+'\\n请像一位耐心的老师，用中文分条、简短地指出我翻译里的问题、可以改进的地方，并给一句更地道的参考译法。';
    englishResult.textContent='AI 正在分析你的翻译…';
    try{ const r=await AI.ask(prompt); englishResult.textContent=(typeof r==='string')?r:JSON.stringify(r); }
    catch(e){ englishResult.textContent='分析失败：'+(e&&e.message||e); }
  },
  /* 朗读：优先选美式真人嗓(en-US 自然语音)，避免机械音（v49） */
  _voice:null,
  pickVoice(){
    const vs=(window.speechSynthesis && speechSynthesis.getVoices()) || [];
    return this._voice = vs.find(v=>/en[-_]US/i.test(v.lang) && /(Google|Natural|Premium|Samantha|Microsoft|Female)/i.test(v.name)) || vs.find(v=>/en[-_]US/i.test(v.lang)) || vs.find(v=>/^en/i.test(v.lang)) || null;
  },
  speak(text){
    if(!('speechSynthesis' in window)) return UI.toast('当前浏览器不支持朗读');
    speechSynthesis.cancel();
    const u=new SpeechSynthesisUtterance(text);
    const v=this.pickVoice(); if(v) u.voice=v;
    u.lang='en-US'; u.rate=.95; u.pitch=1;
    speechSynthesis.speak(u);
  },
  playDialog(){ this.speak(this.today().dialog.replace(/^[AB]:/gm,'')); },
  playQuote(){ this.speak(this.today().quote); },""",
'English.reveal/play')
# 13i. done
rep(
r"""  done(name){
    const list = [...new Set(Store.getDaily('english_done',[]).concat(name))];
    Store.setDaily('english_done', list);
    UI.toast('✅ 已完成学习');
    /* 完成全部 4 项学习（不含测试）奖励「英语全勤」金币 */
    const learn=['每日一句','每日单词','固定搭配','每日对话'];
    if(learn.every(n=>list.includes(n)) && !Store.getDaily('english_all',false)){
      Coin.earn('english','完成英语全部学习');
      Store.setDaily('english_all',true);
    }
    this.render();
    Home.render();
  },""",
r"""  done(name){
    const list = [...new Set(Store.getDaily('english_done',[]).concat(name))];
    Store.setDaily('english_done', list);
    /* 学完任一项 -> 登记进 SRS，之后按 3/7/14 天间隔复习 */
    const tMap={'每日一句':'quote','每日单词':'word','固定搭配':'phrase','每日对话':'dialog'};
    if(tMap[name]) this.ensureSRS(tMap[name]);
    UI.toast('✅ 已完成学习');
    /* 完成全部 4 项学习奖励「英语全勤」金币 */
    const learn=['每日一句','每日单词','固定搭配','每日对话'];
    if(learn.every(n=>list.includes(n)) && !Store.getDaily('english_all',false)){
      Coin.earn('english','完成英语全部学习');
      Store.setDaily('english_all',true);
    }
    if(tMap[name]) this.checkTestComplete();
    this.render();
    Home.render();
  },""",
'English.done')
# 13j. 英语写作卡加「让 AI 分析我的翻译」按钮
rep(
r"""        <button class="btn" style="margin-top:10px;width:100%" onclick="English.reveal()">查看参考翻译</button>""",
r"""        <button class="btn" style="margin-top:10px;width:100%" onclick="English.reveal()">查看参考翻译</button>
        <button class="btn ghost" style="margin-top:8px;width:100%" onclick="English.aiAnalyze()">🤖 让 AI 分析我的翻译</button>""",
'English.html.aiBtn')

# ============================================================
# 14. sw.js 版本号
def rep_sw(old, new, label=''):
    global sw
    n = sw.count(old)
    if n != 1:
        fails.append('[SW %s] 期望 1 次，实际 %d' % (label, n)); print('!! SW 失败 [%s]' % label); return
    sw = sw.replace(old, new, 1); print('OK  [SW %s]' % label)
rep_sw(
r"""const CACHE = 'xiaozhi-workbench-v48';""",
r"""const CACHE = 'xiaozhi-workbench-v49';""",
'CACHE')
rep_sw(
r"""const BUILD = '2026-08-13-v48';""",
r"""const BUILD = '2026-08-14-v49';""",
'BUILD')

# ============================================================
print('\n=== 校验 ===')
checks = [
    ('english_srs', 'SRS 数据结构'),
    ('wheel-pointer', '转盘指针(不转)'),
    ('wheel-result-bingo', '转盘 bingo 结果'),
    ('life-mini-row', '生活万花筒单行'),
    ('Gift.save', '份子钱保存'),
    ('Gift.duplicate', '份子钱再记一笔'),
    ('giftEventOptions', '份子钱事件下拉'),
    ('Quick.copy', '灵感复制'),
    ('Coin.earn(\'notes\'', '经验摘录金币'),
    ('notes:{name', '金币来源 notes'),
    ('playQuote', '每日一句朗读'),
    ('aiAnalyze', 'AI 翻译分析'),
    ('_trackerSeeded', '习惯只种一次'),
    ('text-security:disc', '密码掩码'),
]
for needle, desc in checks:
    ok = needle in s
    print(('  ✓ ' if ok else '  ✗ ') + desc + '  (' + needle + ')')
    if not ok: fails.append('check:' + needle)

if fails:
    print('\n❌ 失败项：')
    for f in fails: print('   - ' + f)
    sys.exit(1)

with io.open(INDEX, 'w', encoding='utf-8') as f:
    f.write(s)
with io.open(SW, 'w', encoding='utf-8') as f:
    f.write(sw)
print('\n✅ 全部替换成功，已写入 index.html 与 sw.js')
