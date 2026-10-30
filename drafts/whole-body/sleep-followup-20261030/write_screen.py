"""Authored sleep scenarios; evidence read at its actual accessible depth."""
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent

def source(identifier,citation,url,kind,support,limitations,reading,funding,doi=None,reviewed=None):
    result=dict(id=identifier,citation=citation,url=url,type=kind,support=support,limitations=limitations,
                reading_depth=reading,funding_disclosure=funding,content_checked_at='2026-10-30')
    if doi:result.update(doi=doi,doi_url='https://doi.org/'+doi)
    if reviewed:result['reviewed_at']=reviewed
    return result

sources=[
source('SLS-S01',
    'National Heart, Lung, and Blood Institute. Sleep deprivation and deficiency: healthy sleep habits [Internet]. 2022 Mar 24 [cited 2026 Oct 30]. Available from: https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits',
    'https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits','官方生活与睡眠指导',
    '睡前留安静时间、减少明亮人工光、适合的卧室环境；一小时为实用生活安排。',
    '没有证明人人必须在第60分钟关机，不能把一般习惯调整当慢性失眠完整治疗；运动时点的笼统表述另核专门研究。',
    '实际读Healthy Sleep Habits正文及轮班小节，核真实更新2022-03-24；只采用光线、安静时间与环境相关建议。',
    '机构患者教育，未见该页独立专项资助声明。',reviewed='2022-03-24'),
source('SLS-S02',
    'National Health Service. How to fall asleep faster and sleep better [Internet]. [cited 2026 Oct 30]. Available from: https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/how-to-fall-asleep-faster-and-sleep-better/',
    'https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/how-to-fall-asleep-faster-and-sleep-better/','公共医疗机构患者指导',
    '睡前收尾、应对担忧、把次日待办写下，时钟放视线外；不强迫入睡，不能睡时离床，困倦后返回。',
    '没有为每种放松活动给出独立疗效估计；其中约20分钟离床是患者操作参考，不能要求盯钟执行。',
    '实际读六项建议全部文字，采用作息、收尾、担忧、环境及不强迫入睡段；未采用页面视频或测验，没有把本站不存在的资源写进正文。页面未确认更新日，题录只记访问日。',
    '机构患者教育，未见该页独立专项资助声明。'),
source('SLS-S03',
    'Chang AM, Aeschbach D, Duffy JF, Czeisler CA. Evening use of light-emitting eReaders negatively affects sleep, circadian timing, and next-morning alertness. Proc Natl Acad Sci U S A. 2015;112(4):1232-1237. doi:10.1073/pnas.1418490112.',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC4313820/','随机交叉实验',
    '12名健康年轻成人在实验条件下连续五晚睡前约四小时使用最亮iPad，与纸书相比部分睡眠、节律和次晨清醒度指标有差异，支持晚间自发光设备可能影响睡眠。',
    '小样本、固定作息和较长最大亮度暴露；不是手机短看几分钟试验，不证明所有屏幕都同样影响，也不能分离全部光谱与照度效应。正式卷期2015，在线2014，不能混拼年份。',
    '实际核PMC作者/题名/正式卷期/DOI、摘要、相关结果、方法中人数/四小时/亮度条件及资助和利益披露；未审原始个体数据及全部补充文件。',
    'NIH及相关研究中心、NASA等支持；Czeisler披露多家药企顾问/研究等关系及2012–2013年Apple、Microsoft股权，不能称完全无商业关系。',
    doi='10.1073/pnas.1418490112'),
source('SLS-S04',
    'Duraccio KM, Zaugg KK, Blackburn RC, Jensen CD. Does iPhone night shift mitigate negative effects of smartphone use on sleep outcomes in emerging adults? Sleep Health. 2021;7(4):478-484. doi:10.1016/j.sleh.2021.03.005.',
    'https://pubmed.ncbi.nlm.nih.gov/33867308/','随机对照试验',
    '167名18–24岁成人随机分三组七晚，睡前一小时手机夜间模式开、关或不用手机；总体睡眠结局未检出组间差异，不支持夜间模式可保证改善睡眠。',
    '只一周、大学生且用腕式活动计；事后按睡眠时长分层属于探索，不当作预设主要结果；无统计差异不等于三种行为严格等效。',
    '实际读PubMed完整题录、摘要及利益声明；原刊全文未取得，不声称审过原始方法全文或全部资助。',
    'PubMed利益声明为作者无利益冲突；全文具体资助未核，不能据此称无资助。',
    doi='10.1016/j.sleh.2021.03.005'),
source('SLS-S05',
    'Singh S, Keller PR, Busija L, McMillan P, Makrai E, Lawrenson JG, et al. Blue-light filtering spectacle lenses for visual performance, sleep, and macular health in adults. Cochrane Database Syst Rev. 2023;8(8):CD013244. doi:10.1002/14651858.CD013244.pub2.',
    'https://pubmed.ncbi.nlm.nih.gov/37593770/','系统综述',
    '成人试验中睡眠结局六RCT共148人，结果不一致、很低确定性，无法确认滤蓝光镜片改善睡眠；不能以生理机理代替产品疗效。',
    '检索截至2022-03-22，2023发表；研究人群与镜片不同，不能归纳所有滤镜、所有色深或特定疾病个体。睡眠证据不确定不是证明无效。',
    '实际读Cochrane官方摘要全部结果与结论，另核PubMed题录、DOI与利益声明；未声称重审所有纳入试验全文。',
    'Downie及Singh参与一项纳入试验，未参与该试验偏倚评估/数据提取；Downie披露无关眼病研究的Alcon/Coopervision资助；Lawrenson和Hull有专业组织稿酬。',
    doi='10.1002/14651858.CD013244.pub2'),
source('SLS-S06',
    'Cuddihy LJ, Grandner MA, Nowakowski S. Implementation of stimulus control and sleep restriction therapy for insomnia: standard definitions and best practices. J Behav Cogn Ther. 2026;36(2):100542. doi:10.1016/j.jbct.2025.100542.',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC12356610/','专业实施评论',
    '解释刺激控制的条件联系目标，反对反复看钟；以明显清醒、烦躁、努力入睡作为起身线索，困倦后返回；不是每到15或20分钟都机械出床。',
    '实施评论而非新随机试验；临床操作读取PMC公开作者手稿，正式卷期另核原刊。不能由此开无监督睡眠限制处方或保证今晚见效；DOI中的2025不是正式卷期年份。',
    '实际读PMC作者稿刺激控制相关操作/时点/离床活动/返回段、限制疗法区别、结论与利益披露；另直接核Elsevier自有EM-consulte正式页的三作者、DOI及2026年5月36卷2期文章100542。正式订阅全文未读，未审所引全部试验。',
    'NIH项目支持；Grandner披露药企、可穿戴和补充品企业顾问及其他关系；三位作者有Elsevier版税。',
    doi='10.1016/j.jbct.2025.100542'),
source('SLS-S07',
    'Edinger JD, Arnedt JT, Bertisch SM, Carney CE, Harrington JJ, Lichstein KL, et al. Behavioral and psychological treatments for chronic insomnia disorder in adults: an American Academy of Sleep Medicine clinical practice guideline. J Clin Sleep Med. 2021;17(2):255-262. doi:10.5664/jcsm.8986.',
    'https://pubmed.ncbi.nlm.nih.gov/33164742/','专业学会临床指南',
    '成人慢性失眠多组分CBT-I强推荐；单独刺激控制为有条件推荐；行动不便、跌倒风险或使用镇静催眠药需调整离床方法，不能把睡眠限制套给高风险个体。',
    '单独刺激控制证据质量低，不能由推荐名气当高确定性；治疗人群为成人慢性失眠，不是每次短暂清醒都需治疗。',
    '实际阅读PMC推荐表、刺激控制与睡眠限制推荐/依据/安全段、CBT-I总体路径及利益披露，核题录DOI；非所有试验逐篇全文审核。',
    'AASM资助，部分作者有Merck、Philips/Respironics、设备厂及其他相关研究/顾问关系，已核披露。',
    doi='10.5664/jcsm.8986'),
source('SLS-S08',
    'He JW, Tu ZH, Xiao L, Su T, Tang YX. Effect of restricting bedtime mobile phone use on sleep, arousal, mood, and working memory: a randomized pilot trial. PLoS One. 2020;15(2):e0228756. doi:10.1371/journal.pone.0228756.',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC7010281/','随机先导试验',
    '38名原有睡前用手机习惯、睡眠质量差的大学生，四周睡前30分钟停手机方案改善部分自报睡眠与睡前唤醒，支持可尝试行为调整。',
    '小样本、未盲、睡眠为日记与量表，干预还含提醒/监督；不能证明30分钟为最佳阈值、单独蓝光原因或保证所有人改善。',
    '实际读PMC题录、方法/筛选/干预监督、睡眠及唤醒结果表、作者限制、利益及资助段；未重新分析附件个体数据。',
    '中国国家自然科学基金及解放军心理卫生应用研究项目支持，作者声明无竞争利益；作者称资助方不参与研究决策。',
    doi='10.1371/journal.pone.0228756'),
]

def entry(identifier,title,summary,plain,benefit,evidence,source_ids,scope):
    return dict(id=identifier,chapter_id='sleep',title=title,summary=summary,
                fields=dict(cost='',plain=plain,benefit=benefit,evidence=evidence,
                            sources='；'.join('[@'+sid+']' for sid in source_ids),notes=''),
                audience=dict(age_groups=['adult','older'],sexes=['all'],scope_note=scope,safety_pin=False),
                content_checked_at='2026-10-30',clinical_review_status='not_clinically_reviewed')

entries=[
entry('sleep-011','睡前先给工作收尾、放下手机，别把夜间模式当助眠保证',
      '睡前越刷越清醒，先给自己留一段不被消息、游戏和待办追着跑的收尾时间。可以从睡前30至60分钟减少屏幕和明亮灯光开始，再看是否更容易按时睡；这不是精确的生理截止线。夜间模式只改部分光线，不能替代减少使用时间；也不必强迫自己情绪完全平静才能上床。',
      '**先把睡前最后一段时间从手机和工作里腾出来。** 可以从计划睡觉前30–60分钟开始：结束容易越看越久的内容，把待办和担心的事写下来，关掉不必要的提醒，再选轻松阅读或安静音频。目标是给睡眠留空间，不是要求你把情绪压到“零波动”；未能完全放松，也不代表今晚一定睡不好。[@SLS-S01][@SLS-S02]\n\n30分钟或一小时都是可试的安排，不是人人相同的医学分界。38名睡眠较差大学生的小试验中，睡前30分钟停手机、持续四周后，部分自报睡眠与睡前清醒兴奋感改善；样本小且有监督，不能保证照做就有效。若总在关机后又开回去，可把充电位置移出伸手就拿到的范围，同时保留必要联络。[@SLS-S08]\n\n别把问题全归给蓝光。蓝光是可见光中波长较短的一部分；屏幕发光可能影响夜晚节律，但亮度、使用时长和内容同样需要考虑；把屏幕调暖，并没有停止聊天、追剧或占用睡觉时间。实验室曾发现，连续几晚睡前约四小时用最大亮度平板会影响部分睡眠和节律指标；这不等于看一眼手机也有同样影响。必须临时使用时，尽量缩短、降低刺眼亮度，结束后放下。[@SLS-S03][@SLS-S01]\n\n**不必为了睡眠先买防蓝光眼镜。** 一项167名年轻成人、七夜的试验中，手机夜间模式并未带来总体睡眠改善；Cochrane综述对滤蓝光镜片的睡眠效果仍无法下定论。它们不应成为继续长时间刷屏的理由，也不能替代[持续失眠的评估与治疗](#/entry/sleep-002)。[@SLS-S04][@SLS-S05]',
      '减少睡眠被拖延和临睡前持续处理事务的机会；调整是否适合自己，以实际睡眠及白天状态判断。',
      'B，停手机与夜间模式有有限人体试验，条件和结果不同；滤蓝光镜片改善睡眠仍不确定。安静收尾及光线安排为C，30–60分钟不是已验证的最佳统一阈值。',
      ['SLS-S01','SLS-S02','SLS-S08','SLS-S03','SLS-S04','SLS-S05'],
      '成人与老年生活习惯入口；手机原始试验多为年轻成人，不把其效果大小推给所有年龄，反复失眠另有治疗路径。'),
entry('sleep-014','躺着越等越烦就换个地方安静待一会儿，别盯钟逼自己睡着',
      '短暂醒来很常见，躺着舒服时不必一醒就起床；但如果越来越清醒、烦躁，开始反复计算还能睡几小时，可以先离床，做一点安静的事，困了再回来。不用设20分钟倒计时，也别把起床当惩罚。反复失眠者可在治疗中使用这种方法；夜间走动容易跌倒或用了安眠药时，要先调整安全方案。',
      '**舒服地躺着休息，不必因为还醒着就立刻起床；如果越躺越清醒、越努力越烦，可以先离开床。** 把钟面转开，去安全的地方坐一会儿，留足防跌倒的照明，看看轻松的纸书或听一段安静内容，等困倦再回床。别改成加班、激烈运动或刷到停不下来的内容。[@SLS-S02][@SLS-S06][@SLS-S07]\n\n不用给自己设“20分钟必须睡着”的考核，也不必反复看钟确认何时离床。刺激控制是把床重新和睡眠联系起来的方法：减少在床上长时间清醒、懊恼和努力入睡；并不是保证起床一次，回来就立刻睡着。疲劳和困倦也不同，不必只因觉得累就提早很久上床等待。[@SLS-S06][@SLS-S07]\n\n如果这种情况反复影响白天，转到[失眠评估与CBT-I](#/entry/sleep-002)，由受训人员把方法和作息一起安排。不要自行把“离床”加码为整夜不睡或大幅压缩睡眠。行动不便、夜间易跌倒，或已经用了镇静催眠药的人，先与治疗者调整做法，不在黑暗中勉强走动。[@SLS-S07]',
      '减少床与清醒烦躁的联系，给反复失眠者提供比一直硬等更明确的应对方式；效果通常需要持续调整。',
      'B，成人慢性失眠的单独刺激控制获AASM有条件推荐，原始证据质量有限；具体操作与防跌倒为C。它不等于完整CBT-I，也不是每次夜醒都要执行的规则。',
      ['SLS-S02','SLS-S06','SLS-S07'],
      '以成人与老年反复入睡困难或夜醒后难再睡为主；跌倒风险、行动不便或用镇静药时需调整，不能据本文自行做睡眠限制疗法。')
]

audit=dict(checked_at='2026-10-30',entries=2,sources=len(sources),clinical_review_status='not_clinically_reviewed',
    actual_read_scope='已读本项目全书SOP核心写作/证据/引用/生活基础段、用户原写作SOP全文，以及既有8条睡眠条目与相关来源；新研究实际深度见各source.reading_depth。',
    editorial_decisions=[
        '书目校正：SLS-S06初稿沿用PubMed在线先发记录；独立打开Elsevier自有EM-consulte正式页 https://www.em-consulte.com/article/1809190/implementation-of-stimulus-control-and-sleep-restr 核三作者、DOI及Vol36 No2 Article100542 mai2026，现用2026;36(2):100542。保留DOI中的2025，临床正文不变；PMC稿和正式付费全文读取范围分开。',
        'sleep-011回答收尾、情绪刺激、30分钟与蓝光/产品，sleep-014回答当晚清醒烦躁的具体动作；后者链接既有CBT-I条目，不复制完整治疗。',
        '普通生理光照效应、屏幕行为时长、内容参与与成品滤蓝光效果不互相替代。',
        '38人中国30min试验有自报阳性；167人夜间模式试验总体无差。并列支持条件性尝试，不隐藏阴性或用亚组反转总体。',
        'Cochrane2023检索截至2022，睡眠结局6RCT/148人、很低确定性；不以无明确证据说成已证无效。',
        '刺激控制和睡眠限制分开。夜间易跌倒、行动不便、镇静药使用的安全调整直接放正文；不机械盯15/20分钟。',
        '只给成人/老年入口；年轻成人手机试验不自动证实老年同样效果，也不外推儿童。',
        '没有使用正文不存在的视频/图片，也未把NHS来源页自带资源写成本站资源。'],
    additional_primary_screening=[
        dict(url='https://pubmed.ncbi.nlm.nih.gov/41341515/',doi='10.3389/fneur.2025.1699303',
             finding='2025系统综述仅3交叉RCT49人、客观睡眠各项置信区间宽；读出版商相关方法/限制/声明与PubMed完整摘要。',
             disposition='不作为主要推荐升级依据：样本仍小、检索至2024，不能据新发表宣称已解决Cochrane不确定性，也不把其偏乐观结论写成已证明有效。'),
        dict(url='https://pubmed.ncbi.nlm.nih.gov/39366085/',doi='10.1016/j.sleep.2024.09.034',
             finding='2024实验20名12–14岁，睡前45min社交媒体/手机读书/纸书未检出睡眠或唤醒差异。实际读PubMed完整摘要/题录/利益披露。',
             disposition='避免写成所有社交内容必然令人兴奋或必然伤睡眠；未以成人条目套儿童。'),
        dict(url='https://pubmed.ncbi.nlm.nih.gov/42008244/',
             finding='2026青少年节律联合干预的PubMed搜索条目显示睡眠安排+晨间亮光+晚间滤蓝光联合，不是单独眼镜对照。',
             disposition='只做范围筛选、未读正文，不用于证明普通成人买眼镜即可助眠。')],
    extra_priorities_for_parent=[
        '睡足仍困、憋醒已有入口；可补不宁腿的夜间动腿冲动及与缺铁/药物评估，不能直接给人人补铁。',
        '手表睡眠分数越看越焦虑，可结合睡眠日记、实际白天功能、设备不诊断及睡眠监测适应证；避免同运动手表完全重复。',
        '夜里被尿意/疼痛/反流反复打断可做交叉入口，先分病因，不用一概禁水或把所有夜醒算失眠。',
        '明显少睡却异常兴奋、精力亢奋和冲动可保留评估提醒，不扩展心理治疗或自诊。'],
    checks=dict(summary_lengths={e['id']:len(e['summary']) for e in entries},
                metadata_checked=True,blocking_unresolved=[]))

for e in entries:
    assert 100<=len(e['summary'])<=180,(e['id'],len(e['summary']))
    assert not re.search(r'[\r\n|]|\[@|\]\(',e['summary'])
used=set(re.findall(r'\[@([^\]]+)\]',json.dumps(entries,ensure_ascii=False)))
assert used=={s['id'] for s in sources}
HERE.mkdir(parents=True,exist_ok=True)
for filename,value in [('screen-entries',entries),('screen-sources',sources),('screen-audit',audit)]:
    (HERE/(filename+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(audit['checks'],ensure_ascii=False))
