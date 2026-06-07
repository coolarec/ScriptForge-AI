# 提交清单

用于对照七牛 XEngineer 第三批次提交规则。

## 必交材料

- 公开 GitHub/Gitee 仓库地址。
- Demo 视频链接。
- README 文档。

## 仓库检查

- 根目录包含 `frontend/`、`backend/`、`docs/`、`samples/`。
- README 写明安装、启动、测试、依赖和原创功能。
- `docs/screenplay-yaml-schema.md` 已定义 YAML Schema 并说明设计原因。
- `samples/novel_3_chapters.txt` 包含 3 个章节以上小说文本。
- `samples/output_script.yaml` 是可校验的结构化剧本 YAML。
- commit 不是单次导入，当前本地已有分阶段提交记录。

## 运行检查

后端：

```bash
cd backend
uv run pytest
```

前端：

```bash
cd frontend
pnpm build
```

联调：

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
cd frontend
pnpm dev
```

打开 `http://localhost:5173`，验证：

- 点击“载入样例”后出现 3 章小说。
- 点击“生成 YAML 剧本”后出现 YAML。
- Schema 状态为“通过”。
- 输入少于 3 章时出现错误提示。

## 提交前动作

1. 创建 GitHub/Gitee 远程仓库。
2. 推送本地 `main` 分支。
3. 录制 demo 视频并上传到可访问平台。
4. 将 demo 视频链接追加到 README 的“Demo 视频”一节。
5. 在七牛报名页面填写公开仓库地址。
