#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v60 补丁：解决两个 v59 残留 bug
  ① 菜篮子：再来一道按钮触发 App.go('cooking') + scrollIntoView → 用户感觉退回首页；
            卡片图走 Util.mediaImg 输出 class="thumb"（54×54 固定），图片没铺满。
  ② 经验摘录：外层分类卡片只显示文本预览 + 计数，
              openCat 严格 === 过滤、render 用 cats.includes() 分组，导致同一分类
              计数不一致（如 成长 显示 3 但内层只 2 条）；
              用户希望外层直接显示内层 mini cards。

修复：
  A. Cooking.duplicate()：去掉 App.go + scrollIntoView + setTimeout 焦点；
     只 render + 立即焦点 dishName + toast
  B. 菜篮子卡片 cover：把 Util.mediaImg(x.photoId) 换成原生 <img class="dc-cover">
     （带 data-media / onclick=Media.openFull / stopPropagation）
     → 不再被 .thumb 54×54 卡死，真正 object-fit:cover 沾满卡片
  C. 经验摘录外层分类卡片：body 直接渲染 note-mini-card 网格（最多 4 张），
     多余的显示「查看全部 →」链接
  D. 归一化分类：bucketing 与 openCat 过滤都用 (x.cat||'').trim()
  E. 升级 BUILD_VERSION / sw.js CACHE / BUILD 到 v60
"""
import io, sys

INDEX = 'index.html'
SW = 'sw.js'

# ---------- helpers ----------
def patch_once(text, old, new, label):
    cnt = text.count(old)
    if cnt != 1:
        raise SystemExit(f'[FAIL] {label}: 命中 {cnt} 次 ≠ 1，未替换')
    return text.replace(old, new, 1)

# ---------- 读取 ----------
with io.open(INDEX, 'r', encoding='utf-8') as f:
    html = f.read()
with io.open(SW, 'r', encoding='utf-8') as f:
    sw = f.read()

# ---------- A. Cooking.duplicate() 简化 ----------
A_OLD = """  /* v59：「再来一道」按钮（卡片上 / 详情视图上）：复制这道菜的名字/标签/步骤到表单，作为新菜录入（不复制图） */
  duplicate(id){
    const it = this.list().find(x=>x.id===id); if(!it) return;
    /* 取消编辑态 → 保存时会插入新菜 */
    Store.remove('dish_editing');
    if(typeof dishName !== 'undefined' && dishName) dishName.value = it.name || '';
    if(typeof dishTags !== 'undefined' && dishTags) dishTags.value = it.tags || '';
    if(typeof dishSteps !== 'undefined' && dishSteps) dishSteps.value = it.steps || '';
    if(typeof dishPhoto !== 'undefined' && dishPhoto) dishPhoto.value = '';
    this.render();
    (document.getElementById('page-cooking')||document.body)?.scrollIntoView?.({behavior:'smooth', block:'start'});
    setTimeout(()=>{ try{ document.getElementById('dishName')?.focus(); }catch(e){} }, 220);
    /* 如果在别的页面，回到做菜栏 */
    try{ if(typeof App !== 'undefined' && App.go) App.go('cooking'); }catch(e){}
    UI.toast('已预填：'+(it.name||'这道菜')+'；改完点「保存菜谱」即可');
  },"""
A_NEW = """  /* v60：「再来一道」（卡片 / 详情视图共用）—— 复制这道菜的 name/tags/steps 到顶部表单作为新菜录入（不复制图）。
     关键修复：不再调 App.go('cooking')（会被 history.pushState 记进栈，下一次 popstate 把页面踢飞）、
     也不再 scrollIntoView（会把页面滚到顶部，让用户觉得「退回了桌面」）。
     只做：render 一次 + 立即聚焦菜名 + toast。 */
  duplicate(id){
    const it = this.list().find(x=>x.id===id); if(!it) return;
    /* 取消编辑态 → 保存时会插入新菜 */
    Store.remove('dish_editing');
    if(typeof dishName !== 'undefined' && dishName) dishName.value = it.name || '';
    if(typeof dishTags !== 'undefined' && dishTags) dishTags.value = it.tags || '';
    if(typeof dishSteps !== 'undefined' && dishSteps) dishSteps.value = it.steps || '';
    if(typeof dishPhoto !== 'undefined' && dishPhoto) dishPhoto.value = '';
    this.render();
    /* 立即聚焦菜名（不开 setTimeout，避免与 popstate / 焦点事件相互影响） */
    try{ document.getElementById('dishName')?.focus?.(); }catch(e){}
    UI.toast('已预填：'+(it.name||'这道菜')+'；改完点「保存菜谱」即可');
  },"""
html = patch_once(html, A_OLD, A_NEW, 'A.duplicate 简化')

# ---------- B. 菜篮子卡片 cover 用 dc-cover 沾满 ----------
# 原：const cover = x.photoId ? Util.mediaImg(x.photoId, x.name) : (x.photo ? `<img class="dc-cover" src="...">` : `<div class="dc-placeholder">...`);
# 改：x.photoId 时直接 <img class="dc-cover" data-media=...>（Media.paint 异步补 src），不再走 .thumb 54x54
B_OLD = """    const recipeHtml = Object.entries(groups).length?Object.entries(groups).map(([tag,rows])=>`<section style="margin-bottom:12px"><h2>${Util.esc(tag)}</h2><div class="dish-grid">${rows.map((x)=>{ const cover = x.photoId ? Util.mediaImg(x.photoId, x.name) : (x.photo ? `<img class="dc-cover" src="${Util.esc(x.photo)}" alt="${Util.esc(x.name)}">` : `<div class="dc-placeholder">${Util.esc((x.name||'?')[0])}</div>`); return `<div class="dish-card" draggable="true" data-sort-id="${x.id}" onclick="Cooking.openDetail('${x.id}')">${cover}<div class="dc-name">${Util.esc(x.name)}</div><button class="dc-addone" type="button" onclick="event.stopPropagation();Cooking.duplicate('${x.id}')" title="再来一道：复制这道菜到表单开始录入新菜">+</button></div>`; }).join('')}</div></section>`).join(''):'';"""
B_NEW = """    /* v60：x.photoId 时不再走 Util.mediaImg（那会输出 class=\"thumb\"，被全局 54×54 样式锁死，导致图片只在卡片里缩成小方块），
       改用 class=\"dc-cover\" 让 CSS 的 object-fit:cover 真正沾满整张卡片。点 cover 弹图片大图（event.stopPropagation 避免误触卡片详情）。 */
    const recipeHtml = Object.entries(groups).length?Object.entries(groups).map(([tag,rows])=>`<section style="margin-bottom:12px"><h2>${Util.esc(tag)}</h2><div class="dish-grid">${rows.map((x)=>{ const cover = x.photoId ? `<img class="dc-cover" data-media="${Util.esc(x.photoId)}" alt="${Util.esc(x.name)}" onclick="event.stopPropagation();Media.openFull('${Util.esc(x.photoId)}')">` : (x.photo ? `<img class="dc-cover" src="${Util.esc(x.photo)}" alt="${Util.esc(x.name)}">` : `<div class="dc-placeholder">${Util.esc((x.name||'?')[0])}</div>`); return `<div class="dish-card" draggable="true" data-sort-id="${x.id}" onclick="Cooking.openDetail('${x.id}')">${cover}<div class="dc-name">${Util.esc(x.name)}</div><button class="dc-addone" type="button" onclick="event.stopPropagation();Cooking.duplicate('${x.id}')" title="再来一道：复制这道菜到表单开始录入新菜">+</button></div>`; }).join('')}</div></section>`).join(''):'';"""
html = patch_once(html, B_OLD, B_NEW, 'B.cover dc-cover')

# ---------- C. 经验摘录外层分类卡片直接渲染 mini cards ----------
C_OLD = """    const cards = cats.map(cat => {
      const items = byCat[cat] || [];
      const latest = items[0];
      /* v59：去掉分类卡片顶部大图（小卡片本身已经显示图，外层不再重复） */
      const preview = latest ? (this._stripMedia(latest.text || '') || latest.title || '（空）').slice(0,140) : '';
      const count = items.length;
      const isEmpty = !latest;
      const date = latest ? (latest.date || '') : '';
      return `<div class="note-cat-card${isEmpty?' note-cat-empty':''}" onclick="Notes.openCat('${Util.esc(cat)}')">
        <div class="nc-head"><span class="nc-title">📁 ${Util.esc(cat)}</span><span class="nc-count">${count}</span></div>
        <div class="nc-preview">${preview ? Util.esc(preview) : '<span style="color:var(--text-dim)">点上面「保存摘录」会自动归到这里</span>'}</div>
        <div class="nc-date">${date ? ('最新 · '+Util.esc(date)) : '还没有摘录'}</div>
      </div>`;
    }).join('');"""
C_NEW = """    /* v60：外层分类卡片 body 直接渲染 mini cards（最多 4 张），不再只显示文本预览。
       这样外层看到的卡片数 = openCat 里看到的卡片数，计数永远对得上。
       多于 4 张时显示「查看全部 →」链接，跳到分类详情全屏。 */
    const cards = cats.map(cat => {
      const items = byCat[cat] || [];
      const count = items.length;
      const isEmpty = !items.length;
      /* 最多展示 4 张 mini card；多于 4 张时显示「查看全部」链接 */
      const showItems = cards.slice(0, 4);
      const inner = isEmpty
        ? '<div class=\"nc-preview\" style=\"color:var(--text-dim)\">点上面「保存摘录」会自动归到这里</div>'
        : '<div class=\"nc-mini-grid\">' + showItems.map(x=>this._miniCard(x)).join('') + '</div>'
          + (count > 4
              ? `<div class=\"nc-see-all\" onclick=\"event.stopPropagation();Notes.openCat('${Util.esc(cat)}')\">查看全部 ${count} 条 →</div>`
              : (count > 0 ? `<div class=\"nc-see-all\" onclick=\"event.stopPropagation();Notes.openCat('${Util.esc(cat)}')\">查看分类 →</div>` : ''));
      return `<div class=\"note-cat-card${isEmpty?' note-cat-empty':''}\">
        <div class=\"nc-head\"><span class=\"nc-title\">📁 ${Util.esc(cat)}</span><span class=\"nc-count\">${count}</span></div>
        ${inner}
      </div>`;
    }).join('');"""
html = patch_once(html, C_OLD, C_NEW, 'C.外层分类卡片')

# 注：上面变量名 showItems = cards.slice(0, 4) —— 修一下
# 重写：
C_NEW2 = """    /* v60：外层分类卡片 body 直接渲染 mini cards（最多 4 张），不再只显示文本预览。
       这样外层看到的卡片数 = openCat 里看到的卡片数，计数永远对得上。
       多于 4 张时显示「查看全部 →」链接，跳到分类详情全屏。 */
    const cards = cats.map(cat => {
      const items = byCat[cat] || [];
      const count = items.length;
      const isEmpty = !items.length;
      /* 最多展示 4 张 mini card；多于 4 张时显示「查看全部」链接 */
      const showItems = items.slice(0, 4);
      const inner = isEmpty
        ? '<div class=\"nc-preview\" style=\"color:var(--text-dim)\">点上面「保存摘录」会自动归到这里</div>'
        : '<div class=\"nc-mini-grid\">' + showItems.map(x=>this._miniCard(x)).join('') + '</div>'
          + (count > 4
              ? `<div class=\"nc-see-all\" onclick=\"event.stopPropagation();Notes.openCat('${Util.esc(cat)}')\">查看全部 ${count} 条 →</div>`
              : (count > 0 ? `<div class=\"nc-see-all\" onclick=\"event.stopPropagation();Notes.openCat('${Util.esc(cat)}')\">查看分类 →</div>` : ''));
      return `<div class=\"note-cat-card${isEmpty?' note-cat-empty':''}\">
        <div class=\"nc-head\"><span class=\"nc-title\">📁 ${Util.esc(cat)}</span><span class=\"nc-count\">${count}</span></div>
        ${inner}
      </div>`;
    }).join('');"""
# 我们刚刚已经把 patch_once 应用到 html 了；现在覆盖掉它的结果
html = html.replace(C_NEW, C_NEW2)

# ---------- D. 归一化 cat：bucketing + openCat 过滤都用 trim ----------
D1_OLD = "list.forEach(x => { const c = cats.includes(x.cat) ? x.cat : (cats[0]||'未分类'); (byCat[c] = byCat[c] || []).push(x); });"
D1_NEW = "/* v60：用 trim 归一化分类名，防止「成长 / 成长 」之类空白差异导致分组与计数错位 */ list.forEach(x => { const raw = (x.cat||'').trim() || (cats[0]||'未分类'); const c = cats.includes(raw) ? raw : (cats[0]||'未分类'); (byCat[c] = byCat[c] || []).push(x); });"
html = patch_once(html, D1_OLD, D1_NEW, 'D1.bucketing trim')

# 同步渲染「全部摘录」卡片也要 trim：
D2_OLD = "    const allLatest = list[0];"
# 不动 list —— 是 list 已经在上面 trim 过分类了，所以 allLatest 用法无需修改。

# openCat 过滤同步 trim：
D3_OLD = "    const list = cat==='__all__' ? this.list() : this.list().filter(x => x.cat === cat);"
D3_NEW = "    /* v60：过滤也用 trim 归一化（与 render 的 bucketing 一致） */\n    const list = cat==='__all__' ? this.list() : this.list().filter(x => (x.cat||'').trim() === (cat||'').trim());"
html = patch_once(html, D3_OLD, D3_NEW, 'D3.openCat filter trim')

# ---------- E. 升级 BUILD_VERSION ----------
E_OLD = "const BUILD_VERSION = '2026-08-14-v59';"
E_NEW = "const BUILD_VERSION = '2026-08-14-v60';"
html = patch_once(html, E_OLD, E_NEW, 'E.BUILD_VERSION v60')

# sw.js 升级
sw = patch_once(sw, "const CACHE = 'xiaozhi-workbench-v59';", "const CACHE = 'xiaozhi-workbench-v60';", 'sw.CACHE v60')
sw = patch_once(sw, "const BUILD = '2026-08-14-v59';", "const BUILD = '2026-08-14-v60';", 'sw.BUILD v60')

# ---------- 写入 ----------
with io.open(INDEX, 'w', encoding='utf-8') as f:
    f.write(html)
with io.open(SW, 'w', encoding='utf-8') as f:
    f.write(sw)
print('[OK] v60 补丁完成')