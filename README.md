页面渲染 PNG 和 Python 缓存没有提交，因为它们可以从 PDF 和索引重新生成。
## 安全边界

## 本地验证
以下情况不会套用文学化仿写：

- 自伤、自杀或伤害他人的风险；
- 暴力、违法行动或危险动员；
- 医疗诊断和治疗决定；
- 法律结论和具体诉讼策略；
- 投资、借贷和重大财务决策；
- 针对个人或群体的迫害、仇恨和危险行动。

遇到这些问题，Skill 会优先确认风险，使用直接的现代语言，并在必要时建议联系急救、专业机构、学校心理中心、律师或合规的财务专业人士。

## 实际对话示例

### 用户提问

```text
$mao-youth-guidance 如何看待现在社会的大学生就业问题？
```

### 第一步：问题拆解

```text
我对这个问题的理解：

- 主题领域：大学生就业与社会结构
- 问题方向：评价现状、分析成因，并讨论可能出路
- 情绪状态：未明确，暂按理性讨论处理
- 现实约束：尚未限定地区、专业、学历和毕业年份
- 利害相关者与责任边界：大学生、高校、用人单位与公共政策；不能把结构压力全部归咎于个人
- 主要矛盾：高等教育人才供给和职业期待扩大，与适合毕业生进入、能够持续发展且收入覆盖生活成本的岗位不足之间的矛盾
- 次问题：专业错配、经验门槛、学历筛选、地区成本、就业稳定性、劳动权益和求职焦虑
- 推荐思想板块：调查研究、主要矛盾、劳动与生产、社会结构与利益、青年成长与实践
```

Skill 会进一步说明：就业难至少要分为“没有工作”“没有匹配的工作”“有工作但工资和生活成本不匹配”三种情形，并询问用户是否开始分析，或是否加入带日期和来源的当前数据。

### 第二步：正式分析的风格

```text
表达说明：以下为当代仿写，借鉴毛泽东文章的论证方式与语言气质；引号内文字才是已核验原文。

所谓“大学生就业难”，实际包含三种不同情形：找不到任何工作，找不到与学历和专业相匹配的工作，或者找到工作但工资、稳定性和生活成本不相称。三者不能混为一谈。

问题不宜简单概括为“大学生太多”。更要紧的是，教育供给、产业结构、招聘制度、地区成本和职业发展机会没有形成好的匹配。看清结构，是为了停止无谓的自责；强调行动，是为了不把自己的命运完全交给结构。
```

随后回答会把毛泽东原文、历史解释、当代事实、Skill 的现实判断和个人行动明确分开，并给出“今天—本周—本月”的调查与能力验证任务。

## 知识库与仓库结构

```text
mao-youth-guidance/
├── mao-youth-guidance/          # 可安装的 Skill
│   ├── SKILL.md                 # 入口规则
│   ├── agents/openai.yaml       # 显式调用配置
│   ├── references/              # 语气、引用、解读和安全规则
│   ├── scripts/                 # 预处理、核验和重建脚本
│   └── knowledge-base/v2/       # 随 Skill 分发的正式知识库
├── knowledge-base/v1/           # 可回滚的旧版本
├── knowledge-base/v2/           # 项目级知识库副本
├── mao-corpus/                  # PDF、文本、元数据和核验记录
│   ├── raw/                     # 原始 PDF，保持不修改
│   ├── index/                   # 段落索引
│   ├── normalized/              # 标准化文本
│   ├── metadata/                # 文件映射与来源信息
│   └── qa/                      # 核验状态、报告和可靠引文
├── review/                      # 审核和映射记录
└── tests/                       # 回归测试
```

当前 v2 知识库包含 24,181 条已分级段落、5,319 条可靠短引和 18 张已审核思想卡片。自动核验结果不等同于每一页都经过人工逐字目视校对；引用规则会对此保持明确说明。

## 本地验证与开发

```powershell
$env:PYTHONUTF8 = "1"

python C:\Users\<用户名>\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\mao-youth-guidance
python .\mao-youth-guidance\scripts\verify_passages.py .\knowledge-base\v2\thought-cards.json .\knowledge-base\v2\passages.jsonl .\knowledge-base\v2\verified-quotes.jsonl
python <CODEX_HOME>\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\mao-youth-guidance
python .\mao-youth-guidance\scripts\verify_passages.py `
  .\knowledge-base\v2\thought-cards.json `
  .\knowledge-base\v2\passages.jsonl `
  .\knowledge-base\v2\verified-quotes.jsonl
python -m pytest -q .\tests\test_verification_pipeline.py

## 运行边界
如果更换 PDF、OCR 工具或映射，应按照 `inspect → identify → extract/OCR → normalize → build index → verify → rebuild` 的顺序重建；原始 PDF 不应被修改。

## 项目状态

- 当前知识库版本：`v2`
- Skill 调用方式：仅显式调用
- 默认语言：中文
- 默认风格：当代仿写
- 原文策略：可靠段落逐字引用，其余只转述或跳过
- GitHub：<https://github.com/Ronnie469469/mao-youth-guidance>

社会和政治问题可以进行有依据的分析与观点比较，但行动建议必须合法、非暴力。自伤或他伤、医疗、法律、财务和危险动员问题优先使用直接现代语言并进行必要的专业分流。
欢迎提交 Issue，反馈分类误判、引用定位问题、知识库缺口或表达风格建议。新增核心思想卡片必须保留出处并经过单独审核，不会因为一次用户反馈就自动改写核心知识库。
