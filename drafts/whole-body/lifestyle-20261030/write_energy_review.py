"""Independent source-to-claim review of the root-authored energy additions."""
import json
import hashlib
from pathlib import Path

p=Path(__file__).resolve().parent
names=['energy-entries.json','energy-sources.json']
inputs={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names}
entries=json.loads((p/names[0]).read_text(encoding='utf-8-sig'))
sources=json.loads((p/names[1]).read_text(encoding='utf-8-sig'))
assert len(entries)==2 and len(sources)==2
assert '肌痛性脑脊髓炎/慢性疲劳综合征（ME/CFS）' in entries[1]['fields']['plain']
result={
 'checked_at':'2026-10-30',
 'reviewer':'independent nutrition research agent; not a clinician sign-off',
 'clinical_review_status':'not_clinically_reviewed',
 'scope':'独立核查两条energy新增条目的原机构正文、结论推导、动作与急症边界；不重新评审全站或接管作者职责。',
 'input_sha256':inputs,
 'decision':'no_blocking_findings',
 'blocking_findings':[],
 'checks':[
  {'entry_id':'energy-001','source_url':'https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much',
   'reading_depth':'已实际打开FDA完整网页，核来源合计、每份/品牌差异、自然来源、400mg、敏感人群、能量饮料、低咖、浓缩粉、逐步减量和过量表现相关全部段落。',
   'support':'400mg写成多数成人的参考而非目标/个人保证，未复制美国标签法规至中国；对孕哺/备孕、药物和未成年保留条件。浓缩粉不以厨房勺配制、低咖非零、习惯性摄入渐减均与正文一致。',
   'acute_check':'胸痛、晕厥与严重不适引导急症并联胸痛分流，没有以咖啡因耐受或减量代替急救。',
   'limitation':'FDA页面不是困倦驾驶的性能试验；“咖啡因不能证明可安全驾车”保留为保守行动边界，不宣称已测出个体驾驶安全。未取得可靠正文更新日，引用只列访问日。'},
  {'entry_id':'energy-002','source_url':'https://www.cdc.gov/me-cfs/management/index.html',
   'reading_depth':'已实际打开CDC完整网页，核PEM、12–48小时的典型迟发/数日到数周恢复、活动日记、任务拆分、活动与休息分配及不同于健康人的运动安排相关全部段落。',
   'support':'把轻微身体/脑力活动后的反复延迟成组加重作为就医线索，没有凭疲劳确诊ME/CFS；不写pacing能治愈，也不要求所有人长期卧床或统一固定活动上限。ME/CFS首次已展开定义。',
   'acute_check':'突然胸痛、明显气短或晕厥明确先急救，活动日记不能延迟分流。',
   'limitation':'CDC面向ME/CFS者的患者指导不能直接证明所有未确诊疲劳者的治疗效果，正文只用于识别/评估前不过度强推。2024-05-10核为页内日期，不采用资源卡片日期冒充更新。'}
 ],
 'population_and_metadata':'两条为adult/older、sexes all；正文未向儿童套成人咖啡因额度或用成人疲劳条目开儿童训练处方。未发现性别互斥或safety_pin绕过逻辑；本次不测试网页实现。',
 'nonblocking_followup':'没有必须在合并前修改的项。所需ME/CFS定义已由根作者在被审版本加入。'
}
(p/'energy-independent-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('energy independent review: no blocking findings',inputs)
