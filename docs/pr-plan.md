# PR 与 Commit 计划

七牛提交规则要求持续交付、PR 粒度清晰、commit 分布合理。本项目按以下方式拆分开发记录。

## 已完成本地提交

1. `docs: add project design spec`
   - 作用：提交市场调研后的设计规格、评分规则映射和项目边界。
   - 测试：文档自检，无占位符和未定义范围。

2. `feat: add backend conversion pipeline`
   - 作用：新增 uv/FastAPI 后端、转换流水线、mock provider、Schema 校验、样例和测试。
   - 测试：`cd backend && uv run pytest`。

3. `feat: scaffold vue conversion UI`
   - 作用：用 Vite Vue TypeScript 脚手架生成前端，并实现小说输入、转换配置、YAML 展示和下载。
   - 测试：`cd frontend && pnpm build`。

## 后续建议 PR

如果推送到 GitHub/Gitee，建议按以下 PR 拆分：

1. 设计与项目初始化。
2. 后端转换流水线。
3. 前端转换工作台。
4. 文档、README、demo 脚本和最终验收修复。

每个 PR 描述包含：

- 标题：一句话说明新增或修改内容。
- 功能描述：说明功能作用和使用方式。
- 实现思路：说明模块拆分和关键逻辑。
- 测试方式：列出实际运行命令和结果。

## 注意事项

- 当前仓库是在 2026-06-07 初始化，第三批次官网截止时间为 2026-06-07 23:59。
- 如果已有远程仓库，建议尽快推送并用 PR 方式合并后续变更。
- 不伪造 commit 时间，不回填不存在的开发记录。
