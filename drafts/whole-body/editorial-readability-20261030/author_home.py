"""Reader-facing introduction; body and mind interact, neither explains everything."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sources=[dict(id='HOME-NIMH',citation='National Institute of Mental Health. Depression [Internet]. 2024 [cited 2026 Oct 30]. Available from: https://www.nimh.nih.gov/health/publications/depression',url='https://www.nimh.nih.gov/health/publications/depression',type='公共研究机构患者教育',support='抑郁涉及生物、心理和环境等因素；部分疾病或药物可引起相似症状，持续症状需评估；不以生活习惯自查代替治疗。',limitations='不证明所有情绪、注意力或疲劳都由激素/身体疾病导致；不要求先排完全部躯体疾病才能接受心理帮助。美国求助电话、药品许可和治疗方案未移植。',reading_depth='首次网页抓取超时；正常打开官网提供PDF链接后重定向至同官网完整正文，实读定义、症状、诊断及自护相关段和页尾Revised 2024。未声称重审其所有底层试验。',funding_disclosure='美国公共研究机构患者教育，页面未单列专项研究资助。',content_checked_at='2026-10-30')]
content=dict(
    audience='面向各年龄与所有性别 · 为自己查，也为家人查',
    headline='每天都在用身体，',headline_end='也该学会照顾它。',
    lead='眼睛干了，该买哪种眼药水？牙龈总出血，还能继续等吗？护肤品、保健品和减重针，哪些真有用，哪些只是宣传好听？从你遇到的问题开始，弄清原因、选择和下一步。',
    note='读懂一个问题，改好一个习惯，少一次盲目花钱。按需查阅就能开始。',
    why_title='身体是你做所有事情的底子，照顾它值得排在前面',
    why='我们会记得给车做保养，却常把自己的不舒服一直往后放。能睡好、吃得下、自在活动，才有余力学习、工作、陪伴家人和享受生活。照顾身体，值得在忙碌的日程里占一个位置。\n\n累、烦躁或注意力不集中时，先回头看一眼：最近是不是睡少了、漏了饭、很久没喝水，或者一坐就是半天？能补上的先补上，也可以在身体允许时出去短暂走走。**如果疲劳持续、原因不明，或已经影响日常生活，就需要评估，而不是继续硬撑。** [疲劳与就医线索](#/entry/basics-003)里有更具体的判断。[@HOME-FATIGUE]\n\n**身体和情绪会彼此影响，但没有一种原因能解释所有不舒服。** 激素变化、一些躯体疾病或药物可能影响情绪；抑郁也会影响睡眠、进食和精力。持续低落、兴趣下降或生活明显受影响时，应[及时寻求帮助](#/entry/basics-008)，身体与心理问题可以一起评估。不要把“补觉、多喝水”当作所有问题的答案，也不必把不适归咎于自己不够自律。[@HOME-NIMH]',
    decisions=[dict(title='不舒服时，知道先做什么',text='从干眼、掉发、口腔溃疡到便秘和私密不适，分清可以先自护的情况、需要检查的线索和应立即求助的信号。'),dict(title='买东西前，知道钱花在哪里',text='把药品、护肤品、保健品和美容项目放回具体用途：对谁有效、改善什么、证据多强、有什么风险。按需要选择，不替宣传买单。'),dict(title='平时没症状，也能少踩坑',text='把清洁、饮食、睡眠和运动做得更合适，也辨别揉眼、掏耳、舔唇等老习惯。用少数有依据的做法，代替越来越长的保养清单。')],
    reader_guide='**有困扰，先查问题。** 搜索症状、习惯或产品，先读标题和梗概；点进去再看它是什么、证据说明什么、具体怎么做。急症条目把求助动作放在最前面。\n\n**为自己或家人查，先选人群。** 儿童近视、成年正畸、老年缺牙、不同性别的私密护理，各有入口。选择年龄和男女侧重，能减少无关内容；孕哺、疾病与用药限制仍要读正文。面向全年龄，不代表同一做法适用于所有人。\n\n**想核依据，就点正文里的引用。** 来源详情保留研究对象、支持范围和局限；没有可靠费用依据时不编价格。字号和行距可在“阅读设置”调整，有用的建议可收藏，并导出备份。\n\n这是一份用于理解护理选择、改善日常习惯和准备就医的参考。医学内容尚未经过临床医生逐条签审，不能替代个人检查、诊断和处方。')
if __name__=='__main__':
    for name,value in [('home-content',content),('home-sources',sources)]:
        (HERE/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
