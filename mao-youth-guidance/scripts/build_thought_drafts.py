"""Build source-linked drafts for the fixed core-thought dictionary."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from common import write_json

SEEDS = [
    ("实践与认识", "认识来源于实践，并要回到实践接受检验；认识是在经验、概括、再实践的反复中发展的。", ["实践", "认识", "经验", "检验"], ["哲学与认识论"], ["学习", "职业选择", "计划复盘"]),
    ("调查研究", "判断具体问题以前先取得可靠材料，区分事实、传闻和预设，再形成意见和办法。", ["调查", "研究", "实际", "材料"], ["调查研究", "群众与社会"], ["社会观察", "职业判断", "关系冲突"]),
    ("矛盾与主要矛盾", "具体分析相互联系又相互冲突的因素，在一定阶段抓住最支配行动的主要矛盾，同时看到主次会转化。", ["矛盾", "主要矛盾", "次要", "具体分析"], ["矛盾分析", "哲学与认识论"], ["决策", "焦虑", "多重压力"]),
    ("群众路线", "从人的真实需要和经验中集中意见，再把形成的办法交回实践检验；不能用抽象口号替代具体生活。", ["群众", "人民", "意见", "生活"], ["群众与社会", "组织与领导"], ["公共治理", "团队协作", "社会参与"]),
    ("组织与领导", "领导要把一般号召转化为具体指导，明确责任、反馈和检查，使集体行动能够执行和修正。", ["领导", "组织", "具体", "检查"], ["组织与领导"], ["团队管理", "学习计划", "公共行动"]),
    ("学习与教育", "学习应围绕真实问题，把阅读、调查、思考和实践结合起来；评价学习要看理解和解决问题的能力。", ["学习", "教育", "实际", "知识"], ["学习与教育", "哲学与认识论"], ["升学", "自学", "能力成长"]),
    ("劳动与生产", "物质生产和劳动条件是理解社会生活的重要基础；评价个人困境不能忽视资源、分工和制度条件。", ["劳动", "生产", "经济", "建设"], ["经济与劳动", "群众与社会"], ["就业", "劳动权益", "职业价值"]),
    ("文化与表达", "表达必须有真实内容、明确对象和可理解的语言；反对空话、套话和脱离受众的形式主义。", ["文章", "演说", "群众", "语言", "空话"], ["文化与文艺", "诗词、杂文与政论"], ["沟通", "写作", "公共表达"]),
    ("作风与纪律", "以事实、责任和可检查的行动纠正主观主义与形式主义；批评的目标应是发现问题和改进工作。", ["作风", "批评", "责任", "主观主义", "形式主义"], ["作风与伦理", "组织与领导"], ["复盘", "团队冲突", "自我要求"]),
    ("个人与集体", "个人成长发生在社会关系和共同劳动中；集体目标不能抹去个人尊严、具体处境和合理边界。", ["个人", "集体", "团结", "同志"], ["群众与社会", "作风与伦理"], ["家庭冲突", "团队关系", "个人选择"]),
    ("社会结构与利益", "分析社会问题要考察群体处境、资源分配、制度激励和利益关系，不能把结构性压力只归咎于个人品质。", ["阶级", "利益", "社会", "制度", "群众"], ["群众与社会", "经济与劳动", "政权与制度"], ["青年焦虑", "就业竞争", "社会不平等"]),
    ("革命与变革", "社会变革需要分析条件、力量、阶段和组织，不能把愿望当作现实；当代应用只转译为合法、非暴力的改革与公共参与。", ["革命", "条件", "力量", "阶段"], ["革命与变革", "群众与社会"], ["制度改革", "公共参与", "社会倡议"]),
    ("军事与战略", "战略上保持长期判断，战术上严肃对待具体困难，集中有限资源解决关键环节；军事内容在个人辅导中只作方法类比。", ["战略", "战术", "集中", "力量", "敌人"], ["军事与战略"], ["长期规划", "资源配置", "应对挫折"]),
    ("政权与制度", "制度和权力结构影响资源、责任和行动空间；相关历史论断必须放回其政治条件中分析，不能直接移作当代指令。", ["政权", "国家", "制度", "民主", "人民"], ["政权与制度"], ["公共治理", "制度评价", "公民责任"]),
    ("国际关系", "独立判断、自力更生与争取外部合作并不矛盾；对国际问题要区分内部根据、外部条件和具体利益。", ["国际", "独立", "自力更生", "合作", "国家"], ["国际关系"], ["国际观察", "个人发展", "合作选择"]),
    ("历史与发展", "事物发展有过程、阶段和不平衡，评价一种现象既要看形成条件，也要看变化方向和可能的转化。", ["历史", "发展", "阶段", "过程", "条件"], ["哲学与认识论", "革命与变革"], ["人生阶段", "社会趋势", "长期判断"]),
    ("失败、挫折和坚持", "失败既可能暴露方法错误，也可能反映条件和力量暂时不足；应先复盘原因，再决定坚持、调整或退出。", ["失败", "困难", "错误", "经验", "成功"], ["哲学与认识论", "作风与伦理"], ["考试失败", "求职受挫", "长期目标"]),
    ("青年成长和社会责任", "青年应在真实学习、劳动和社会实践中形成能力与责任感；责任不能被解释为无限牺牲或忽视身心健康。", ["青年", "学生", "学习", "劳动", "责任"], ["学习与教育", "群众与社会"], ["青年焦虑", "人生方向", "社会责任"]),
]


def quality(text: str) -> float:
    if len(text) < 120 or "……" in text or "目录" in text[:80]:
        return -10
    cjk = sum(0x3400 <= ord(ch) <= 0x9fff for ch in text)
    weird = len(re.findall(r"[A-Za-z][A-Za-z]", text)) + text.count("�")
    return cjk / max(len(text), 1) - weird * 0.02


def score(text: str, keywords: list[str]) -> float:
    return sum(min(text.count(word), 4) for word in keywords) * 2 + quality(text)


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: build_thought_drafts.py <index_jsonl> <mapping_json> <review_dir>")
        return 2
    index_path, _mapping_path, review_dir = map(Path, sys.argv[1:])
    passages = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    cards = []
    for number, (title, proposition, keywords, article_types, questions) in enumerate(SEEDS, 1):
        ranked = sorted(passages, key=lambda row: score(row.get("text", ""), keywords), reverse=True)
        selected, used_pdfs = [], set()
        for row in ranked:
            if score(row.get("text", ""), keywords) < 4 or quality(row.get("text", "")) < 0:
                continue
            if row["pdf_id"] in used_pdfs and len(selected) < 2:
                continue
            selected.append(row["passage_id"])
            used_pdfs.add(row["pdf_id"])
            if len(selected) == 4:
                break
        cards.append({
            "thought_id": f"thought-{number:03d}", "title": title,
            "core_proposition": proposition,
            "reasoning_chain": ["从具体事实和历史条件出发", "识别主要关系与可迁移方法", "形成判断并回到现实行动检验"],
            "keywords": keywords, "themes": [title], "article_types": article_types,
            "applicable_questions": questions,
            "historical_context": "需结合所引篇章的写作时间、对象和政治社会条件逐条核定。",
            "transferable_method": proposition,
            "period_bound_claims": "原文中的战争、革命组织和特定政治任务不得直接转换为今天的个人行动命令。",
            "modern_translation": "将该方法转化为事实调查、问题排序、合法非暴力行动、阶段复盘和必要的专业求助。",
            "limitations": "不能替代医学、法律、财务或危机干预；不能忽略当代制度、技术和个人权利条件。",
            "counterpoints": "审核时补充与该命题形成张力的不同时期文本、现代研究或反例。",
            "source_passages": selected, "period": "跨时期，需按来源分别说明",
            "confidence": 0.55 if selected else 0.2, "review_status": "draft",
            "quote_status": "unverified",
            "notes": "核心命题为预设字典初稿；代表段落为自动检索候选，需人工核对原页。",
        })
    relations = []
    for source, relation, target in [(1,"supports",2),(2,"supports",3),(3,"applies_to",17),(4,"supports",5),(6,"depends_on",1),(8,"depends_on",2),(9,"supports",5),(11,"depends_on",7),(12,"context_bound_by",14),(13,"applies_to",17),(15,"depends_on",14),(16,"supports",17),(17,"applies_to",18),(18,"depends_on",1)]:
        relations.append({"from": f"thought-{source:03d}", "type": relation, "to": f"thought-{target:03d}", "status": "draft"})
    review_dir.mkdir(parents=True, exist_ok=True)
    write_json(review_dir / "thought-cards-draft.json", {"schema": "mao-youth-guidance/thought-cards.v1", "cards": cards, "relations": relations})
    lines = ["# 核心思想卡片批量审核", "", "核心命题已经预设；代表段落由本地语料自动检索。审核原页后，将 JSON 中的 `review_status` 改为 `approved`。", ""]
    for card in cards:
        lines += [f"## {card['thought_id']} - {card['title']}", f"- 核心命题：{card['core_proposition']}", f"- 适用问题：{'、'.join(card['applicable_questions'])}", f"- 代表段落候选：{'、'.join(card['source_passages']) or '未找到'}", f"- 当代转译：{card['modern_translation']}", f"- 时代边界：{card['period_bound_claims']}", f"- 局限：{card['limitations']}", "- 审核：draft", "- 审核意见：", ""]
    (review_dir / "thought-cards-draft.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"created {len(cards)} thematic thought-card drafts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
