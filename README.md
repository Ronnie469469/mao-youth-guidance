一个显式调用的 Codex Skill：使用经过预处理和核验的毛泽东文本知识库，分析青年困惑与当代社会问题，并给出具体行动、心理支持和安全边界提示。
> 把经典文本转化为今天可以使用的问题分析工具。

`mao-youth-guidance` 是一个面向 Codex 的显式调用 Skill。它以用户提供并经过预处理、分类、核验的毛泽东相关文本为基础，用来分析青年困惑、学习压力、就业问题、家庭冲突、个人选择和当代社会现象。

它不是简单的语录问答，也不是把历史口号机械套到现实生活中。它会先调查问题本身，再抓住主要矛盾，区分历史条件与今天的现实，最后把分析落实为能够执行和复盘的行动。

## 安装

### 方法一：使用 Codex Skill Installer

在 Codex 中调用 Skill Installer，并指定：

```text
GitHub 仓库：Ronnie469469/mao-youth-guidance
Skill 路径：mao-youth-guidance
```

安装完成后重启 Codex。

## 直接使用
### 方法二：手动安装

安装 Skill 后显式调用：
把仓库中的整个 `mao-youth-guidance/` 文件夹复制到：

```text
C:\Users\<你的用户名>\.codex\skills\mao-youth-guidance
```

PowerShell 示例：

```powershell
$source = "C:\路径\mao-youth-guidance\mao-youth-guidance"
$target = "$env:USERPROFILE\.codex\skills\mao-youth-guidance"

if (Test-Path -LiteralPath $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
}

New-Item -ItemType Directory -Path $target -Force | Out-Null
Copy-Item -Path "$source\*" -Destination $target -Recurse -Force
```

复制后重启 Codex，使 Skill 清单重新加载。

## 如何调用

在新对话中显式调用：

```text
$mao-youth-guidance 我考研失败，不知道要不要继续。
```

也可以只先调用 Skill，再输入问题：

```text
$mao-youth-guidance
如何看待现在社会的大学生就业问题？
```

Skill 默认使用 `knowledge-base/v2/`，不会在运行时重新从 PDF 提炼思想。正式逐字引用只来自 `verified-quotes.jsonl`；未核验内容只能转述，阻断内容不会进入检索。
该 Skill 默认只允许显式调用，不会自动介入无关对话。

默认回答采用当代仿写语气，借鉴毛泽东文章的问题分析节奏和语言气质，但会明确标注为当代仿写，不冒充本人，不伪造原文。也可以要求现代方法论风格或学术解释风格。
## 核心特点

## 安装
### 1. 先拆解问题，再正式回答

在 Codex 中安装本仓库的 Skill 路径：
面对复杂问题，Skill 会先展示：

```text
$skill-installer
我对这个问题的理解：
- 主题领域：
- 问题方向：
- 情绪状态：
- 现实约束：
- 利害相关者与责任边界：
- 期望结果：
- 主问题与主要矛盾：
- 次问题：
- 推荐思想板块：
```

或者将 `mao-youth-guidance/` 目录复制到：
用户可以回复“开始分析”，也可以修改分类。信息不足时，Skill 会渐进式追问，最多五问，重点确认发生了什么、困惑从何而来、已经尝试过什么、最大限制是什么，以及希望得到评价、方案还是鼓励。

### 2. 不在运行时重新提炼思想

Skill 默认读取已经建立好的 `knowledge-base/v2/`，而不是每次从 PDF 重新总结。知识库包括：

- 18 张已审核的核心思想卡片；
- 文章类型与主题板块字典；
- 概念关系图；
- 页级和段落级索引；
- 历史语境、适用条件和局限；
- 可靠原文、转述材料和阻断段落的状态记录。

### 3. 原文引用有严格等级

| 状态 | 使用方式 |
| --- | --- |
| `quote_verified` | 可以逐字引用，并定位到作品、卷次、PDF 和页码 |
| `paraphrase_only` | 可以检索和转述，但不能加引号 |
| `blocked` | 不进入引用检索 |

正式逐字引用只来自 `knowledge-base/v2/verified-quotes.jsonl`。日文、英文或其他语言资料会保留语言和版本信息，不能翻译后伪装成中文原文。

### 4. 输出分为两层

默认先给出结构化指导单，再给出较完整的评论文章。内容通常包括问题画像、分类判断、原文依据、历史语境、核心思想、现实评价、不同观点、行动方案、心理支持和专业边界。

用户也可以指定“只要提纲”“只要行动方案”“只要短答”“使用现代方法论风格”或“使用学术解释风格”。

## 默认语气：当代仿写

Skill 默认尽量接近毛泽东文章的论证节奏和语言气质，但模仿的是方法与表达结构，不是身份。

主要特点：

- 先摆事实，再分析原因；
- 先区分现象，再抓主要矛盾；
- 既看客观条件，也看个人能够改变的部分；
- 使用清楚的对照和递进；
- 重视调查、实践、试验、总结和修正；
- 结论坚定、语言直接，但不空喊口号。

正式分析会标注：

```text
C:\Users\<用户名>\.codex\skills\mao-youth-guidance
表达说明：以下为当代仿写，借鉴毛泽东文章的论证方式与语言气质；引号内文字才是已核验原文。
```

复制后重启 Codex。
Skill 不会冒充毛泽东本人，不会编写“毛泽东新语录”，也不会把生成内容放进原文引号。自伤、医疗、法律和财务问题始终使用直接现代语言。

## 仓库内容
## 适用问题

- `mao-youth-guidance/`：Skill 入口、参考规则、处理脚本和随 Skill 分发的 `knowledge-base/v2/`。
- `knowledge-base/v2/`：18 张已审核思想卡片、概念关系、段落索引、可靠引文和阻断段落。
- `mao-corpus/raw/`：用户提供的原始 PDF，保持不修改，用于追溯和重新处理。
- `mao-corpus/index/`、`normalized/`、`metadata/`、`qa/`：页级文本、元数据、核验结果和报告。
- `knowledge-base/v1/`：旧版本知识库，保留用于回滚和比较。
- `review/`：PDF 映射、思想卡片审核记录和核验报告。
- `tests/`：核验规则和知识库一致性测试。
- “我考研失败，不知道要不要继续。”
- “年轻人为什么越来越焦虑？”
- “怎么看待就业竞争和躺平？”
- “家庭要求和个人选择冲突怎么办？”
- “如何评价某个有争议的社会现象？”
- “语料库没有相关原文，怎么办？”

社会与政治问题可以进行有依据的分析、比较不同立场并表达明确判断；行动建议必须合法、非暴力、可验证。

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
