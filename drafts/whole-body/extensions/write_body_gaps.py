"""Small, actionable omissions found in the whole-book reader audit."""
import re
from write_reader_gaps import entry, web, save


def main():
    sources=[
        web('GAPS-S01','American Academy of Dermatology Association','Hives: Diagnosis and treatment',
            'https://www.aad.org/public/diseases/a-z/hives-treatment','2026 Jul 13',
            '荨麻疹急症、抗组胺药轻症和专科选择；持续6周/大面积、症状记录与选择性检查。',
            '机构公众指导，不将其所有器械/新药列表当中国批准或一线方案；未重读所有试验。',
            '实际读急症、轻症、6周就诊、诊断检查、抗组胺及页末Last updated。'),
        web('GAPS-S02','Centers for Disease Control and Prevention','Symptoms of scabies',
            'https://www.cdc.gov/scabies/signs-symptoms/index.html','2024 Jan 12',
            '夜间明显瘙痒、常见皮疹部位；无症状仍可传播。',
            '这些症状不能单独确诊疥疮，不把所有合租瘙痒归为螨虫。',
            '实际读原页主要症状、常见部位及儿童差异。'),
        web('GAPS-S03','Centers for Disease Control and Prevention','Treatment of scabies',
            'https://www.cdc.gov/scabies/treatment/index.html','2024 Jan 12',
            '杀螨治疗、衣物清洁、不可清洗物封存，持续瘙痒可不等于失败，新疥道/疹复评及不用杀虫喷雾。',
            '不照搬美国处方/非处方分类，不把成人治疗范围与药物套婴幼儿或孕期。',
            '实际读Treatment overview、感染与2至4周复评、What not to do段。'),
        web('GAPS-S04','Centers for Disease Control and Prevention','Preventing scabies',
            'https://www.cdc.gov/scabies/prevention/index.html','2023 Dec 18',
            '家庭成员与近接触者同时治疗；治疗前三天衣物寝具处理，不能清洗物封存。',
            '家庭同住/密切接触不等于同楼所有人，仍由接诊者结合暴露安排。',
            '实际读原页预防段全部关键点；未套用集体机构额外流程。'),
        web('GAPS-S05','国家疾病预防控制局综合司; 国家卫生健康委办公厅','关于印发狂犬病暴露预防处置工作规范（2023年版）的通知',
            'https://www.ndcpa.gov.cn/jbkzzx/c100012/common/content/content_1706568784078565376.html','2023 Sep 16',
            '暴露定义分级、约15分钟肥皂水/清水交替冲洗、眼等特殊部位、疫苗与被动免疫、破伤风等评估。',
            '文书署发2023Sep13、网页公布Sep16分开；未输出疫苗/免疫制剂剂量或替个体判级。',
            '实际读规范第1至10条原文，特别第7和10条伤口/特殊部位；不声称重核全部免疫程序。'),
    ]
    sources[0]['funding_disclosure']='页面明确感谢Sanofi与Regeneron支持，并称内容由AAD独立开发；这一资助关系保留展示，不据此自动否定或提高具体建议。'
    entries=[
        entry('bodygap-001','bodyskin-rash','风团伴口舌肿、气短或晕厥就急救；反复起风团别只靠止痒膏',
            '一块块突然隆起、很痒又会消退的风团，可能是荨麻疹；若伴面口咽肿、吞咽或呼吸困难、眩晕欲倒，立即急救。轻症可核对适合的抗组胺药，反复或大面积则检查原因与治疗。记录单块持续多久和近期用药，不把所有风团都当食物过敏，也不要为求彻底清零而自行大范围忌口或叠药。',
            '**风团伴面口咽肿、呼吸吞咽困难、明显眩晕或将要晕倒，立即联系急救或急诊。** 风团是突然隆起的痒块，可能属于荨麻疹；严重反应不能等待涂药。[@GAPS-S01]\n\n只有轻度风团和痒时，可向药师核对合适的较少嗜睡抗组胺药；它抑制组胺等引起的症状，不是给身体排毒。按本地药品说明，不自己加倍或叠多种；孕哺、儿童与正在用其他药时另核。大面积、持续或反复出现，尤其超过6周，应预约皮肤科。[@GAPS-S01]\n\n拍下皮疹，记录单块多久消退、药物、感染、运动冷热与其他症状。荨麻疹不全由食物过敏引起；检查应由病史和表现决定，不直接买全套过敏原套餐，也不盲目长期忌口。[@GAPS-S01]',
            '及时识别严重反应，让反复风团获得针对处理，少靠涂抹和忌口反复试错。',
            'AAD2026荨麻疹诊疗与急症指导。[@GAPS-S01]',ages=('child','teen','adult','older'),safety=True),
        entry('bodygap-002','bodyskin-rash','夜里特别痒且同住者也起疹，就查疥疮，别只换除螨沐浴露',
            '夜间明显瘙痒，指缝、腕部、腰臀或生殖器周围起疹，尤其近接触者也痒时，应检查疥疮等原因。疥疮是疥螨寄生，不是搓洗不够，普通除螨沐浴露和杀虫喷雾不能替代治疗。确诊后要把用药、密切接触者与衣被处理一起安排；治后仍痒不一定失败，新疹或持续不好再复评。',
            '**夜间特别痒、常见部位起疹，或同住/密切接触者也有相似表现，去皮肤科说明接触史。** 疥疮由疥螨寄生引起，指缝、腕部、腰臀和生殖器周围是常见部位；但这些线索不能排除湿疹等其他原因。[@GAPS-S02]\n\n确诊后，家庭成员及密切接触者应按医嘱同一时间处理，包括暂时没有瘙痒的人。患者需要针对疥螨的外用或口服药物，不是反复搓澡、换除螨沐浴露或向身体喷杀虫剂。问清涂哪些部位、停留多久、何时重复及哪些同住/密切接触者要同步处理；儿童和孕期不直接照成人方案。[@GAPS-S03][@GAPS-S04]\n\n按医嘱同时处理近期衣物、寝具和毛巾：可热洗烘干的依标签执行，不能清洗的可按指导密封封存数日至一周。治疗后瘙痒可能延续几周，不自动说明药没用；若出现新疥道、新疹、皮肤感染，或超过2至4周仍痒，要复评，不自行无限重复用药。[@GAPS-S03][@GAPS-S04]',
            '减少漏掉传染性皮肤病和接触者反复传回，以及不必要的杀虫剂暴露。',
            'CDC症状、治疗与预防原页。[@GAPS-S02][@GAPS-S03][@GAPS-S04]',ages=('teen','adult','older')),
        entry('bodygap-003','bodyskin-wound','被犬猫咬抓伤先冲洗约15分钟，尽快评估狂犬病暴露，别等感染再去',
            '犬猫等动物咬伤、抓伤，或唾液接触破损皮肤与黏膜，可能需要狂犬病暴露处置。普通皮肤伤口尽早用肥皂水和流动清水交替冲洗约15分钟，再尽快到正规暴露处置门诊；是否需要疫苗和现成抗体由暴露分级等决定，不能以伤口没流血、宠物看着健康就自行排除。眼部和重伤另走及时医疗处理。',
            '**有动物咬抓伤，或唾液接触破损皮肤、黏膜，先处理伤口并尽快到狂犬病暴露处置门诊评估。** 轻微抓伤即使没明显出血也可能需要处置；接触蝙蝠等情境也要说明，不自己凭动物外观判零风险。[@GAPS-S05]\n\n普通皮肤咬抓伤尽早用肥皂水与流动清水交替彻底冲洗约15分钟，再冲净残留。眼部不要灌肥皂水或消毒剂，应及时由医疗人员用适当方式处理；深伤、头面等特殊部位也尽快求医。大量出血止不住时先加压止血并急救，不为凑够冲洗时间耽误。[@GAPS-S05][@BODYSKIN-S01]\n\n带上受伤时间、动物种类、伤口位置、既往疫苗和免疫疾病资料。医生判级后决定疫苗及被动免疫制剂——后者提供现成抗体；也会评估破伤风、感染和伤口闭合。抗生素与消毒不能代替需要的狂犬病预防，不等待症状出现或伤口感染再就诊。[@GAPS-S05]',
            '把容易误当小伤的动物暴露接上及时、规范的预防处置。',
            '国家疾控局与国家卫健委2023规范；NHS出血伤口急症。[@GAPS-S05][@BODYSKIN-S01]',
            ages=('child','teen','adult','older'),safety=True),
    ]
    for e in entries:
        e['chapter_id']='bodyskin'
        if not 110 <= len(e['summary']) <=170:raise ValueError((e['id'],len(e['summary'])))
    save('body-gaps-entries.json',entries);save('body-gaps-sources.json',sources)
    save('body-gaps-audit.json',dict(status='author_checked_pending_independent_review',entries=len(entries),source_records=len(sources),
        clinical_review_status='not_clinically_reviewed',
        rationale='读者场景查漏：反复风团/严重过敏、宿舍近接触瘙痒、动物咬抓伤处理。分别补原体表章，不另开重复病种百科。',
        safety='急症不因年龄筛选隐藏；家庭不能靠皮疹/痛感自诊；不抄国外药品分类或剂量。'))


if __name__=='__main__':main()
