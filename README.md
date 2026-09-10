

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
