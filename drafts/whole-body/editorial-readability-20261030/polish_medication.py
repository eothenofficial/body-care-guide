"""One final readability correction, independently rechecked before release."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
 p=HERE/'body-rewrites.json';rows=json.loads(p.read_text(encoding='utf-8'))
 e=next(e for e in rows if e['id']=='nutrition-017');before=e['fields']['plain']
 after='''GLP-1（胰高血糖素样肽-1）是一种参与调节食欲和血糖的肠道激素。司美格鲁肽模拟它的作用，帮助减少饥饿感和进食量。替尔泊肽同时作用于GLP-1和葡萄糖依赖性促胰岛素多肽（GIP）的受体；玛仕度肽同时作用于GLP-1和胰高血糖素的受体。这些药不是直接把脂肪溶掉，作用靶点更多，也不自动意味着更安全。[@src-d9882eacf41f][@src-6b0e3e1da079][@src-b26bf3573369]

**想比较效果，优先看直接比较两种药的试验。** SURMOUNT-5把751名没有2型糖尿病的肥胖成年人随机分组。参加者起始平均体重113千克、BMI39.4，按研究方案逐步增加到各自最大耐受剂量。72周时，替尔泊肽组平均体重下降20.2%，司美格鲁肽组下降13.7%。研究由礼来资助，参加者知道自己使用哪种药，两组都常见胃肠道不适。这个平均结果不能直接用于体重正常者，也不保证每位中国患者、每种剂量都能达到同样效果；减得更多不等于所有方面都更安全。[@src-9d7643fe0c2e]

玛仕度肽的GLORY-1纳入中国610名超重或肥胖成年人，起始平均体重87.2千克、BMI31.1。48周时，4毫克组平均体重下降11.00%，6毫克组下降14.01%，安慰剂组增加0.30%；这项分析包含停药等情况，研究由信达资助。两项试验的人群、疗程和方案不同，不能把数字横排成“最强减重针”榜单。这里的研究剂量用于解释结果，不是个人加量处方。[@src-4028138dc4d5]

**先确认具体制剂的中国适应证，再讨论哪一种适合自己。** 中国成人BMI≥28的肥胖诊断标准，不能代替所有药品的用药门槛。下列制剂均需配合饮食和活动；符合BMI条件，也不等于已经适合使用。[@src-d9882eacf41f][@src-6b0e3e1da079][@src-b26bf3573369][@src-704851d0c5f3]

| 制剂 | 成人体重管理适应证中的初始BMI | 选择时还要看什么 |
| --- | --- | --- |
| 司美格鲁肽注射液，诺和盈 | ≥30；或≥27至<30并有至少一种相关合并症 | 不能用同成分糖尿病制剂的说明书代替；已有心血管疾病等情况，还要确认对应的获批用途 |
| 替尔泊肽注射液，穆峰达 | ≥28；或≥24并有至少一种相关合并症 | 看胃肠道耐受、病史和具体说明书，有直接比较试验也不代表人人更合适 |
| 玛仕度肽注射液，信尔美 | ≥28；或≥24并有至少一种相关合并症 | 说明书所列体重试验中，65岁及以上仅3人，不能照搬年轻人的安全结论 |

相关合并症可包括高血压、血脂异常、高血糖和阻塞性睡眠呼吸暂停等，具体范围随制剂确认。就诊时说明已有疾病、正在用的药和最在意的目标，再比较效果与耐受。已经反复呕吐、吃不够或年长体弱时，先顾营养与身体状况；现有方案有效且能耐受，不因排行榜自行换药或叠加针剂。[@src-704851d0c5f3][@src-6b0e3e1da079][@src-b26bf3573369]'''
 e['fields']['plain']=after
 p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 log=dict(id='nutrition-017',field='plain',reason='补回完整语法、GLP-1首次中文解释与研究比较的对象；不改变数字、比较方向、来源和人群。',before=before,after=after)
 (HERE/'root-final-polish.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
