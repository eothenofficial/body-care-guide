/* Reader UI. No trackers, remote libraries, medical inference or account system. */
(() => {
  'use strict';
  const data = window.__GUIDE_DATA__;
  const main = document.getElementById('main');
  if (!data || !Array.isArray(data.entries) || !Array.isArray(data.sources)) {
    main.textContent = '内容未能载入。请重新构建项目，或打开下载目录中的完整正文。';
    return;
  }
  const entries = data.entries;
  const chapters = data.chapters;
  const manifest = data.manifest || {};
  const offlineDocument = location.protocol === 'file:' || /\/guide-offline\.html$/.test(location.pathname);
  const byId = new Map(entries.map(e => [e.id, e]));
  const bySource = new Map(data.sources.map(s => [s.id, s]));
  const byNumber = new Map(data.sources.map((s, i) => [String(s.number || i + 1), s]));
  const chapterMap = new Map(chapters.map(c => [c.id, c]));
  const names = {eyes:'眼睛',nose:'鼻子',lips:'嘴唇',oral:'口腔',ears:'耳朵',skin:'面部皮肤',hair:'头发'};
  const iconNames = {eyes:'eye',nose:'nose',lips:'lips',oral:'tooth',ears:'ear',skin:'skin',hair:'hair'};
  const colors = {eyes:'var(--sage)',nose:'var(--sand)',lips:'var(--rose)',oral:'var(--blue)',ears:'var(--sand)',skin:'var(--rose)',hair:'var(--sage)'};
  const descriptions = {eyes:'看清、舒服，再把镜片戴安全。',nose:'整理鼻毛，分清黑头，照顾鼻腔。',lips:'减少干裂和刺激，再选润唇用品。',oral:'牙齿、牙龈和舌面，一起照顾好。',ears:'少伸工具，控制音量，留意听力。',skin:'做好基础护理，再为具体改变花钱。',hair:'先照顾头皮，再做喜欢的发型。'};
  const fieldLabels = {cost:'成本',plain:'说人话',benefit:'收益',evidence:'证据等级',sources:'来源',notes:'备注'};
  const synonymGroups = [['ok镜','角膜塑形镜'],['针眼','麦粒肿'],['水牙线','冲牙器'],['a醇','视黄醇'],['a醛','视黄醛'],['痘痘','痤疮','粉刺'],['牙齿变白','美白','牙贴'],['眼睛干','眼睛干涩','干眼','干涩'],['头屑','去屑'],['发膜','护发素']];
  const storageKey = 'body-care-guide:bookmarks:v1';
  let saved;
  try { saved = new Set(JSON.parse(localStorage.getItem(storageKey) || '[]').filter(id => byId.has(id))); } catch { saved = new Set(); }
  let toastTimer;
  let currentRoute = {};
  let searchTimer;
  let previousSourceFocus = null;

  function node(tag, attrs = {}, ...children) {
    const n = document.createElement(tag);
    for (const [key,value] of Object.entries(attrs)) {
      if (value === undefined || value === null) continue;
      if (key === 'class') n.className = value;
      else if (key === 'text') n.textContent = value;
      else if (key.startsWith('on') && typeof value === 'function') n.addEventListener(key.slice(2), value);
      else if (key === 'value') n.value = value;
      else if (key === 'checked') n.checked = !!value;
      else n.setAttribute(key, String(value));
    }
    for (const child of children.flat()) {
      if (child === null || child === undefined || child === false) continue;
      n.append(child instanceof Node ? child : document.createTextNode(String(child)));
    }
    return n;
  }
  function icon(name) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class','icon');svg.setAttribute('aria-hidden','true');
    const use = document.createElementNS('http://www.w3.org/2000/svg','use');use.setAttribute('href', '#i-' + name);svg.append(use);return svg;
  }
  function safeUrl(value) {
    try { const u = new URL(String(value));return /^https?:$/.test(u.protocol) ? u.href : null; } catch { return null; }
  }
  function sourceNum(s) { return s.number || data.sources.indexOf(s) + 1; }
  function stripped(text) { return String(text || '').replace(/\[@[^\]]+\]|\[\d+\]/g,'').replace(/\*\*/g,'').replace(/\[([^\]]+)\]\([^)]*\)/g,'$1').replace(/^#{1,6}\s/gm,'').replace(/\s+/g,' ').trim(); }
  function inline(text, parent) {
    const re = /\[@(src-[A-Za-z0-9_-]+)\]|\[(\d+)\]|\*\*([^*]+)\*\*|\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;
    let last = 0, m;
    while ((m = re.exec(String(text)))) {
      parent.append(document.createTextNode(String(text).slice(last,m.index)));
      if (m[1] || m[2]) {
        const source = m[1] ? bySource.get(m[1]) : byNumber.get(m[2]);
        if (source) parent.append(node('button',{class:'citation',type:'button','aria-label':`查看来源 ${sourceNum(source)}`,onclick:() => showSource(source.id)},`[${sourceNum(source)}]`));
        else parent.append(document.createTextNode(m[0]));
      } else if (m[3]) { const strong = node('strong');inline(m[3],strong);parent.append(strong); }
      else { const url = safeUrl(m[5]);parent.append(url ? node('a',{href:url,target:'_blank',rel:'noopener noreferrer'},m[4]) : document.createTextNode(m[4])); }
      last = re.lastIndex;
    }
    parent.append(document.createTextNode(String(text).slice(last)));
  }
  function prose(text, extraClass='') {
    const box=node('div',{class:'prose '+extraClass});
    const paras=String(text || '').replace(/\r\n/g,'\n').split(/\n\s*\n/);
    for (const para of paras) {
      if(!para.trim())continue;
      const lines=para.trim().split('\n');
      if(lines.length>1 && /^\|/.test(lines[0]) && /^\|?\s*:?-/.test(lines[1])) {
        const table=node('table'), rows=lines.filter((_,i)=>i!==1);
        rows.forEach((line,i)=>{const tr=node('tr');line.replace(/^\||\|$/g,'').split('|').forEach(cell=>{const td=node(i===0?'th':'td');inline(cell.trim(),td);tr.append(td);});table.append(tr);});
        box.append(node('div',{class:'table-wrap'},table));continue;
      }
      if (lines.every(l=>/^[-•]\s/.test(l))) {
        const ul=node('ul');lines.forEach(line=>{const li=node('li');inline(line.replace(/^[-•]\s/,''),li);ul.append(li);});box.append(ul);continue;
      }
      const heading=para.match(/^#{1,6}\s+(.+)$/);
      if(heading){const h=node('h3');inline(heading[1],h);box.append(h);continue;}
      const p=node('p');lines.forEach((line,i)=>{if(i)p.append(node('br'));inline(line,p);});box.append(p);
    }
    return box;
  }
  function toast(message) {
    const t=document.getElementById('toast');t.textContent=message;t.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.hidden=true,3000);
  }
  function downloadText(filename, text, mime='text/plain;charset=utf-8') {
    const url=URL.createObjectURL(new Blob([text],{type:mime}));
    const a=node('a',{href:url,download:filename});document.body.append(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),2000);
  }
  function markdownExport(){
    const blocks=[manifest.book?.front_matter||''];
    for(const ch of chapters){blocks.push('# '+titleOf(ch)+' '+(ch.subtitle||''),ch.intro||'');for(const unit of ch.units||[]){blocks.push('## '+unit.title,unit.intro||'');for(const id of unit.entry_ids||[]){const e=byId.get(id);if(!e)continue;blocks.push('### '+e.ordinal+' '+e.title);for(const [key,label]of Object.entries(fieldLabels))blocks.push('**'+label+'：** '+e.fields[key]);}}}
    blocks.push(manifest.book?.back_matter||'','# 参考文献');
    for(const s of data.sources)blocks.push('['+sourceNum(s)+'] '+s.citation+' [原文]('+s.url+')');
    return blocks.filter(Boolean).join('\n\n').replace(/\[@(src-[A-Za-z0-9_-]+)\]/g,(whole,id)=>bySource.has(id)?'['+sourceNum(bySource.get(id))+']':whole)+'\n';
  }
  function downloadLink(url,title,subtitle){
    const a=node('a',{class:'download-card',href:offlineDocument&&!url.startsWith('#')?'#':url,...(url.startsWith('#')?{}:{download:''})},icon('download'),node('span',{},node('strong',{},title),node('small',{},subtitle)));
    if(offlineDocument&&!url.startsWith('#'))a.addEventListener('click',ev=>{ev.preventDefault();if(url.endsWith('guide.md'))downloadText('guide.md',markdownExport(),'text/markdown;charset=utf-8');else if(url.endsWith('guide.json'))downloadText('guide.json',JSON.stringify(data,null,2),'application/json');else downloadText('guide-offline.html','<!doctype html>\n'+document.documentElement.outerHTML,'text/html;charset=utf-8');});
    return a;
  }
  function updateSaved() {
    document.getElementById('saved-count').textContent=saved.size;
    try {localStorage.setItem(storageKey,JSON.stringify([...saved]));}catch{toast('浏览器未允许本地保存；这次收藏只能保留到关闭页面。');}
  }
  function saveButton(id, small=false) {
    return node('button',{class:'button '+(small?'small ':'')+(saved.has(id)?'saved':''),type:'button','aria-pressed':saved.has(id),onclick:()=>{
      saved.has(id)?saved.delete(id):saved.add(id);updateSaved();
      document.querySelectorAll(`[data-save="${id}"]`).forEach(b=>{b.classList.toggle('saved',saved.has(id));b.setAttribute('aria-pressed',String(saved.has(id)));b.replaceChildren(icon('save'),document.createTextNode(saved.has(id)?'已收藏':'收藏'));});
      if(currentRoute.path==='saved')render();
    },'data-save':id},icon('save'),saved.has(id)?'已收藏':'收藏');
  }
  function grades(entry) { return entry.evidence_labels || []; }
  function gradeBadges(entry) { return grades(entry).map(g=>node('span',{class:'grade '+g,title:'本条包含该等级的证据，具体限定见正文'},'证据 '+g)); }
  function titleOf(ch) { return names[ch.id] || ch.name || ch.title; }
  function chapterEntries(id) { return entries.filter(e=>e.chapter_id===id).sort((a,b)=>a.ordinal-b.ordinal); }
  function parseRoute() {
    const raw=location.hash.replace(/^#\/?/,'');const [path,search='']=raw.split('?');const bits=path.split('/').filter(Boolean);
    return {path:bits[0] || 'home',id:bits[1] || '',params:new URLSearchParams(search)};
  }
  function navigate(path,params={},replace=false) {
    const p=new URLSearchParams();for(const [k,v] of Object.entries(params))if(v)p.set(k,v);
    const hash='#/'+path+(p.size?'?'+p.toString():'');
    if(replace){history.replaceState(null,'',hash);render();}else if(location.hash===hash)render();else location.hash=hash;
  }
  function closeNav(){document.getElementById('sidebar').classList.remove('open');document.getElementById('nav-shade').hidden=true;document.getElementById('menu-toggle').setAttribute('aria-expanded','false');}
  function setActive(route) {
    document.querySelectorAll('.nav-item').forEach(a=>a.classList.toggle('active', a.dataset.nav===route.path || (route.path==='chapter'&&a.dataset.chapter===route.id) || (route.path==='entry'&&a.dataset.chapter===byId.get(route.id)?.chapter_id)));
  }
  function searchForm(value='',onSearch) {
    const input=node('input',{type:'search',value,placeholder:'搜索问题、习惯或用品，如：干眼、牙线、发膜','aria-label':'搜索护理建议'});
    const form=node('form',{class:'search-home',onsubmit:e=>{e.preventDefault();onSearch(input.value);}},icon('search'),input,node('span',{class:'search-shortcut'},'Enter ↵'));
    return form;
  }
  function heroArt(){
    const art=node('div',{class:'hero-art','aria-hidden':'true'});
    // This static illustration contains no content data or user-provided markup.
    const graphic=document.createElementNS('http://www.w3.org/2000/svg','svg');graphic.setAttribute('viewBox','0 0 160 190');graphic.setAttribute('class','head-illustration');
    graphic.innerHTML='<path d="M42 79C26 77 26 104 42 108m76-29c16-2 16 25 0 29M42 62v48c0 30 20 51 38 51s38-21 38-51V62M44 78c1-40 11-48 35-48 27 0 37 11 39 48M43 67c13-2 28-17 31-28 5 18 29 25 44 26M59 87q9-8 17 0m11 0q9-8 17 0M65 90v2m30-2v2M80 92l-4 19h8M68 124q12 7 24 0M63 151v20m34-20v20M45 185l18-14h34l18 14"/><path d="M41 61C29 13 63 9 80 16c21-12 55 8 40 48M68 132h24" stroke-opacity=".55"/><circle cx="26" cy="43" r="3" fill="currentColor" stroke="none"/><path d="M134 119v10m-5-5h10M22 137v7m-4-3h8" stroke-opacity=".5"/>';
    art.append(graphic,node('div',{class:'art-caption'},'从头开始 · 慢慢学会'),node('span',{class:'art-tag one'},'好好用眼'),node('span',{class:'art-tag two'},'读懂成分'),node('span',{class:'art-tag three'},'照顾日常'));return art;
  }
  function home(){
    const frag=document.createDocumentFragment();
    frag.append(node('section',{class:'hero'},node('div',{},node('div',{class:'eyebrow'},'五官与头部护理 · 第一篇'),node('h1',{},'从头开始，',node('br'),node('em',{},'学会照顾自己。')),node('p',{},'没人系统教过的身体护理，在这里慢慢弄明白。从每天的小习惯，到值得花的钱，每条建议都带着理由、来源和适用条件。'),node('div',{class:'hero-actions'},node('a',{class:'button primary',href:'#/read'},'打开阅读指南',icon('arrow')),node('a',{class:'button ghost',href:'#/about?section=method'},'先了解怎么读 ↗')),node('p',{class:'hero-note'},'研究修订版 · 尚未完成临床医生逐条审阅')),heroArt()));
    const stats=node('div',{class:'stats'});
    [[chapters.length,'护理部位','从五官与头部开始'],[entries.length,'行动建议','按需要挑选阅读'],[data.sources.length,'可追溯来源','效果与局限一起看'],['01','首篇内容','继续扩展到全身']].forEach(([n,t,s])=>stats.append(node('div',{class:'stat'},node('span',{class:'stat-number'},n),node('span',{class:'stat-label'},node('strong',{},t),s))));frag.append(stats);
    frag.append(node('div',{class:'section-heading'},node('div',{},node('h2',{},'今天，从哪里开始'),node('p',{},'选一个部位，顺着日常习惯、常见困扰和消费选择往下读。')),node('a',{class:'text-link',href:'#/read'},'查看全部建议',icon('arrow'))));
    frag.append(searchForm('',q=>navigate('read',{q})));
    const grid=node('div',{class:'chapter-grid'});
    chapters.forEach((ch,i)=>{const a=node('a',{class:'chapter-card',href:'#/chapter/'+ch.id,style:'--card-color:'+colors[ch.id]},node('div',{class:'chapter-card-top'},node('span',{class:'chapter-card-icon'},icon(iconNames[ch.id]||'book')),node('span',{class:'chapter-number'},String(i+1).padStart(2,'0'))),node('h3',{},titleOf(ch)),node('p',{},descriptions[ch.id]||stripped(ch.intro)),node('div',{class:'chapter-card-footer'},`${chapterEntries(ch.id).length} 条建议 · ${(ch.units||[]).length} 个单元`,icon('arrow')));grid.append(a);});
    grid.append(node('div',{class:'start-card'},node('div',{class:'mini-stack'},node('span'),node('span'),node('span')),node('div',{},node('h3',{},'不必一次全部做到'),node('p',{},'可以先改一个习惯，也可以只查一个想买的用品。收藏有用的那条，需要时再回来。'),node('a',{class:'text-link',href:'#/saved'},'看看我的收藏 ↗'))));frag.append(grid);
    frag.append(node('div',{class:'section-heading'},node('div',{},node('h2',{},'也许，你也有这些困惑'))));
    const quick=node('div',{class:'quick-row'});['眼睛干涩','美瞳','牙线','电动牙刷','防晒','发膜','掏耳朵'].forEach(q=>quick.append(node('a',{class:'chip',href:'#/read?q='+encodeURIComponent(q)},q,icon('arrow'))));frag.append(quick);
    frag.append(node('div',{class:'method-strip'},...[
      ['01','先看行动，再弄懂原理','陌生名词就近解释。先知道它是什么，再决定怎么做。'],
      ['02','把效果和适用条件一起读','研究的人群、比较对象、时间与局限，都影响结论。'],
      ['03','留住依据，允许持续纠错','查看原始来源与核查状态，让之后的修订也有迹可循。']
    ].map(([n,t,p])=>node('div',{},node('span',{class:'small-index'},n),node('h3',{},t),node('p',{},p)))));
    main.append(frag);document.title='身体护理指南 · 从头开始照顾自己';
  }
  function entryCard(e){
    return node('article',{class:'entry-card','data-entry':e.id},node('div',{class:'entry-card-meta'},node('span',{},names[e.chapter_id]||e.chapter_id),node('span',{},'· 第'+e.ordinal+'条'),...gradeBadges(e)),node('h3',{},node('a',{href:'#/entry/'+e.id},e.title)),node('p',{},stripped(e.fields.plain)),node('div',{class:'entry-card-bottom'},node('div',{class:'mini-tags'},...(e.tags||[]).map(t=>node('span',{class:'mini-tag'},t))),node('div',{class:'action-row'},saveButton(e.id,true),node('a',{class:'text-link',href:'#/entry/'+e.id},'阅读全文',icon('arrow')))));
  }
  function matchQuery(e,q){
    if(!q.trim())return true;
    const hay=[e.title,names[e.chapter_id],...Object.values(e.fields),...(e.tags||[])].join(' ').toLowerCase();
    return q.toLowerCase().trim().split(/\s+/).every(term=>{
      const group=synonymGroups.find(g=>g.includes(term));return (group||[term]).some(t=>hay.includes(t));
    });
  }
  function readList(savedOnly=false){
    const params=currentRoute.params;
    const q=params.get('q')||'',chapter=params.get('chapter')||'',grade=params.get('grade')||'',tag=params.get('tag')||'';
    main.append(node('header',{class:'page-head'},node('div',{class:'eyebrow'},savedOnly?'留给下次需要的自己':'查一条，用一条'),node('h1',{},savedOnly?'我的收藏':'查找护理建议'),node('p',{class:'page-lead'},savedOnly?'收藏只保存在当前浏览器中，不需要登录，也不会上传你的阅读记录。':'用你熟悉的词搜索。证据等级筛选表示条目包含该等级，具体用途和条件仍要读正文。')));
    const search=node('input',{type:'search',value:q,placeholder:'搜索问题、习惯或用品…','aria-label':'关键词'});
    const select=node('select',{class:'select','aria-label':'筛选部位'},node('option',{value:''},'所有部位'),...chapters.map(c=>node('option',{value:c.id},titleOf(c))));select.value=chapter;
    const gradeRow=node('div',{class:'filter-row'},node('span',{class:'filter-label'},'证据等级'));
    const tagRow=node('div',{class:'filter-row'},node('span',{class:'filter-label'},'阅读方向'));
    const resultCount=node('span',{class:'filter-count','aria-live':'polite'});
    let state={q,chapter,grade,tag};
    const list=node('div',{class:'entry-list'});
    function update(){
      const results=entries.filter(e=>(!savedOnly||saved.has(e.id))&&(!state.chapter||e.chapter_id===state.chapter)&&(!state.grade||grades(e).includes(state.grade))&&(!state.tag||(e.tags||[]).includes(state.tag))&&matchQuery(e,state.q));
      list.replaceChildren(...results.map(entryCard));resultCount.textContent=`找到 ${results.length} / ${savedOnly?saved.size:entries.length} 条`;
      if(!results.length)list.append(empty(savedOnly?'还没有符合条件的收藏':'没有找到符合条件的建议',savedOnly?'阅读时点“收藏”，就能留在这里。':'换一个更短的词，或清除筛选后再试。'));
      for(const row of [gradeRow,tagRow])row.querySelectorAll('[data-value]').forEach(b=>b.classList.toggle('active',state[b.dataset.kind]===b.dataset.value));
      const qs=new URLSearchParams();Object.entries(state).forEach(([k,v])=>{if(v)qs.set(k,v);});history.replaceState(null,'','#/'+(savedOnly?'saved':'read')+(qs.size?'?'+qs:''));
    }
    ['','A','B','C'].forEach(g=>gradeRow.append(node('button',{class:'chip',type:'button','data-kind':'grade','data-value':g,onclick:()=>{state.grade=g;update();}},g?'包含 '+g+' 级':'全部')));
    ['','习惯','消费','症状','专业服务'].forEach(t=>tagRow.append(node('button',{class:'chip',type:'button','data-kind':'tag','data-value':t,onclick:()=>{state.tag=t;update();}},t||'全部')));
    tagRow.append(resultCount);
    search.addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{state.q=search.value;update();},120);});
    select.addEventListener('change',()=>{state.chapter=select.value;update();});
    const clear=node('button',{class:'button small',type:'button',onclick:()=>{state={q:'',chapter:'',grade:'',tag:''};search.value='';select.value='';update();}},'清除筛选');
    main.append(node('section',{class:'filter-panel','aria-label':'筛选护理建议'},node('div',{class:'filter-top'},node('div',{class:'searchbox'},icon('search'),search),select,clear),gradeRow,tagRow),list);
    update();document.title=(savedOnly?'我的收藏':'查找建议')+' · 身体护理指南';
  }
  function empty(title,message){return node('div',{class:'empty-state'},icon('book'),node('h2',{},title),node('p',{},message),node('a',{class:'button small',href:'#/read'},'查看全部建议'));}
  function chapterView(id){
    const ch=chapterMap.get(id);if(!ch)return notFound();const group=chapterEntries(id),selected=currentRoute.params.get('unit')||'';
    main.append(node('header',{class:'page-head chapter-head'},node('div',{},node('div',{class:'breadcrumb'},node('a',{href:'#/'},'阅读首页'),'/',titleOf(ch)),node('h1',{},titleOf(ch)),node('p',{class:'page-lead'},ch.subtitle||descriptions[id])),node('div',{class:'big-icon'},icon(iconNames[id]||'book'))));
    if(ch.intro)main.append(prose(ch.intro,'page-lead'));
    const tabs=node('div',{class:'unit-tabs'},node('a',{class:'chip '+(!selected?'active':''),href:'#/chapter/'+id},'全部 '+group.length+' 条'));
    (ch.units||[]).forEach((u,i)=>tabs.append(node('a',{class:'chip '+(selected===u.id?'active':''),href:'#/chapter/'+id+'?unit='+u.id},`${String(i+1).padStart(2,'0')} ${u.title}`)));main.append(tabs);
    for(const u of ch.units||[]){if(selected&&selected!==u.id)continue;main.append(node('header',{class:'unit-heading'},node('h2',{},u.title),u.intro?prose(u.intro):null));const list=node('div',{class:'entry-list'});group.filter(e=>e.unit_id===u.id).forEach(e=>list.append(entryCard(e)));main.append(list);}
    if(!(ch.units||[]).length)main.append(node('div',{class:'entry-list'},...group.map(entryCard)));
    document.title=titleOf(ch)+'护理 · 身体护理指南';
  }
  async function copyLink(id){
    if(offlineDocument){toast('传播离线版时，请分享完整HTML文件。');return;}
    const url=new URL('read/'+encodeURIComponent(id)+'/',new URL('.',location.href));
    try{await navigator.clipboard.writeText(url.href);toast('已复制这条建议的链接');}
    catch{const box=node('input',{value:url.href,'aria-label':'可复制的分享链接'});main.prepend(box);box.focus();box.select();toast('已显示链接，可手动复制。');}
  }
  function entryView(id){
    const e=byId.get(id);if(!e)return notFound();const ch=chapterMap.get(e.chapter_id),u=(ch.units||[]).find(u=>u.id===e.unit_id);
    const article=node('article',{class:'article'});
    article.append(node('header',{class:'page-head'},node('div',{class:'breadcrumb'},node('a',{href:'#/'},'首页'),'/',node('a',{href:'#/chapter/'+e.chapter_id},titleOf(ch)),u?' / '+u.title:''),node('h1',{},e.title),node('div',{class:'article-meta'},node('span',{},'第 '+e.ordinal+' 条'),...gradeBadges(e),node('span',{},'资料核对 '+(e.content_checked_at||'2026-10-28')),node('span',{},'未临床签审'))));
    article.append(node('div',{class:'action-row article-actions'},saveButton(id),node('button',{class:'button small',type:'button',onclick:()=>copyLink(id)},icon('link'),'复制单条链接'),node('a',{class:'button small ghost',href:'#/chapter/'+e.chapter_id},'返回本章')));
    for(const key of ['plain','cost','benefit','evidence','sources','notes'])article.append(node('section',{class:'reading-field '+(key==='plain'?'plain-field':'')},node('h2',{},fieldLabels[key]),prose(e.fields[key])));
    const linked=node('div',{class:'reading-field'},node('h2',{},'本条引用的来源'));
    for(const sid of e.source_ids||[]){const s=bySource.get(sid);if(s)linked.append(node('p',{},node('button',{class:'text-link button ghost small',type:'button',onclick:()=>showSource(sid)},`[${sourceNum(s)}] ${sourceShortTitle(s)}`)));}article.append(linked);
    const group=chapterEntries(e.chapter_id),at=group.findIndex(x=>x.id===id),previous=group[at-1],next=group[at+1];
    article.append(node('nav',{class:'article-bottom','aria-label':'相邻条目'},previous?node('a',{href:'#/entry/'+previous.id},'← 上一条',node('strong',{},previous.title)):node('span'),next?node('a',{href:'#/entry/'+next.id},'下一条 →',node('strong',{},next.title)):node('a',{href:'#/chapter/'+e.chapter_id},'这一章读完了',node('strong',{},'返回本章目录'))));
    article.append(node('p',{class:'article-status'},'本条供理解护理选择和就诊准备。证据等级描述特定结论的把握度，不能代替个人检查或处方。'));
    main.append(article);document.title=e.title+' · 身体护理指南';
  }
  function sourceShortTitle(s){return String(s.citation||s.title||s.id).replace(/\s*\[Internet\].*$/,'').slice(0,135);}
  function supportOf(s){const a=s.support||s['支持结论']||'';return Array.isArray(a)?a.join('；'):a;}
  function limitsOf(s){return s.limitations||s['局限']||'';}
  function usesOf(id){return entries.filter(e=>(e.source_ids||[]).includes(id));}
  function showSource(id){
    const s=bySource.get(id);if(!s)return;previousSourceFocus=document.activeElement;
    const box=document.getElementById('source-dialog-body');box.replaceChildren(node('span',{class:'source-type'},s.type||'参考资料'),node('p',{class:'citation-title'},`[${sourceNum(s)}] ${s.citation}`));
    if(supportOf(s))box.append(node('h3',{},'它支持什么'),prose(supportOf(s)));
    if(limitsOf(s))box.append(node('h3',{},'使用这份证据的限制'),prose(limitsOf(s)));
    const url=safeUrl(s.url);if(url)box.append(node('a',{class:'button small',href:url,target:'_blank',rel:'noopener noreferrer'},'打开原始来源 ↗'));
    const uses=usesOf(id);box.append(node('h3',{},`哪些条目引用了它 · ${uses.length}`),node('div',{class:'source-uses'},...uses.map(e=>node('a',{href:'#/entry/'+e.id,onclick:()=>document.getElementById('source-dialog').close()},`${names[e.chapter_id]} · ${e.title}`))));
    document.getElementById('source-dialog-title').textContent='来源 '+sourceNum(s);
    const d=document.getElementById('source-dialog');if(!d.open)d.showModal();
  }
  function sourcesView(){
    main.append(node('header',{class:'page-head'},node('div',{class:'eyebrow'},'让判断可追溯'),node('h1',{},'查看证据来源'),node('p',{class:'page-lead'},'论文、专业护理资料、监管文件与产品信息各有用途。能打开一个链接，并不等于它证明了附近所有结论。')));
    const input=node('input',{type:'search','aria-label':'搜索文献、机构或题名',placeholder:'搜索文献、机构或题名，如 Cochrane、牙膏…'}),count=node('p',{class:'muted',style:'font-size:11px','aria-live':'polite'}),list=node('div',{class:'source-grid'});
    function update(){const q=input.value.toLowerCase().trim();const matches=data.sources.filter(s=>[s.citation,s.type,supportOf(s),s.url].join(' ').toLowerCase().includes(q));count.textContent=`${matches.length} 项来源 · 内容版本 ${manifest.content_version||'2026.10.28-1'}`;list.replaceChildren(...matches.map(s=>{
      let domain='';try{domain=new URL(s.url).hostname;}catch{}
      return node('article',{class:'source-card'},node('div',{class:'source-card-top'},node('span',{class:'source-number'},'['+sourceNum(s)+']'),node('span',{},s.type||'参考资料')),node('h2',{},s.citation),node('div',{class:'action-row'},node('button',{class:'button small',type:'button',onclick:()=>showSource(s.id)},'查看支持范围 · '+usesOf(s.id).length+' 条引用'),safeUrl(s.url)?node('a',{class:'source-domain',href:s.url,target:'_blank',rel:'noopener noreferrer'},domain+' ↗'):null));}));if(!matches.length)list.append(empty('没有找到这份来源','试试作者、机构或题名中的一个短词。'));}
    input.addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(update,120);});main.append(node('div',{class:'searchbox'},icon('search'),input),count,list);update();document.title='证据来源 · 身体护理指南';
  }
  function about(){
    main.append(node('header',{class:'page-head'},node('div',{class:'eyebrow'},'一份可以继续维护的指南'),node('h1',{},'项目与下载'),node('p',{class:'page-lead'},'先把五官与头部照顾好，再沿着同一套证据与编辑标准扩展到全身。读者可以直接阅读，维护者可以从结构化内容继续开发。')));
    const downloads=node('section',{class:'info-panel'},node('h2',{},'把指南带走'),node('p',{},'离线文件保存的是下载时的版本，不会自动更新。当前内容版本：'+(manifest.content_version||'2026.10.28-1')));
    const dgrid=node('div',{class:'download-grid'});
    [['downloads/guide-offline.html','离线阅读版','单个HTML · 含检索与全部正文'],['downloads/guide.md','完整正文','Markdown · 方便阅读与编辑'],['downloads/guide.json','结构化数据','JSON · 供开发与二次整理'],['#/print','打印与另存PDF','展开全文 · 使用浏览器打印']].forEach(([url,t,p])=>dgrid.append(downloadLink(url,t,p)));downloads.append(dgrid);
    const method=node('section',{class:'info-panel',id:'method'},node('h2',{},'怎样理解证据等级'),node('p',{},'A、B、C是这份指南的阅读分级，描述特定结论的依据，不是品牌评分，也不是正式GRADE评定。'),...[
      ['A','较可靠的直接人体临床依据','仍要看研究对象、实际改善幅度和风险。'],['B','有限或间接的人体资料','小样本、短随访、方法或人群差异都会限制判断。'],['C','护理规范、机理或实践建议','不等于无用。急症处理也不能因缺少随机试验被忽略。']
    ].map(([g,t,p])=>node('div',{},node('h3',{},node('span',{class:'grade '+g},g),' '+t),node('p',{},p))),node('p',{},'一条建议可能包含不同等级的判断。筛选只帮助定位，完整证据和限定在正文里。'));
    if(manifest.book?.front_matter)method.append(node('details',{},node('summary',{},'展开完整阅读导览'),prose(manifest.book.front_matter)));
    if(manifest.book?.back_matter)method.append(node('details',{},node('summary',{},'展开证据与引用说明'),prose(manifest.book.back_matter)));
    const roadmap=node('section',{class:'info-panel'},node('h2',{},'接下来，继续照顾全身'),node('div',{class:'roadmap-item done'},node('span',{},'五官与头部'),node('small',{},'研究修订 · 66条')), ...['个人卫生与私处护理','手脚与身体皮肤','肩颈、运动与日常活动','生活方式与身心状态'].map(t=>node('div',{class:'roadmap-item'},node('span',{},t),node('small',{},'规划中'))),node('p',{},'规划中的篇目还没有医学结论。扩展前先定问题清单，再查证、编辑和复核。'));
    const api=node('section',{class:'info-panel'},node('h2',{},'给维护者与开发者'),node('p',{},'内容与界面分开保存。稳定条目ID用于链接，数据接口供检索、导出或其他阅读器使用。这里提供的是只读资料，不是诊断或个体治疗接口。'),...['manifest','chapters','entries','sources'].map(x=>{const a=node('a',{class:'api-link',href:offlineDocument?'#':'api/v1/'+x+'.json',...(offlineDocument?{}:{target:'_blank',rel:'noopener'})},'api/v1/'+x+'.json '+(offlineDocument?'↓':'↗'));if(offlineDocument)a.addEventListener('click',ev=>{ev.preventDefault();const value=x==='manifest'?manifest:{schema_version:manifest.schema_version,content_version:manifest.content_version,[x]:data[x]};downloadText(x+'.json',JSON.stringify(value,null,2),'application/json');});return a;}),node('p',{},'自动检查负责字段、引用、链接与复核期限。医学结论、证据等级和临床审核状态，需要人工审查。'));
    const repo=manifest.repository_url||manifest.config?.repository_url||'';
    if(safeUrl(repo))api.append(node('a',{class:'button small',href:repo,target:'_blank',rel:'noopener noreferrer'},'在 GitHub 查看源码 ↗'),node('a',{class:'button small ghost',href:repo.replace(/\/$/,'')+'/issues/new/choose',target:'_blank',rel:'noopener noreferrer'},'报告一条问题 ↗'));
    else api.append(node('p',{},'公开仓库尚未绑定。源码中已准备贡献规范、纠错表单与自动发布配置；确认仓库后即可接入。'));
    main.append(node('div',{class:'about-grid'},node('div',{},downloads,method),node('div',{},roadmap,api)),node('div',{class:'provenance-note'},'当前为案头资料复核的研究修订稿，尚未完成临床医生逐条审阅。来源可靠性、研究质量和结论适用性分别核查；有不确定性时保留限制。产品实例不代表销量排名或成品疗效背书。本站不收集症状表单或上传阅读搜索词。'));
    document.title='项目与下载 · 身体护理指南';if(currentRoute.params.get('section')==='method')requestAnimationFrame(()=>document.getElementById('method')?.scrollIntoView());
  }
  function printView(){
    main.append(node('div',{class:'print-toolbar action-row'},node('button',{class:'button primary',type:'button',onclick:()=>window.print()},icon('download'),'打印 / 另存为 PDF'),node('a',{class:'button',href:'#/about'},'返回下载页')),node('header',{class:'page-head'},node('h1',{},'身体护理指南 · 五官与头部'),node('p',{class:'page-lead'},'内容版本 '+(manifest.content_version||'2026.10.28-1')+' · 研究修订稿，未完成临床签审。')));
    for(const ch of chapters){main.append(node('h2',{class:'print-chapter'},titleOf(ch)));for(const e of chapterEntries(ch.id)){const article=node('article',{class:'print-entry'},node('h3',{},e.ordinal+' '+e.title));for(const [key,label]of Object.entries(fieldLabels))article.append(node('div',{class:'print-field'},node('span',{class:'print-field-label'},label+'：'),prose(e.fields[key])));main.append(article);}}
    main.append(node('h2',{class:'print-chapter'},'参考文献'),...data.sources.map(s=>node('p',{style:'font-size:10px;overflow-wrap:anywhere'},`[${sourceNum(s)}] ${s.citation} ${s.url}`)));
    document.title='打印正文 · 身体护理指南';
  }
  function notFound(){main.append(empty('没有找到这个页面','条目可能已经移入归档，或链接输入有误。请从检索页查找。'));document.title='页面未找到 · 身体护理指南';}
  function render(){
    closeNav();const d=document.getElementById('source-dialog');if(d.open)d.close();currentRoute=parseRoute();main.replaceChildren();setActive(currentRoute);
    if(currentRoute.path==='home')home();else if(currentRoute.path==='read')readList();else if(currentRoute.path==='saved')readList(true);else if(currentRoute.path==='chapter')chapterView(currentRoute.id);else if(currentRoute.path==='entry')entryView(currentRoute.id);else if(currentRoute.path==='sources')sourcesView();else if(currentRoute.path==='about')about();else if(currentRoute.path==='print')printView();else notFound();
    window.scrollTo({top:0,behavior:'instant'});
  }

  // A re-exported offline document may already contain its rendered navigation.
  document.getElementById('chapter-nav').replaceChildren();
  for(const ch of chapters)document.getElementById('chapter-nav').append(node('a',{class:'nav-item',href:'#/chapter/'+ch.id,'data-chapter':ch.id},icon(iconNames[ch.id]||'book'),titleOf(ch),node('span',{class:'nav-count'},chapterEntries(ch.id).length)));
  document.getElementById('saved-count').textContent=saved.size;
  document.querySelector('.skip-link').addEventListener('click',ev=>{ev.preventDefault();main.focus();main.scrollIntoView();});
  document.getElementById('update-label').textContent='内容核对 '+String(manifest.content_checked_at||'2026-10-28').replaceAll('-','.');
  document.getElementById('menu-toggle').addEventListener('click',()=>{const open=document.getElementById('sidebar').classList.toggle('open');document.getElementById('nav-shade').hidden=!open;document.getElementById('menu-toggle').setAttribute('aria-expanded',String(open));});
  document.getElementById('nav-shade').addEventListener('click',closeNav);
  document.getElementById('sidebar').addEventListener('click',e=>{if(e.target.closest('a'))closeNav();});
  document.getElementById('source-close').addEventListener('click',()=>document.getElementById('source-dialog').close());
  document.getElementById('source-dialog').addEventListener('click',e=>{if(e.target===e.currentTarget)e.currentTarget.close();});
  document.getElementById('source-dialog').addEventListener('close',()=>{if(previousSourceFocus?.isConnected)previousSourceFocus.focus();});
  document.getElementById('theme-toggle').addEventListener('click',()=>{const dark=document.body.dataset.theme!=='dark';document.body.dataset.theme=dark?'dark':'light';try{localStorage.setItem('body-care-guide:theme',dark?'dark':'light');}catch{}document.getElementById('theme-toggle').setAttribute('aria-label',dark?'切换浅色模式':'切换深色模式');});
  try{const theme=localStorage.getItem('body-care-guide:theme');if(theme==='dark'){document.body.dataset.theme='dark';document.getElementById('theme-toggle').setAttribute('aria-label','切换浅色模式');}}catch{}
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeNav();});
  window.addEventListener('hashchange',render);
  // Read-only helpers for maintainers and browser QA; these do not infer medical advice.
  window.GuideReader = Object.freeze({version:manifest.content_version,findEntries:q=>entries.filter(e=>matchQuery(e,q)).map(e=>e.id),hasEntry:id=>byId.has(id)});
  render();
})();
