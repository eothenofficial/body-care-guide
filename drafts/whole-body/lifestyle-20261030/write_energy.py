"""Author-reviewed additions: stimulant decisions and a fatigue/PEM exception."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent


def main():
    sources=[
      dict(id='LIFE-ROOT-S01',citation='US Food and Drug Administration. Spilling the beans: how much caffeine is too much? [Internet]. [cited 2026 Oct 30]. Available from: https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much',
        url='https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much',
        type='监管机构消费安全指导',support='所有来源咖啡因合计、产品与个体差异；400mg只是多数成人的参考而非目标；儿童青少年不使用能量饮料，孕哺与用药需单独核对；高浓缩咖啡因风险。',
        limitations='美国标签法规不等于中国法律。参考量不保证个人无症状，咖啡和饮料毫升/杯数不能固定换算剂量；未用该页单次中毒数字给家庭自配剂量。',
        reading_depth='已打开原页，完整核读成人参考量、未成年、来源/标签、低咖、能量饮料、高浓缩产品及过量表现；页面未展示可靠更新日，引用只列访问日。',
        content_checked_at='2026-10-30',funding_note='监管患者教育；未把机构名称当单个饮料的疗效证明。'),
      dict(id='LIFE-ROOT-S02',citation='Centers for Disease Control and Prevention. Manage ME/CFS [Internet]. 2024 May 10. [cited 2026 Oct 30]. Available from: https://www.cdc.gov/me-cfs/management/index.html',
        url='https://www.cdc.gov/me-cfs/management/index.html',type='公共卫生机构患者与照护指导',
        support='活动后不适可在12–48小时后加重并持续多日，日记与按耐受分配活动休息可帮助识别范围；ME/CFS不能套健康人的强有氧训练建议。',
        limitations='仅提供识别与就医前减轻反复加重的原则，不能凭疲劳确诊ME/CFS；不把pacing写成治愈，不给所有疲劳者固定活动上限或要求长期卧床。',
        reading_depth='已打开原页，核读PEM与活动管理全部段落、睡眠和诊断边界；2024-05-10为页内日期，资源卡片2024-05-13不作为该页更新日。未采用其他药物及补盐操作。',
        content_checked_at='2026-10-30',funding_note='机构临床教育，非不同运动疗法的直接随机比较。')]
    def entry(eid,title,summary,plain,benefit,evidence,sources,scope):
        return dict(id=eid,title=title,summary=summary,fields=dict(cost='',plain=plain,benefit=benefit,evidence=evidence,sources=sources,notes=''),
            audience=dict(age_groups=['adult','older'],sexes=['all'],scope_note=scope,safety_pin=False),
            clinical_review_status='not_clinically_reviewed',content_checked_at='2026-10-30')
    entries=[
      entry('energy-001','提神前算全天咖啡因总量，心悸或失眠就减，不把400mg当必须吃满的额度',
        '咖啡、茶、能量饮料和训练前补剂里的咖啡因要一起算，不能按几杯咖啡估计总量。多数健康成人的400mg每日参考不是目标或人人安全线；心悸、睡不好或对它敏感时更应减少。能量饮料不能替代睡眠，低咖也可能含咖啡因；儿童青少年、孕哺与合并用药另有条件，不照搬成人参考。',
        '**先查每份含量，再乘实际份数，把咖啡、茶、能量饮料、训练前补剂和相关药物一起算。** 标签未标量时查品牌官方资料或询问商家，不按杯数猜。天然来源的咖啡因也计入总量。[@LIFE-ROOT-S01]\n\nFDA列出的每日400mg是多数成人的参考，不是提神目标，也不保证敏感者或有基础病者不受影响。已经心悸、恶心、手抖或失眠就停止继续叠加并求助；胸痛、晕厥、严重不适按急症处理，见[胸痛分流](#/entry/chest-001)。孕哺、备孕、合并用药先核个人限制；儿童青少年不拿能量饮料提神。[@LIFE-ROOT-S01]\n\n困倦时需要睡眠与查原因，不能靠咖啡因证明可以安全驾车。不要买纯粉或高浓缩液用厨房勺自行配量；想减少长期摄入可逐步减，低咖产品也不一定完全无咖啡因。[@LIFE-ROOT-S01]',
        '把隐形叠加和个体不耐受纳入选择，减少为提神而影响睡眠或误用高浓缩产品。',
        'C，监管机构安全指导与成人参考，不是每个个体的无不良反应上限。',
        'FDA咖啡因来源、参考量与过量表现。[@LIFE-ROOT-S01]',
        '成年人的提神选择；儿童不使用成人参考量，孕哺、备孕与合并用药另核。'),
      entry('energy-002','轻微活动后隔天明显垮掉、几天缓不过来，先记录并评估，别强加训练量',
        '运动后的局部酸痛，与买菜、工作或轻微活动后全身明显加重，不能一概按缺乏锻炼处理。若不适反复延迟到隔天出现，伴疲劳、脑雾或睡眠问题并拖数日，先记录活动和症状，预约评估。暂把任务拆小、穿插休息，避免好一天就补做大量活动；这条不能用于自行诊断慢性疲劳综合征。',
        '**如果很轻的身体或脑力活动后，也反复出现明显迟发加重，先停止硬推固定递增训练。** 活动后不适（PEM）指活动后症状成组加重，可迟发并持续数日，不等于普通肌肉酸痛；它是需要评估的线索，不是一个人凭疲劳即可确定的病名。[@LIFE-ROOT-S02]\n\n把做了什么、持续多久、何时开始加重及恢复过程记下来，带给全科或相关门诊。在评估前按自己耐受把任务拆小、交替活动与休息，不在稍好时一次补完，也不要求人人完全不动。确诊肌痛性脑脊髓炎/慢性疲劳综合征（ME/CFS）者的活动安排需个体化，不能套健康人的训练目标。[@LIFE-ROOT-S02]\n\n突然胸痛、明显气短或晕厥仍先按急症处理；日记和慢性问题评估不能替代急救，见[胸痛急症](#/entry/chest-001)。',
        '识别不适合照搬常规训练进阶的情境，给后续评估留下症状与活动的时间关系。',
        'C，CDC活动管理与症状指导；不是诊断标准或保证恢复的疗法。',
        'CDC的ME/CFS活动后不适与pacing说明。[@LIFE-ROOT-S02]',
        '成年人的反复活动后加重线索；非确诊，也不用于给儿童或个体制定训练处方。')]
    for name,value in [('energy-entries',entries),('energy-sources',sources),('energy-audit',dict(date='2026-10-30',scope='两个补充决策；保留旧疲劳、烟酒与求助条目，情绪不另开治疗百科。',limits='未重新综述全部疲劳病因；仅用已核相关官方段落，不将健康成人参考或ME/CFS方案泛化。',external_checks=[s['url'] for s in sources]))]:
        (HERE/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
