# 剧本 YAML Schema 说明

本文档定义 AI 小说转剧本工具输出的 YAML 结构，并说明设计原因。该 Schema 面向“中文小说/IP 改编为短剧分场剧本初稿”的场景。

## 设计目标

1. 可编辑：作者能直接修改角色、场景、对白和旁白。
2. 可追踪：每个剧本场景能追溯到来源章节。
3. 可校验：工具能自动判断 YAML 是否满足结构要求。
4. 可扩展：后续可导出为分镜、拍摄清单或其他剧本格式。

## 顶层结构

```yaml
schema_version: "1.0"
project: {}
source: {}
characters: []
episodes: []
validation: {}
```

### `schema_version`

固定为 `"1.0"`。后续新增字段时可通过版本号兼容旧输出。

### `project`

```yaml
project:
  title: "雨夜重逢"
  source_type: "novel"
  target_format: "short_drama"
  language: "zh-CN"
```

设计原因：明确来源是小说，目标是短剧，避免 YAML 被误解为普通文本摘要或传统电影剧本。

### `source`

```yaml
source:
  chapters:
    - id: "ch01"
      title: "第一章 雨夜重逢"
      summary: "林晚在雨夜街口遇见顾沉..."
```

设计原因：题目要求输入 3 个章节以上。保留章节列表可以证明工具确实解析了多章节输入，也能支持后续逐章回看和改编审查。

约束：

- `chapters` 至少 3 项。
- `id` 使用 `ch01`、`ch02` 这样的稳定编号。

### `characters`

```yaml
characters:
  - id: "char_01"
    name: "林晚"
    role: "protagonist"
    description: "故事主角，面临情感与命运的双重选择。"
    goals:
      - "找出真相并保护重要的人"
```

设计原因：角色独立建模后，对白可以引用角色 ID，减少同名、改名、错别字导致的编辑混乱。

### `episodes`

```yaml
episodes:
  - id: "ep01"
    title: "雨夜重逢：第一集"
    logline: "主角在连续冲突中发现真相的第一块拼图。"
    scenes: []
```

设计原因：短剧通常按集和场次组织。即使 MVP 只生成一集，保留 `episodes` 层也方便后续扩展多集剧本。

### `scenes`

```yaml
scenes:
  - id: "sc01"
    title: "第 1 场：建立人物目标"
    location: "雨夜街口"
    time_of_day: "night"
    source_chapters: ["ch01"]
    dramatic_purpose: "建立人物目标"
    adaptation_note: "将小说叙述压缩为短剧分场。"
    elements: []
    hook: "门外传来一句熟悉的声音。"
```

设计原因：

- `source_chapters`：让作者知道场景来自哪里，降低 AI 黑盒感。
- `dramatic_purpose`：说明这一场在剧作结构中的作用。
- `adaptation_note`：解释改编策略，便于作者继续打磨。
- `hook`：贴合短剧节奏，突出每场结尾的追看动力。

### `elements`

```yaml
elements:
  - type: "action"
    text: "雨夜街口，林晚停在积水前。"
  - type: "dialogue"
    speaker: "char_01"
    text: "我不是来解释的，我是来要一个答案。"
  - type: "narration"
    text: "旁白交代人物无法说出口的隐秘动机。"
  - type: "transition"
    text: "切至下一场。"
```

设计原因：剧本不是单一长文本，而由动作、对白、旁白和转场组成。拆成 `elements` 后，前端编辑、导出和校验都更直接。

## 校验规则

后端使用 `backend/app/schemas/screenplay.schema.json` 作为 JSON Schema。YAML 会先解析为 JSON-compatible 对象，再进行校验。

核心校验：

- 必须包含 `schema_version`、`project`、`source`、`characters`、`episodes`。
- `source.chapters` 至少 3 项。
- 至少有 1 个角色、1 集、1 场。
- 场景必须包含来源章节、戏剧目的、改编说明、剧本元素和钩子。
- 剧本元素类型只能是 `action`、`dialogue`、`narration`、`transition`。

## 示例

完整示例见 `samples/output_script.yaml`。
