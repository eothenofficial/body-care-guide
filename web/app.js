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
  const guideTitle = manifest.title || '少走弯路的人体保养指南';
  const brandTitle = document.getElementById('brand-title');
  if(guideTitle==='少走弯路的人体保养指南')brandTitle.replaceChildren(node('span',{class:'brand-prefix'},'少走弯路的'),node('span',{},'人体保养指南'));
  else brandTitle.textContent=guideTitle;
  document.getElementById('brand-link').setAttribute('aria-label',guideTitle+'首页');
  document.getElementById('footer-guide-title').textContent=guideTitle;
  const entryAliases=manifest.entry_aliases||{};
  const canonicalId=id=>Object.prototype.hasOwnProperty.call(entryAliases,id)?entryAliases[id]:id;
  const offlineDocument = location.protocol === 'file:' || /\/guide-offline\.html$/.test(location.pathname);
  const byId = new Map(entries.map(e => [e.id, e]));
  const bySource = new Map(data.sources.map(s => [s.id, s]));
  const byNumber = new Map(data.sources.map((s, i) => [String(s.number || i + 1), s]));
  const chapterMap = new Map(chapters.map(c => [c.id, c]));
  const names = {eyes:'眼睛',nose:'鼻子',lips:'嘴唇',oral:'口腔',ears:'耳朵',skin:'面部皮肤',hair:'头发'};
  const iconNames = {eyes:'eye',nose:'nose',lips:'lips',oral:'tooth',ears:'ear',skin:'skin',hair:'hair'};
  const colors = {eyes:'var(--sage)',nose:'var(--sand)',lips:'var(--rose)',oral:'var(--blue)',ears:'var(--sand)',skin:'var(--rose)',hair:'var(--sage)'};
  const descriptions = {eyes:'看清、舒服，再把镜片戴安全。',nose:'整理鼻毛，分清黑头，照顾鼻腔。',lips:'减少干裂和刺激，再选润唇用品。',oral:'牙齿、牙龈和舌面，一起照顾好。',ears:'少伸工具，控制音量，留意听力。',skin:'做好基础护理，再为具体改变花钱。',hair:'先照顾头皮，再做喜欢的发型。'};
  // New body parts are data, not a second hard-coded set of reader pages.
  for(const chapter of chapters){
    names[chapter.id]=chapter.title||chapter.name||names[chapter.id]||chapter.id;
    colors[chapter.id]=chapter.color||colors[chapter.id]||'var(--sage)';
    iconNames[chapter.id]=chapter.icon||iconNames[chapter.id]||'book';
    descriptions[chapter.id]=chapter.summary||descriptions[chapter.id]||chapter.subtitle||'';
  }
  const fieldLabels = {cost:'成本',plain:'说人话',benefit:'收益',evidence:'证据等级',sources:'来源',notes:'备注'};
  const synonymGroups = [['ok镜','角膜塑形镜'],['针眼','麦粒肿'],['水牙线','冲牙器'],['a醇','视黄醇'],['a醛','视黄醛'],['痘痘','痤疮','粉刺'],['牙齿变白','美白','牙贴'],['眼睛干','眼睛干涩','干眼','干涩'],['头屑','去屑'],['发膜','护发素']];
  const storageKey = 'body-care-guide:bookmarks:v1';
  let saved;
  try { saved = new Set(JSON.parse(localStorage.getItem(storageKey) || '[]').map(canonicalId).filter(id => byId.has(id))); } catch { saved = new Set(); }
  let toastTimer;
  let currentRoute = {};
  let searchTimer;
  let previousSourceFocus = null;
  let previousAudienceFocus = null;
  let navOpen = false;
  let navScrollY = 0;
  const mobileNavigation = window.matchMedia?.('(max-width: 760px), (max-width: 1024px) and (max-height: 500px)');
  const mobileFontKey = 'body-care-guide:mobile-font:v1';
  const mobileFontSizes = ['small','medium','large'];
  let mobileFont = 'medium';
  try{const stored=localStorage.getItem(mobileFontKey);if(mobileFontSizes.includes(stored))mobileFont=stored;}catch{}
  const ageNames = {child:'儿童（0–11岁）',teen:'青少年（12–17岁）',adult:'成人（18–64岁）',older:'老年（65岁起）'};
  let audienceState = audienceFromParams(new URLSearchParams((location.hash.split('?')[1]||'')));


  function node(tag, attrs = {}, ...children) {
    const n = document.createElement(tag);
    for (const [key,value] of Object.entries(attrs)) {
      if (value === undefined || value === null) continue;
      if (key === 'class') n.className = value;
      else if (key === 'text') n.textContent = value;
      else if (key.startsWith('on') && typeof value === 'function') n.addEventListener(key.slice(2), value);
      else if (key === 'value') n.value = value;
      else if (key === 'checked') n.checked = !!value;
      else n.setAttribute(key, key==='href' ? audienceHref(String(value)) : String(value));
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
  function safeEntryHref(value) {
    const target = String(value), match = /^#\/entry\/([a-z][a-z0-9]*(?:-[a-z0-9]+)*-\d{3})$/.exec(target);
    return match && match[0] === target && byId.has(canonicalId(match[1])) ? '#/entry/' + canonicalId(match[1]) : null;
  }
  function sourceNum(s) { return s.number || data.sources.indexOf(s) + 1; }
  function stripped(text) { return String(text || '').replace(/\[@[^\]]+\]|\[\d+\]/g,'').replace(/\*\*/g,'').replace(/\[([^\]]+)\]\([^)]*\)/g,'$1').replace(/^#{1,6}\s/gm,'').replace(/\s+/g,' ').trim(); }
  function entrySummary(e) {
    // Summaries are edited independently of the full medical argument. Older
    // editions have no summary: use one prose paragraph, never flatten a table.
    const authored=typeof e.summary==='string'&&e.summary.trim();
    const blocks=String(authored||e.fields?.plain||'').replace(/\r\n?/g,'\n').split(/\n\s*\n/);
    let text='';
    for(const block of blocks){
      const lines=block.split('\n'),proseLines=[];
      for(let i=0;i<lines.length;i++){
        const line=lines[i].trim(),next=(lines[i+1]||'').trim();
        const tableSeparator=/^\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?$/.test(next);
        if(tableSeparator||line.includes('|'))break;
        if(/^#{1,6}\s/.test(line)||/^[-•]\s/.test(line))continue;
        if(line)proseLines.push(line);
      }
      text=stripped(proseLines.join(' '));
      if(text)break;
    }
    if(!text)return '查看本条的具体做法、适用条件和证据来源。';
    const characters=Array.from(text),limit=220;
    if(characters.length<=limit)return text;
    const prefix=characters.slice(0,limit).join('');
    const sentences=[...prefix.matchAll(/[。！？.!?；;]/g)];
    const end=sentences.length?sentences[sentences.length-1].index+1:0;
    return end>=prefix.length/2?prefix.slice(0,end):prefix.trimEnd()+'…';
  }
  function inline(text, parent) {
    const re = /\[@(src-[A-Za-z0-9_-]+)\]|\[(\d+)\]|\*\*([^*]+)\*\*|\[([^\]\n]+)\]\(([^)\n]+)\)/g;
    let last = 0, m;
    while ((m = re.exec(String(text)))) {
      parent.append(document.createTextNode(String(text).slice(last,m.index)));
      if (m[1] || m[2]) {
        const source = m[1] ? bySource.get(m[1]) : byNumber.get(m[2]);
        if (source) parent.append(node('button',{class:'citation',type:'button','aria-label':`查看来源 ${sourceNum(source)}`,onclick:() => showSource(source.id)},`[${sourceNum(source)}]`));
        else parent.append(document.createTextNode(m[0]));
      } else if (m[3]) { const strong = node('strong');inline(m[3],strong);parent.append(strong); }
      else {
        const internal = safeEntryHref(m[5]), external = internal || /\s/.test(m[5]) ? null : safeUrl(m[5]);
        parent.append(internal ? node('a',{href:internal},m[4]) : external ? node('a',{href:external,target:'_blank',rel:'noopener noreferrer'},m[4]) : document.createTextNode(m[0]));
      }
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
        box.append(node('div',{class:'table-wrap',tabindex:'0',role:'region','aria-label':'可横向滚动的比较表格'},node('span',{class:'table-hint'},'左右滑动查看完整表格'),table));continue;
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
    for(const ch of chapters){blocks.push('# '+titleOf(ch)+' '+(ch.subtitle||''),ch.intro||'');for(const unit of ch.units||[]){blocks.push('## '+unit.title,unit.intro||'');for(const id of unit.entry_ids||[]){const e=byId.get(id);if(!e)continue;blocks.push('### '+e.ordinal+' '+e.title,audienceCaption(e));for(const [key,label]of Object.entries(fieldLabels))if(e.fields[key]?.trim())blocks.push('**'+label+'：** '+e.fields[key]);}}}
    blocks.push(manifest.book?.back_matter||'','# 参考文献');
    for(const s of data.sources)blocks.push('['+sourceNum(s)+'] '+s.citation+' [原文]('+s.url+')');
    return blocks.filter(Boolean).join('\n\n').replace(/\[@(src-[A-Za-z0-9_-]+)\]/g,(whole,id)=>bySource.has(id)?'['+sourceNum(bySource.get(id))+']':whole)+'\n';
  }
  function downloadLink(url,title,subtitle){
    const extension=url.endsWith('.md')?'.md':url.endsWith('.json')?'.json':'.html';
    const a=node('a',{class:'download-card',href:offlineDocument&&!url.startsWith('#')?'#':url,...(url.startsWith('#')?{}:{download:guideTitle+extension})},icon('download'),node('span',{},node('strong',{},title),node('small',{},subtitle)));
    if(offlineDocument&&!url.startsWith('#'))a.addEventListener('click',ev=>{ev.preventDefault();if(url.endsWith('guide.md'))downloadText(guideTitle+'.md',markdownExport(),'text/markdown;charset=utf-8');else if(url.endsWith('guide.json'))downloadText(guideTitle+'.json',JSON.stringify(data,null,2),'application/json');else downloadText(guideTitle+'.html','<!doctype html>\n'+document.documentElement.outerHTML,'text/html;charset=utf-8');});
    return a;
  }
  function updateSaved() {
    document.getElementById('saved-count').textContent=saved.size;
    try {localStorage.setItem(storageKey,JSON.stringify([...saved]));return true;}catch{toast('浏览器未允许本地保存；这次收藏只能保留到关闭页面。');return false;}
  }
  function parseBookmarkImport(raw){
    let value;try{value=JSON.parse(raw);}catch{throw new Error('文件不是有效的JSON。');}
    if(!value||value.kind!=='body-care-guide-bookmarks'||value.schema_version!=='1.0.0'||!Array.isArray(value.entry_ids)||value.entry_ids.length>5000||value.entry_ids.some(id=>typeof id!=='string'||!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*-\d{3}$/.test(id)))throw new Error('请选择本指南导出的收藏文件。');
    const unique=[...new Set(value.entry_ids.map(canonicalId))];return {known:unique.filter(id=>byId.has(id)),unknown:unique.filter(id=>!byId.has(id)).length};
  }
  function bookmarkTools(){
    const picker=node('input',{type:'file',accept:'.json,application/json',hidden:'','aria-label':'选择收藏JSON文件'});
    picker.addEventListener('change',async()=>{
      const file=picker.files?.[0];if(!file)return;
      try{
        if(file.size>1024*1024)throw new Error('收藏文件不能超过1MB。');
        const imported=parseBookmarkImport(await file.text()),before=saved.size;
        for(const id of imported.known)saved.add(id);const persistent=updateSaved();render();
        toast('合并了 '+(saved.size-before)+' 条新收藏'+(imported.unknown?'；跳过 '+imported.unknown+' 条本版本未收录的建议':'')+'。'+(persistent?'':'浏览器未允许本地保存，本次只能暂存；请导出备份。'));
      }catch(error){toast('未导入：'+error.message);}finally{picker.value='';}
    });
    return node('section',{'aria-label':'收藏备份与迁移'},node('div',{class:'bookmark-tools'},node('button',{class:'button small',type:'button',onclick:()=>{
      downloadText(guideTitle+'_收藏.json',JSON.stringify({kind:'body-care-guide-bookmarks',schema_version:'1.0.0',entry_ids:[...saved]},null,2),'application/json');
    }},icon('download'),'导出收藏'),node('button',{class:'button small',type:'button',onclick:()=>picker.click()},'导入收藏'),picker),node('p',{class:'bookmark-transfer-note'},'可用JSON文件备份或迁移到另一浏览器。导出全部收藏，不受当前筛选影响；文件只包含条目编号。导入会合并，不覆盖已有收藏，文件不会上传。'));
  }
  function saveButton(id, small=false) {
    return node('button',{class:'button '+(small?'small ':'')+(saved.has(id)?'saved':''),type:'button','aria-pressed':saved.has(id),onclick:()=>{
      saved.has(id)?saved.delete(id):saved.add(id);updateSaved();
      document.querySelectorAll(`[data-save="${id}"]`).forEach(b=>{b.classList.toggle('saved',saved.has(id));b.setAttribute('aria-pressed',String(saved.has(id)));b.replaceChildren(icon('save'),node('span',{},saved.has(id)?'已收藏':'收藏'));});
      if(currentRoute.path==='saved')render();
    },'data-save':id},icon('save'),node('span',{},saved.has(id)?'已收藏':'收藏'));
  }
  function grades(entry) { return entry.evidence_labels || []; }
  function gradeBadges(entry) { return grades(entry).map(g=>node('span',{class:'grade '+g,title:'本条包含该等级的证据，具体限定见正文'},'证据 '+g)); }
  function titleOf(ch) { return names[ch.id] || ch.name || ch.title; }
  function chapterEntries(id) { return entries.filter(e=>e.chapter_id===id).sort((a,b)=>a.ordinal-b.ordinal); }
  function ageGroup(age) { return age<12?'child':age<18?'teen':age<65?'adult':'older'; }
  function audienceFromParams(params) {
    const raw=params.get('age')||'',age=/^(?:0|[1-9]\d{0,2})$/.test(raw)&&Number(raw)<=120?raw:'';
    const requested=params.get('band')||'',band=['child','teen','under18','adult','older'].includes(requested)?requested:'';
    const sex=['female','male'].includes(params.get('sex'))?params.get('sex'):'';
    return {age,band:age?'':band,sex};
  }
  function audienceParams() { return Object.fromEntries(Object.entries(audienceState).filter(([,v])=>v)); }
  function hasAudienceFilter() { return !!(audienceState.age||audienceState.band||audienceState.sex); }
  function audienceHref(href) {
    if(!href.startsWith('#/'))return href;
    const [path,query='']=href.split('?'),params=new URLSearchParams(query);
    for(const key of ['age','band','sex'])params.delete(key);
    for(const [key,value]of Object.entries(audienceParams()))params.set(key,value);
    return path+(params.size?'?'+params.toString():'');
  }
  function syncAudienceNavigation() {
    // The sidebar survives main-content renders. Replace its previous audience
    // query before reusing a link, including after all audience filters clear.
    document.querySelectorAll('#sidebar a[href^="#/"]').forEach(link=>{
      link.setAttribute('href',audienceHref(link.getAttribute('href')));
    });
    for(const id of ['mobile-home-link','mobile-search-link']){
      const link=document.getElementById(id),href=link?.getAttribute('href');
      if(href)link.setAttribute('href',audienceHref(href));
    }
  }
  function audienceOf(e) {
    const a=e.audience||{};
    return {age_groups:Array.isArray(a.age_groups)&&a.age_groups.length?a.age_groups:['adult'],
      sexes:Array.isArray(a.sexes)&&a.sexes.length?a.sexes:['all'],
      scope_note:a.scope_note||'本条以成人护理为主，儿童和老年情境尚未逐条核对。',safety_pin:a.safety_pin===true};
  }
  function audienceMatches(e,filters=audienceState) {
    const a=audienceOf(e);
    const selected=filters.age!==''?[ageGroup(Number(filters.age))]:filters.band==='under18'?['child','teen']:filters.band?[filters.band]:[];
    return (!selected.length||selected.some(g=>a.age_groups.includes(g)))&&(!filters.sex||a.sexes.includes('all')||a.sexes.includes(filters.sex));
  }
  function audienceLabel() {
    const a=audienceState,parts=[];
    if(a.age!=='')parts.push(a.age+'岁 · '+ageNames[ageGroup(Number(a.age))]);
    else if(a.band)parts.push(a.band==='under18'?'18岁以下':ageNames[a.band]);
    if(a.sex)parts.push(a.sex==='female'?'女性侧重':'男性侧重');
    return parts.length?parts.join(' / '):'不限年龄与男女';
  }
  function audienceSummary(e) {
    const a=audienceOf(e),ages=a.age_groups.map(g=>ageNames[g]||g).join('、');
    const sex=a.sexes.includes('all')?'男女通用':a.sexes.map(g=>g==='female'?'女性':'男性').join('、');
    return '阅读侧重：'+ages+' · '+sex+(a.safety_pin?' · 急症提示':'');
  }
  function audienceBadges(e) { return node('p',{class:'audience-badges'},audienceSummary(e)); }
  function audienceCaption(e) {
    const a=audienceOf(e);
    return audienceSummary(e)+'。'+a.scope_note+' 年龄分组用于导览，不代表治疗资格。';
  }
  function audienceTools() {
    return node('section',{class:'audience-toolbar','aria-label':'年龄与男女阅读筛选'},node('div',{},node('strong',{},'按阅读人群选内容'),node('span',{class:'audience-current','aria-live':'polite'},audienceLabel())),node('button',{class:'button small',type:'button',onclick:showAudience},'年龄与男女筛选'),hasAudienceFilter()?node('button',{class:'text-link',type:'button',onclick:clearAudience},'清除人群筛选'):null,node('p',{},'保留所选人群的专属内容和通用建议，急症条目也遵守同一规则。年龄段用于查找；用药、孕哺及个人限制仍需读正文。'));
  }
  function clearAudience() { audienceState={age:'',band:'',sex:''};applyAudienceRoute(); }
  function applyAudienceRoute() {
    const route=parseRoute(),params=Object.fromEntries(route.params);
    for(const key of ['age','band','sex'])delete params[key];
    if(route.path==='chapter'&&params.unit){
      const ch=chapterMap.get(route.id),unit=ch?.units?.find(u=>u.id===params.unit);
      if(!unit||!unit.entry_ids.some(id=>byId.has(id)&&audienceMatches(byId.get(id))))delete params.unit;
    }
    Object.assign(params,audienceParams());
    navigate((route.path==='home'?'read':route.path+(route.id?'/'+route.id:'')),params,true);
  }
  function closeAudience() { const dialog=document.getElementById('audience-dialog');if(dialog.open)dialog.close(); }
  function showAudience() {
    closeNav();
    previousAudienceFocus=document.activeElement;
    const dialog=document.getElementById('audience-dialog'),box=document.getElementById('audience-dialog-body');
    const age=node('input',{id:'audience-age',type:'number',min:'0',max:'120',step:'1',inputmode:'numeric',value:audienceState.age,placeholder:'例如 16','aria-describedby':'audience-error audience-scope'});
    const band=node('select',{id:'audience-band',class:'select'},node('option',{value:''},'不限年龄'),node('option',{value:'under18'},'18岁以下'),...Object.entries(ageNames).map(([value,label])=>node('option',{value},label)));band.value=audienceState.band;
    const sex=node('select',{id:'audience-sex',class:'select'},node('option',{value:''},'男女通用与全部内容'),node('option',{value:'female'},'女性侧重'),node('option',{value:'male'},'男性侧重'));sex.value=audienceState.sex;
    const error=node('p',{id:'audience-error',class:'audience-error',role:'alert'});
    age.addEventListener('input',()=>{if(age.value!=='')band.value='';error.textContent='';});
    band.addEventListener('change',()=>{if(band.value)age.value='';error.textContent='';});
    const form=node('form',{class:'audience-form',novalidate:'',onsubmit:event=>{
      event.preventDefault();const raw=age.value.trim();
      if(raw!==''&&(!/^(?:0|[1-9]\d{0,2})$/.test(raw)||Number(raw)>120)){error.textContent='请输入0至120之间的整数年龄，或清空后选择年龄段。';age.setAttribute('aria-invalid','true');age.focus();return;}
      age.removeAttribute('aria-invalid');audienceState={age:raw,band:raw?'':band.value,sex:sex.value};closeAudience();applyAudienceRoute();
    }},node('p',{id:'audience-scope',class:'audience-scope'},'可以输入年龄，也可以只选年龄段。这里只筛选已整理的阅读侧重，不判断你是否适合某种药物、手术或产品；信息不上传，也不保存到账号。'),node('label',{for:'audience-age'},'具体年龄（可选）'),age,node('label',{for:'audience-band'},'或选择年龄段'),band,node('label',{for:'audience-sex'},'男女阅读侧重'),sex,error,node('div',{class:'audience-actions'},node('button',{class:'button primary',type:'submit'},'应用筛选'),node('button',{class:'button ghost',type:'button',onclick:()=>{age.value='';band.value='';sex.value='';error.textContent='';}},'重置选项')),
      node('p',{class:'audience-scope'},'选女性时隐藏男性专属建议，选男性时隐藏女性专属建议；双方都需要的内容继续保留。急症也按年龄和男女标签筛选。筛选不会判断你的器官、孕哺状态或治疗资格。'));
    box.replaceChildren(form);dialog.showModal();document.body.classList.toggle('audience-open',true);age.focus();
  }
  function parseRoute() {
    const raw=location.hash.replace(/^#\/?/,'');const [path,search='']=raw.split('?');const bits=path.split('/').filter(Boolean);
    return {path:bits[0] || 'home',id:bits[1] || '',params:new URLSearchParams(search)};
  }
  function navigate(path,params={},replace=false) {
    const p=new URLSearchParams();for(const [k,v] of Object.entries({...audienceParams(),...params}))if(v)p.set(k,v);
    const hash='#/'+path+(p.size?'?'+p.toString():'');
    if(replace){history.replaceState(null,'',hash);render();}else if(location.hash===hash)render();else location.hash=hash;
  }
  function setNavOpen(open, restoreFocus=false){
    const mobile=!!mobileNavigation?.matches,sidebar=document.getElementById('sidebar'),wasOpen=navOpen;
    navOpen=mobile&&open;
    if(navOpen&&!wasOpen){navScrollY=window.scrollY||0;document.body.style?.setProperty('--nav-scroll-top',-navScrollY+'px');}
    sidebar.classList.toggle('open',navOpen);sidebar.inert=mobile&&!navOpen;
    if(mobile&&!navOpen)sidebar.setAttribute('aria-hidden','true');else sidebar.removeAttribute('aria-hidden');
    document.body.classList.toggle('nav-open',navOpen);
    main.inert=navOpen;const footer=document.querySelector('.site-footer');if(footer)footer.inert=navOpen;
    for(const background of [main,footer].filter(Boolean)){if(navOpen){background.setAttribute('inert','');background.setAttribute('aria-hidden','true');}else{background.removeAttribute('inert');background.removeAttribute('aria-hidden');}}
    document.getElementById('nav-shade').hidden=!navOpen;
    const toggle=document.getElementById('menu-toggle');
    toggle.setAttribute('aria-expanded',String(navOpen));toggle.setAttribute('aria-label',navOpen?'收起目录':'打开目录');
    toggle.replaceChildren(icon(navOpen?'close':'menu'),node('span',{},navOpen?'收起':'目录'));
    if(wasOpen&&!navOpen){document.body.style?.removeProperty('--nav-scroll-top');window.scrollTo({top:navScrollY,behavior:'instant'});if(!mobile)main.focus({preventScroll:true});else if(restoreFocus)toggle.focus({preventScroll:true});}
    if(navOpen&&!wasOpen){const focusClose=()=>{if(navOpen)document.getElementById('nav-close').focus({preventScroll:true});};if(window.requestAnimationFrame)window.requestAnimationFrame(focusClose);else focusClose();}
  }
  function closeNav(restoreFocus=false){setNavOpen(false,restoreFocus);}
  function setActive(route) {
    document.querySelectorAll('.nav-item').forEach(a=>a.classList.toggle('active', a.dataset.nav===route.path || (route.path==='chapter'&&a.dataset.chapter===route.id) || (route.path==='entry'&&a.dataset.chapter===byId.get(route.id)?.chapter_id)));
    for(const [id,active]of [['mobile-home-link',route.path==='home'],['mobile-search-link',route.path==='read']]){
      const link=document.getElementById(id);if(active)link?.setAttribute('aria-current','page');else link?.removeAttribute('aria-current');
    }
  }
  function searchForm(value='',onSearch) {
    const input=node('input',{type:'search',value,placeholder:'搜索症状、习惯或用品','aria-label':'搜索护理建议'});
    const form=node('form',{class:'search-home',onsubmit:e=>{e.preventDefault();onSearch(input.value);}},icon('search'),input,node('span',{class:'search-shortcut'},'Enter ↵'));
    return form;
  }
  function home(){
    const frag=document.createDocumentFragment();
    const hc=manifest.home_content||{};
    frag.append(node('section',{class:'hero'},
      node('div',{class:'hero-copy'},node('div',{class:'eyebrow'},guideTitle),
        node('h1',{},hc.headline||'从头到脚，',node('br'),node('em',{},hc.headline_end||'学会照顾自己。')),
        ...String(hc.lead||'从日常不适、护理习惯和用品选择开始，找到适合自己的做法。').split(/\n\s*\n/).map(paragraph=>node('p',{class:'hero-description'},paragraph)),
        node('div',{class:'hero-actions'},node('a',{class:'button primary',href:'#/read'},'查找我的问题',icon('arrow')),node('a',{class:'button ghost',href:'#/about?section=method'},'了解阅读方法',icon('arrow'))),
        node('p',{class:'hero-note'},hc.note||'按需选读，不必把护理变成一张任务清单。')),
      node('figure',{class:'hero-portrait','aria-hidden':'true'},node('img',{src:'assets/home-portrait-abstract.png',alt:'',width:300,height:360,decoding:'async'}))));
    const stats=node('div',{class:'stats'});
    [[chapters.length,'内容专题','按部位与生活场景查找'],[entries.length,'行动建议','按需要挑选阅读'],[data.sources.length,'可追溯来源','效果与局限一起看'],['随需','阅读方式','从你关心的问题开始']].forEach(([n,t,s])=>stats.append(node('div',{class:'stat'},node('span',{class:'stat-number'},n),node('span',{class:'stat-label'},node('strong',{},t),s))));frag.append(stats);
    frag.append(node('div',{class:'section-heading'},node('div',{},node('h2',{},'今天，从哪里开始'),node('p',{},'选一个部位，顺着日常习惯、常见困扰和消费选择往下读。')),node('a',{class:'text-link',href:'#/read'},'查看全部建议',icon('arrow'))));
    frag.append(searchForm('',q=>navigate('read',{q})));
    const positions=bodyPositionMap();if(positions)frag.append(positions);
    const grid=node('div',{class:'chapter-grid'});
    (positions?[]:chapters).forEach((ch,i)=>{const visible=chapterEntries(ch.id).filter(e=>audienceMatches(e));if(!visible.length)return;const a=node('a',{class:'chapter-card',href:'#/chapter/'+ch.id,style:'--card-color:'+colors[ch.id]},node('div',{class:'chapter-card-top'},node('span',{class:'chapter-card-icon'},icon(iconNames[ch.id]||'book')),node('span',{class:'chapter-number'},String(i+1).padStart(2,'0'))),node('h3',{},titleOf(ch)),node('p',{},descriptions[ch.id]||stripped(ch.intro)),node('div',{class:'chapter-card-footer'},`${visible.length} 条建议 · ${(ch.units||[]).filter(u=>visible.some(e=>e.unit_id===u.id)).length} 个单元`,icon('arrow')));grid.append(a);});
    grid.append(node('div',{class:'start-card'},node('div',{class:'mini-stack'},node('span'),node('span'),node('span')),node('div',{},node('h3',{},'不必一次全部做到'),node('p',{},'可以先改一个习惯，也可以只查一个想买的用品。收藏有用的那条，需要时再回来。'),node('a',{class:'text-link',href:'#/saved'},'看看我的收藏',icon('arrow')))));frag.append(grid);
    frag.append(node('div',{class:'section-heading'},node('div',{},node('h2',{},'也许，你也有这些困惑'))));
    const examples=Array.isArray(manifest.search_examples)&&manifest.search_examples.length?manifest.search_examples:['眼睛干涩','美瞳','牙线','电动牙刷','防晒','发膜','掏耳朵'];
    const quick=node('div',{class:'quick-row'});examples.forEach(q=>quick.append(node('a',{class:'chip',href:'#/read?q='+encodeURIComponent(q)},q,icon('arrow'))));frag.append(quick);
    frag.append(node('div',{class:'method-strip'},...[
      ['01','先看行动，再弄懂原理','陌生名词就近解释。先知道它是什么，再决定怎么做。'],
      ['02','把效果和适用条件一起读','研究的人群、比较对象、时间与局限，都影响结论。'],
      ['03','留住依据，允许持续纠错','查看原始来源与核查状态，让之后的修订也有迹可循。']
    ].map(([n,t,p])=>node('div',{},node('span',{class:'small-index'},n),node('h3',{},t),node('p',{},p)))));
    main.append(frag);document.title=guideTitle+' · 从头到脚，学会照顾自己';
  }
  function bodyPositionMap(){
    if(!Array.isArray(manifest.body_layout)||!manifest.body_layout.length)return null;
    const section=node('section',{class:'body-position-map','aria-label':'按身体位置查找篇目'},node('h2',{},'按身体位置找篇目'),node('p',{},'先选身体区域，再选具体部位；睡眠、饮食、运动和疲劳等生活基础放在末尾。'));
    manifest.body_layout.forEach((part,index)=>{
      const links=(part.chapters||[]).filter(ch=>chapterMap.has(ch.id)&&chapterEntries(ch.id).some(e=>audienceMatches(e))).map(ch=>node('a',{class:'chip',href:'#/chapter/'+ch.id},icon(iconNames[ch.id]||'book'),ch.title||titleOf(chapterMap.get(ch.id))));
      if(!links.length&&hasAudienceFilter())return;
      section.append(node('div',{class:'body-position-row'},node('span',{class:'position-index'},String(index+1).padStart(2,'0')),node('div',{},node('h3',{},part.title),node('p',{},part.description||''),node('div',{class:'position-links'},...links,links.length?null:node('span',{class:'position-pending'},'内容准备中')))));
    });
    return section;
  }
  function entryCard(e){
    return node('article',{class:'entry-card','data-entry':e.id},node('div',{class:'entry-card-meta'},node('span',{},names[e.chapter_id]||e.chapter_id),node('span',{},'· 第'+e.ordinal+'条'),...gradeBadges(e)),node('h3',{},node('a',{href:'#/entry/'+e.id},e.title)),node('p',{class:'entry-summary'},entrySummary(e)),audienceBadges(e),node('div',{class:'entry-card-bottom'},node('div',{class:'mini-tags'},...(e.tags||[]).map(t=>node('span',{class:'mini-tag'},t))),node('div',{class:'action-row'},saveButton(e.id,true),node('a',{class:'text-link',href:'#/entry/'+e.id},'阅读全文',icon('arrow')))));
  }
  function matchQuery(e,q){
    if(!q.trim())return true;
    const hay=[e.title,e.summary,...(e.search_aliases||[]),names[e.chapter_id],...Object.values(e.fields),...(e.tags||[])].join(' ').toLowerCase();
    return q.toLowerCase().trim().split(/\s+/).every(term=>{
      const group=synonymGroups.find(g=>g.includes(term));return (group||[term]).some(t=>hay.includes(t));
    });
  }
  function readList(savedOnly=false){
    const params=currentRoute.params;
    const q=params.get('q')||'',chapter=params.get('chapter')||'',grade=params.get('grade')||'',tag=params.get('tag')||'';
    main.append(node('header',{class:'page-head'},node('div',{class:'eyebrow'},savedOnly?'留给下次需要的自己':'查一条，用一条'),node('h1',{},savedOnly?'我的收藏':'查找护理建议'),node('p',{class:'page-lead'},savedOnly?'收藏只保存在当前浏览器中，不需要登录，也不会上传你的阅读记录。':'用你熟悉的词搜索。证据等级筛选表示条目包含该等级，具体用途和条件仍要读正文。')));
    if(savedOnly)main.append(bookmarkTools());
    const search=node('input',{type:'search',value:q,placeholder:'搜索问题、习惯或用品…','aria-label':'关键词'});
    const select=node('select',{class:'select','aria-label':'筛选部位'},node('option',{value:''},'所有部位'),...chapters.map(c=>node('option',{value:c.id},titleOf(c))));select.value=chapter;
    const gradeRow=node('div',{class:'filter-row'},node('span',{class:'filter-label'},'证据等级'));
    const tagRow=node('div',{class:'filter-row'},node('span',{class:'filter-label'},'阅读方向'));
    const resultCount=node('span',{class:'filter-count','aria-live':'polite'});
    let state={q,chapter,grade,tag,...audienceParams()};
    const list=node('div',{class:'entry-list'});
    function update(){
      const selectedChapters=manifest.chapter_aliases?.[state.chapter]?.chapter_ids||[state.chapter];
      const results=entries.filter(e=>(!savedOnly||saved.has(e.id))&&(!state.chapter||selectedChapters.includes(e.chapter_id))&&(!state.grade||grades(e).includes(state.grade))&&(!state.tag||(e.tags||[]).includes(state.tag))&&matchQuery(e,state.q)&&audienceMatches(e));
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
    const clear=node('button',{class:'button small',type:'button',onclick:()=>{audienceState={age:'',band:'',sex:''};navigate(savedOnly?'saved':'read',{},true);}},'清除筛选');
    main.append(audienceTools(),node('section',{class:'filter-panel','aria-label':'筛选护理建议'},node('div',{class:'filter-top'},node('div',{class:'searchbox'},icon('search'),search),select,clear),gradeRow,tagRow),list);
    update();document.title=(savedOnly?'我的收藏':'查找建议')+' · '+guideTitle;
  }
  function empty(title,message){return node('div',{class:'empty-state'},icon('book'),node('h2',{},title),node('p',{},message),node('a',{class:'button small',href:'#/read'},'查看全部建议'));}
  function chapterView(id){
    if(manifest.chapter_aliases?.[id]&&currentRoute.params.get('part')!=='1')return chapterGroupView(manifest.chapter_aliases[id]);
    const ch=chapterMap.get(id);if(!ch)return notFound();const group=chapterEntries(id),filtered=group.filter(e=>audienceMatches(e)),requested=currentRoute.params.get('unit')||'',selected=(ch.units||[]).some(u=>u.id===requested&&filtered.some(e=>e.unit_id===u.id))?requested:'';
    main.append(node('header',{class:'page-head chapter-head'},node('div',{},node('div',{class:'breadcrumb'},node('a',{href:'#/'},'阅读首页'),'/',titleOf(ch)),node('h1',{},titleOf(ch)),node('p',{class:'page-lead'},ch.subtitle||descriptions[id])),node('div',{class:'big-icon'},icon(iconNames[id]||'book'))));
    if(ch.intro&&(!hasAudienceFilter()||filtered.length===group.length))main.append(prose(ch.intro,'page-lead'));
    main.append(audienceTools(),node('p',{class:'audience-result','aria-live':'polite'},'本章匹配 '+filtered.length+' / '+group.length+' 条'));
    const tabs=node('div',{class:'unit-tabs'},node('a',{class:'chip '+(!selected?'active':''),href:'#/chapter/'+id},'全部 '+filtered.length+' 条'));
    (ch.units||[]).filter(u=>filtered.some(e=>e.unit_id===u.id)).forEach((u,i)=>tabs.append(node('a',{class:'chip '+(selected===u.id?'active':''),href:'#/chapter/'+id+'?unit='+u.id},`${String(i+1).padStart(2,'0')} ${u.title}`)));main.append(tabs);
    for(const u of ch.units||[]){if(selected&&selected!==u.id)continue;const visible=filtered.filter(e=>e.unit_id===u.id);if(!visible.length)continue;const wholeUnit=visible.length===group.filter(e=>e.unit_id===u.id).length;main.append(node('header',{class:'unit-heading'},node('h2',{},u.title),u.intro&&wholeUnit?prose(u.intro):null));const list=node('div',{class:'entry-list'});visible.forEach(e=>list.append(entryCard(e)));main.append(list);}
    if(!(ch.units||[]).length)main.append(node('div',{class:'entry-list'},...filtered.map(entryCard)));
    if(!filtered.some(e=>!selected||e.unit_id===selected))main.append(node('div',{class:'empty-state'},icon('book'),node('h2',{},'本章该年龄或人群内容尚未系统整理'),node('p',{},'未收录不表示某种做法适合该年龄。可以清除人群筛选，继续查看全章。'),node('button',{class:'button small',type:'button',onclick:clearAudience},'清除人群筛选，查看全章')));
    document.title=titleOf(ch)+' · '+guideTitle;
  }
  function chapterGroupView(group){
    main.append(node('header',{class:'page-head'},node('h1',{},group.title),node('p',{class:'page-lead'},'选择具体部位，继续查找相关的问题与用品。')),audienceTools());
    for(const id of group.chapter_ids){
      const ch=chapterMap.get(id),visible=chapterEntries(id).filter(e=>audienceMatches(e));if(!ch||!visible.length)continue;
      main.append(node('section',{class:'info-panel'},node('h2',{},icon(iconNames[id]||'book'),' ',node('a',{href:'#/chapter/'+id+(id===currentRoute.id?'?part=1':'')},titleOf(ch))),node('p',{},ch.subtitle||ch.summary||''),node('div',{class:'entry-list'},...visible.map(entryCard))));
    }
    document.title=group.title+' · '+guideTitle;
  }
  async function copyLink(id){
    if(offlineDocument){toast('传播离线版时，请分享完整HTML文件。');return;}
    const url=new URL('read/'+encodeURIComponent(id)+'/',new URL('.',location.href));
    try{await navigator.clipboard.writeText(url.href);toast('已复制这条建议的链接');}
    catch{
      document.getElementById('share-panel')?.remove();
      const box=node('input',{id:'share-url',class:'share-url',type:'url',readonly:'',value:url.href,'aria-label':'可复制的分享链接'});
      const panel=node('section',{id:'share-panel',class:'share-panel',role:'region','aria-label':'手动复制分享链接'},
        node('div',{class:'share-panel-head'},node('strong',{},'长按下方链接，选择复制'),node('button',{id:'share-close',class:'icon-button',type:'button','aria-label':'关闭分享链接',onclick:()=>{panel.remove();document.getElementById('copy-entry-link')?.focus();}},icon('close'))),box);
      const actions=document.querySelector('.article-actions');if(actions?.after)actions.after(panel);else main.append(panel);
      box.focus();box.select();toast('自动复制未成功，可长按链接手动复制。');
    }
  }
  function entryView(id){
    const e=byId.get(id);if(!e)return notFound();const ch=chapterMap.get(e.chapter_id),u=(ch.units||[]).find(u=>u.id===e.unit_id);
    if(hasAudienceFilter()&&!audienceMatches(e)){
      main.append(node('header',{class:'page-head'},node('h1',{},'这条建议不在当前筛选范围内'),node('p',{class:'page-lead'},'当前选择：'+audienceLabel()+'。本条的阅读侧重不同，已隐藏标题和正文。')),audienceTools(),node('a',{class:'button',href:'#/chapter/'+e.chapter_id},'查看本章符合条件的建议'));
      document.title='筛选范围提示 · '+guideTitle;return;
    }
    const article=node('article',{class:'article'});
    article.append(node('header',{class:'page-head'},node('div',{class:'breadcrumb'},node('a',{href:'#/'},'首页'),'/',node('a',{href:'#/chapter/'+e.chapter_id},titleOf(ch)),u?' / '+u.title:''),node('h1',{},e.title),node('div',{class:'article-meta'},node('span',{},'第 '+e.ordinal+' 条'),...gradeBadges(e),node('span',{},'资料核对 '+(e.content_checked_at||'2026-10-28')))));
    article.append(node('div',{class:'action-row article-actions'},saveButton(id),node('button',{id:'copy-entry-link',class:'button small',type:'button','aria-label':'复制这条建议的链接',onclick:()=>copyLink(id)},icon('link'),node('span',{class:'copy-full-label'},'复制单条链接'),node('span',{class:'copy-mobile-label'},'复制链接')),node('a',{class:'button small ghost',href:'#/chapter/'+e.chapter_id},'返回本章')));
    const scope=audienceOf(e);article.append(node('aside',{class:'audience-detail'},audienceBadges(e),node('p',{},scope.scope_note),hasAudienceFilter()?node('p',{},'当前阅读筛选：'+audienceLabel()+(audienceMatches(e)?'。':'。本条的阅读侧重不同，以下完整正文仍保留供了解。')):null,node('button',{class:'text-link',type:'button',onclick:showAudience},'调整年龄与男女筛选')));
    for(const key of ['plain','cost','benefit','evidence','sources','notes'])if(e.fields[key]?.trim())article.append(node('section',{class:'reading-field '+(key==='plain'?'plain-field':'')},node('h2',{},fieldLabels[key]),prose(e.fields[key])));
    const linked=node('div',{class:'reading-field'},node('h2',{},'本条引用的来源'));
    for(const sid of e.source_ids||[]){const s=bySource.get(sid);if(s)linked.append(node('p',{},node('button',{class:'text-link button ghost small',type:'button',onclick:()=>showSource(sid)},`[${sourceNum(s)}] ${sourceShortTitle(s)}`)));}article.append(linked);
    const group=chapterEntries(e.chapter_id).filter(item=>audienceMatches(item)),at=group.findIndex(x=>x.id===id),previous=group[at-1],next=group[at+1];
    article.append(node('nav',{class:'article-bottom','aria-label':'相邻条目'},previous?node('a',{href:'#/entry/'+previous.id},'← 上一条',node('strong',{},previous.title)):node('span'),next?node('a',{href:'#/entry/'+next.id},'下一条 →',node('strong',{},next.title)):node('a',{href:'#/chapter/'+e.chapter_id},'这一章读完了',node('strong',{},'返回本章目录'))));
    article.append(node('p',{class:'article-status'},'本条供理解护理选择和就诊准备。证据等级描述特定结论的把握度，不能代替个人检查或处方。'));
    main.append(article);document.title=e.title+' · '+guideTitle;
  }
  function sourceShortTitle(s){return String(s.citation||s.title||s.id).replace(/\s*\[Internet\].*$/,'').slice(0,135);}
  function supportOf(s){const a=s.support||s['支持结论']||'';return Array.isArray(a)?a.join('；'):a;}
  function limitsOf(s){return s.limitations||s['局限']||'';}
  function usesOf(id){return entries.filter(e=>audienceMatches(e)&&(e.source_ids||[]).includes(id));}
  function visibleSources(){
    if(!hasAudienceFilter())return data.sources;
    const used=new Set(entries.filter(e=>audienceMatches(e)).flatMap(e=>e.source_ids||[]));return data.sources.filter(s=>used.has(s.id));
  }
  function showSource(id){
    const s=bySource.get(id);if(!s)return;previousSourceFocus=document.activeElement;
    const box=document.getElementById('source-dialog-body');box.replaceChildren(node('span',{class:'source-type'},s.type||'参考资料'),node('p',{class:'citation-title'},`[${sourceNum(s)}] ${s.citation}`));
    if(supportOf(s))box.append(node('h3',{},'它支持什么'),prose(supportOf(s)));
    if(limitsOf(s))box.append(node('h3',{},'使用这份证据的限制'),prose(limitsOf(s)));
    if(s.reading_depth)box.append(node('h3',{},'原文核读范围'),prose(s.reading_depth));
    if(s.funding_disclosure)box.append(node('h3',{},'资金与利益披露'),prose(s.funding_disclosure));
    const url=safeUrl(s.url);if(url)box.append(node('a',{class:'button small',href:url,target:'_blank',rel:'noopener noreferrer'},'打开原始来源',icon('external')));
    const uses=usesOf(id);box.append(node('h3',{},`哪些条目引用了它 · ${uses.length}`),node('div',{class:'source-uses'},...uses.map(e=>node('a',{href:'#/entry/'+e.id,onclick:()=>document.getElementById('source-dialog').close()},`${names[e.chapter_id]} · ${e.title}`))));
    if(JSON.stringify(manifest.home_content||{}).includes('[@'+id+']'))box.append(node('p',{},'首页导览也引用了这份资料。'),node('a',{class:'text-link',href:'#/',onclick:()=>document.getElementById('source-dialog').close()},'返回首页导览'));
    document.getElementById('source-dialog-title').textContent='来源 '+sourceNum(s);
    const d=document.getElementById('source-dialog');if(!d.open)d.showModal();
  }
  function sourcesView(){
    main.append(node('header',{class:'page-head'},node('div',{class:'eyebrow'},'让判断可追溯'),node('h1',{},'查看证据来源'),node('p',{class:'page-lead'},'论文、专业护理资料、监管文件与产品信息各有用途。能打开一个链接，并不等于它证明了附近所有结论。')));
    const input=node('input',{type:'search','aria-label':'搜索文献、机构或题名',placeholder:'搜索文献、机构或题名，如 Cochrane、牙膏…'}),count=node('p',{class:'muted',style:'font-size:11px','aria-live':'polite'}),list=node('div',{class:'source-grid'});
    function update(){const q=input.value.toLowerCase().trim();const matches=visibleSources().filter(s=>[s.citation,s.type,supportOf(s),s.url].join(' ').toLowerCase().includes(q));count.textContent=`${matches.length} 项来源 · 内容版本 ${manifest.content_version||'2026.10.28-1'}`;list.replaceChildren(...matches.map(s=>{
      let domain='';try{domain=new URL(s.url).hostname;}catch{}
      return node('article',{class:'source-card'},node('div',{class:'source-card-top'},node('span',{class:'source-number'},'['+sourceNum(s)+']'),node('span',{},s.type||'参考资料')),node('h2',{},s.citation),node('div',{class:'action-row'},node('button',{class:'button small',type:'button',onclick:()=>showSource(s.id)},'查看支持范围 · '+usesOf(s.id).length+' 条引用'),safeUrl(s.url)?node('a',{class:'source-domain',href:s.url,target:'_blank',rel:'noopener noreferrer'},domain,icon('external')):null));}));if(!matches.length)list.append(empty('没有找到这份来源','试试作者、机构或题名中的一个短词。'));}
    input.addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(update,120);});main.append(node('div',{class:'searchbox'},icon('search'),input),count,list);update();document.title='证据来源 · '+guideTitle;
  }
  function about(){
    main.append(node('header',{class:'page-head'},node('div',{class:'eyebrow'},'阅读、保存与追溯依据'),node('h1',{},'项目与下载'),node('p',{class:'page-lead'},'按身体部位、遇到的症状或想买的用品查找建议。这里可以保存完整指南、了解引用方式和阅读方法。')));
    const downloads=node('section',{class:'info-panel'},node('h2',{},'把指南带走'),node('p',{},'以下下载均包含整本内容，不受当前筛选影响；打印页按当前筛选展开。离线文件不会自动更新。内容版本：'+(manifest.content_version||'2026.10.28-1')));
    const dgrid=node('div',{class:'download-grid'});
    [['downloads/guide-offline.html','离线阅读版','单个HTML · 含检索与全部正文'],['downloads/guide.md','完整正文','Markdown · 方便阅读与编辑'],['downloads/guide.json','结构化数据','JSON · 供开发与二次整理'],['#/print','打印与另存PDF','展开全文 · 使用浏览器打印']].forEach(([url,t,p])=>dgrid.append(downloadLink(url,t,p)));downloads.append(dgrid);
    const method=node('section',{class:'info-panel',id:'method'},node('h2',{},'怎样理解证据等级'),node('p',{},'A、B、C是这份指南的阅读分级，描述特定结论的依据，不是品牌评分，也不是正式GRADE评定。'),...[
      ['A','较可靠的直接人体临床依据','仍要看研究对象、实际改善幅度和风险。'],['B','有限或间接的人体资料','小样本、短随访、方法或人群差异都会限制判断。'],['C','护理规范、机理或实践建议','不等于无用。急症处理也不能因缺少随机试验被忽略。']
    ].map(([g,t,p])=>node('div',{},node('h3',{},node('span',{class:'grade '+g},g),' '+t),node('p',{},p))),node('p',{},'一条建议可能包含不同等级的判断。筛选只帮助定位，完整证据和限定在正文里。'));
    if(manifest.book?.front_matter)method.append(node('details',{},node('summary',{},'展开完整阅读导览'),prose(manifest.book.front_matter)));
    if(manifest.book?.back_matter)method.append(node('details',{},node('summary',{},'展开证据与引用说明'),prose(manifest.book.back_matter)));
    const roadmap=node('section',{class:'info-panel'},node('h2',{},'按部位继续阅读'),...chapters.filter(ch=>chapterEntries(ch.id).some(e=>audienceMatches(e))).map(ch=>node('a',{class:'roadmap-item done',href:'#/chapter/'+ch.id},icon(iconNames[ch.id]||'book'),node('span',{},titleOf(ch)),node('small',{},chapterEntries(ch.id).filter(e=>audienceMatches(e)).length+' 条匹配建议'))));
    const developer=node('section',{class:'info-panel developer-panel'},node('h2',{},'开发者：Eothen Tsang'),node('a',{class:'developer-profile',href:'https://github.com/eothenofficial',target:'_blank',rel:'noopener noreferrer'},'GitHub · eothenofficial',icon('external')),node('p',{},'欢迎共同维护这份指南，提出建议、补充资料或指出错误，一起把它做得更好。'));
    main.append(node('div',{class:'about-grid'},node('div',{},downloads,method),node('div',{},roadmap,developer)),node('div',{class:'provenance-note'},'本指南提供有来源的健康科普，尚未经过临床医生逐条审核，不能代替个人检查、诊断或处方。产品示例不代表品牌背书。有不确定性时，正文保留限制和分流条件。本站不上传搜索词或阅读记录。'));
    document.title='项目与下载 · '+guideTitle;if(currentRoute.params.get('section')==='method')requestAnimationFrame(()=>document.getElementById('method')?.scrollIntoView());
  }
  function printView(){
    main.append(node('div',{class:'print-toolbar action-row'},node('button',{class:'button primary',type:'button',onclick:()=>window.print()},icon('download'),'打印 / 另存为 PDF'),node('a',{class:'button',href:'#/about'},'返回下载页')),node('header',{class:'page-head'},node('h1',{},guideTitle),node('p',{class:'page-lead'},'内容版本 '+(manifest.content_version||'2026.10.28-1')+' · '+audienceLabel())));
    for(const ch of chapters){const visible=chapterEntries(ch.id).filter(e=>audienceMatches(e));if(!visible.length)continue;main.append(node('h2',{class:'print-chapter'},titleOf(ch)));for(const e of visible){const article=node('article',{class:'print-entry'},node('h3',{},e.ordinal+' '+e.title),node('p',{class:'print-audience'},audienceCaption(e)));for(const [key,label]of Object.entries(fieldLabels))if(e.fields[key]?.trim())article.append(node('div',{class:'print-field'},node('span',{class:'print-field-label'},label+'：'),prose(e.fields[key])));main.append(article);}}
    main.append(node('h2',{class:'print-chapter'},'参考文献'),...visibleSources().map(s=>node('p',{style:'font-size:10px;overflow-wrap:anywhere'},`[${sourceNum(s)}] ${s.citation} ${s.url}`)));
    document.title='打印正文 · '+guideTitle;
  }
  function notFound(){main.append(empty('没有找到这个页面','条目可能已经移入归档，或链接输入有误。请从检索页查找。'));document.title='页面未找到 · '+guideTitle;}
  function render(){
    closeNav();const d=document.getElementById('source-dialog');if(d.open)d.close();currentRoute=parseRoute();
    if(currentRoute.path==='entry'&&entryAliases[currentRoute.id]){currentRoute.id=canonicalId(currentRoute.id);const query=currentRoute.params.toString();history.replaceState(null,'','#/entry/'+currentRoute.id+(query?'?'+query:''));}
    audienceState=audienceFromParams(currentRoute.params);renderChapterNavigation();syncAudienceNavigation();
    const audienceToggle=document.getElementById('audience-toggle'),fullAudienceLabel=hasAudienceFilter()?'人群：'+audienceLabel():'年龄与男女';
    audienceToggle.replaceChildren(node('span',{class:'audience-desktop-label'},fullAudienceLabel),node('span',{class:'audience-mobile-label'},icon('filter'),node('span',{},hasAudienceFilter()?'已筛选':'筛选')));
    audienceToggle.setAttribute('aria-label','按年龄与男女筛选，'+fullAudienceLabel);audienceToggle.setAttribute('title',fullAudienceLabel);
    main.replaceChildren();setActive(currentRoute);
    if(currentRoute.path==='home')home();else if(currentRoute.path==='read')readList();else if(currentRoute.path==='saved')readList(true);else if(currentRoute.path==='chapter')chapterView(currentRoute.id);else if(currentRoute.path==='entry')entryView(currentRoute.id);else if(currentRoute.path==='sources')sourcesView();else if(currentRoute.path==='about')about();else if(currentRoute.path==='print')printView();else notFound();
    window.scrollTo({top:0,behavior:'instant'});
    updateTopButton();
  }

  // A re-exported offline document may already contain its rendered navigation.
  function renderChapterNavigation(){
    const nav=document.getElementById('chapter-nav');nav.replaceChildren();let lastGroup='';
    for(const ch of chapters){
      const visible=chapterEntries(ch.id).filter(e=>audienceMatches(e));if(!visible.length)continue;
      if(ch.body_group&&ch.body_group!==lastGroup){nav.append(node('div',{class:'nav-label body-group-label'},ch.body_group));lastGroup=ch.body_group;}
      nav.append(node('a',{class:'nav-item',href:'#/chapter/'+ch.id,'data-chapter':ch.id},icon(iconNames[ch.id]||'book'),titleOf(ch),node('span',{class:'nav-count'},visible.length)));
    }
  }
  renderChapterNavigation();
  document.getElementById('saved-count').textContent=saved.size;
  document.querySelector('.skip-link').addEventListener('click',ev=>{ev.preventDefault();main.focus();main.scrollIntoView();});
  document.getElementById('update-label').textContent='内容核对 '+String(manifest.content_checked_at||'2026-10-28').replaceAll('-','.');
  document.getElementById('menu-toggle').addEventListener('click',()=>setNavOpen(!navOpen));
  document.getElementById('nav-close').addEventListener('click',()=>closeNav(true));
  document.getElementById('nav-shade').addEventListener('click',()=>closeNav(true));
  document.getElementById('sidebar').addEventListener('click',e=>{if(e.target.closest('a'))closeNav();});
  for(const id of ['mobile-home-link','mobile-search-link'])document.getElementById(id)?.addEventListener('click',event=>{
    closeNav();if(event.currentTarget.getAttribute('href')===location.hash){event.preventDefault();render();}
  });
  document.getElementById('source-close').addEventListener('click',()=>document.getElementById('source-dialog').close());
  document.getElementById('source-dialog').addEventListener('click',e=>{if(e.target===e.currentTarget)e.currentTarget.close();});
  document.getElementById('source-dialog').addEventListener('close',()=>{if(previousSourceFocus?.isConnected)previousSourceFocus.focus();});
  document.getElementById('audience-toggle').addEventListener('click',showAudience);
  document.getElementById('audience-close').addEventListener('click',closeAudience);
  document.getElementById('audience-dialog').addEventListener('click',event=>{if(event.target===event.currentTarget)closeAudience();});
  document.getElementById('audience-dialog').addEventListener('close',()=>{document.body.classList.toggle('audience-open',false);if(previousAudienceFocus?.isConnected)previousAudienceFocus.focus();});
  function syncThemeControls(){const dark=document.body.dataset.theme==='dark',label=dark?'切换浅色模式':'切换深色模式';document.getElementById('theme-toggle').setAttribute('aria-label',label);const mobile=document.getElementById('mobile-theme-toggle');mobile.replaceChildren(icon('sun'),node('span',{},dark?'浅色':'深色'));mobile.setAttribute('aria-label',label);mobile.setAttribute('title',label);}
  function toggleTheme(){const dark=document.body.dataset.theme!=='dark';document.body.dataset.theme=dark?'dark':'light';try{localStorage.setItem('body-care-guide:theme',dark?'dark':'light');}catch{}syncThemeControls();}
  document.getElementById('theme-toggle').addEventListener('click',toggleTheme);
  document.getElementById('mobile-theme-toggle').addEventListener('click',toggleTheme);
  try{if(localStorage.getItem('body-care-guide:theme')==='dark')document.body.dataset.theme='dark';}catch{}
  syncThemeControls();
  function syncMobileFont(){document.body.setAttribute('data-mobile-font',mobileFont);for(const size of mobileFontSizes)document.getElementById('mobile-font-'+size)?.setAttribute('aria-pressed',String(size===mobileFont));}
  for(const size of mobileFontSizes)document.getElementById('mobile-font-'+size)?.addEventListener('click',()=>{
    mobileFont=size;syncMobileFont();try{localStorage.setItem(mobileFontKey,size);}catch{toast('字号已调整，当前浏览器无法保存，下次需重新选择。');}
  });
  syncMobileFont();
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'){closeNav(true);closeAudience();}
    if(e.key==='Tab'&&navOpen){
      const controls=[...document.querySelectorAll('.topbar a[href], .topbar button, #sidebar a[href], #sidebar button')].filter(el=>!el.hidden&&!el.disabled&&(!el.getClientRects||el.getClientRects().length));
      const first=controls[0],last=controls[controls.length-1];
      if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}
    }
  });
  mobileNavigation?.addEventListener?.('change',()=>closeNav());
  window.addEventListener('hashchange',render);
  function updateTopButton(){document.getElementById('back-to-top').hidden=(window.scrollY||0)<480;}
  window.addEventListener('scroll',updateTopButton,{passive:true});
  document.getElementById('back-to-top').addEventListener('click',()=>{
    const reduce=window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
    main.focus({preventScroll:true});window.scrollTo({top:0,behavior:reduce?'instant':'smooth'});
  });
  // Read-only helpers for maintainers and browser QA; these do not infer medical advice.
  window.GuideReader = Object.freeze({version:manifest.content_version,findEntries:q=>entries.filter(e=>matchQuery(e,q)).map(e=>e.id),hasEntry:id=>byId.has(canonicalId(id)),filterAudience:filters=>entries.filter(e=>audienceMatches(e,audienceFromParams(new URLSearchParams(filters)))).map(e=>e.id)});
  render();
})();
