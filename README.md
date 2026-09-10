# mao-youth-guidance

一个显式调用的 Codex Skill：使用经过预处理和核验的毛泽东文本知识库，分析青年困惑与当代社会问题，并给出具体行动、心理支持和安全边界提示。

## 直接使用

安装 Skill 后显式调用：

```text
$mao-youth-guidance
```

Skill 默认使用 `knowledge-base/v2/`，不会在运行时重新从 PDF 提炼思想。正式逐字引用只来自 `verified-quotes.jsonl`；未核验内容只能转述，阻断内容不会进入检索。

默认回答采用当代仿写语气，借鉴毛泽东文章的问题分析节奏和语言气质，但会明确标注为当代仿写，不冒充本人，不伪造原文。也可以要求现代方法论风格或学术解释风格。

## 安装

在 Codex 中安装本仓库的 Skill 路径：

```text
$skill-installer
```

或者将 `mao-youth-guidance/` 目录复制到：

```text
C:\Users\<用户名>\.codex\skills\mao-youth-guidance
```

复制后重启 Codex。

## 仓库内容

- `mao-youth-guidance/`：Skill 入口、参考规则、处理脚本和随 Skill 分发的 `knowledge-base/v2/`。
- `knowledge-base/v2/`：18 张已审核思想卡片、概念关系、段落索引、可靠引文和阻断段落。
- `mao-corpus/raw/`：用户提供的原始 PDF，保持不修改，用于追溯和重新处理。
- `mao-corpus/index/`、`normalized/`、`metadata/`、`qa/`：页级文本、元数据、核验结果和报告。
- `knowledge-base/v1/`：旧版本知识库，保留用于回滚和比较。
- `review/`：PDF 映射、思想卡片审核记录和核验报告。
- `tests/`：核验规则和知识库一致性测试。

页面渲染 PNG 和 Python 缓存没有提交，因为它们可以从 PDF 和索引重新生成。

## 本地验证

```powershell
$env:PYTHONUTF8 = "1"
python C:\Users\<用户名>\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\mao-youth-guidance
python .\mao-youth-guidance\scripts\verify_passages.py .\knowledge-base\v2\thought-cards.json .\knowledge-base\v2\passages.jsonl .\knowledge-base\v2\verified-quotes.jsonl
python -m pytest -q .\tests\test_verification_pipeline.py
```

## 运行边界

社会和政治问题可以进行有依据的分析与观点比较，但行动建议必须合法、非暴力。自伤或他伤、医疗、法律、财务和危险动员问题优先使用直接现代语言并进行必要的专业分流。
