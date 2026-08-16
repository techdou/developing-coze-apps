# developing-coze-apps

一个 Agent Skill，用于规划、开发、审查和打包 Coze Coding（扣子编程）应用——覆盖全栈 Web 应用、Agent、工作流、RAG、媒体生成，以及单 HTML / iframe 打包交付（`dist/index.single.html`）。

当前版本：**v0.3.2**（见 [CHANGELOG.md](CHANGELOG.md)）

## 这个 skill 做什么

- **平台分层判断**：区分 Coze Coding / 普通 Coze（Agent、Workflow、Plugin、知识库）各自的适用边界，避免把业务系统塞进单个 Bot。
- **资源路由设计**：UI/状态 → 前端；事务与权限 → 后端 + 数据库；文件 → 对象存储（存 key 不存临时签名 URL）；推理 → LLM；文档问答 → RAG。
- **MVP 与分阶段 Prompt**：输出可执行的范围切分（Must / Should / Later）和可直接粘贴的分阶段开发 Prompt。
- **项目审查**：资源误用、配额、安全（前端暴露密钥、service-role 泄漏）、生产就绪度检查。
- **单 HTML / iframe 打包**：把已部署 URL 或静态构建打包为单个 HTML，支持 8 种模板（全屏 iframe、应用外壳、图文页、视觉故事、课程文章、画廊等），并验证自包含性、iframe 安全策略与密钥泄漏。

## 安装

把本目录放入你的 Agent Skills 目录。不同工具的路径：

```bash
# Claude Code
~/.claude/skills/developing-coze-apps/

# 通用跨 agent 目录（Codex / ZCode 等）
~/.agents/skills/developing-coze-apps/
```

或直接克隆：

```bash
git clone https://github.com/techdou/developing-coze-apps.git ~/.agents/skills/developing-coze-apps
```

## 快速开始

对支持 Agent Skill 的助手说：

```text
使用 developing-coze-apps skill，设计一个 Coze Coding 教学应用。先判断平台层级，再输出资源路由、MVP、数据库/存储方案、分阶段开发 Prompt 和验收清单。
```

```text
使用 developing-coze-apps skill，把我在 Coze 搭建的 Web 应用嵌入到单 HTML。先根据 URL 和使用场景给我 3 款方案，包括全屏 iframe、带应用外壳、课程介绍+应用分栏，并推荐最合适的一款。选定后输出到 dist/index.single.html。
```

```text
使用 developing-coze-apps skill，做一个图文型单 HTML 教学页。图片使用当前 Coze Coding 内置生图能力生成；先列出图片槽位、比例、内容要求，再生成页面并把图片内嵌，输出 dist/index.single.html。
```

```text
使用 developing-coze-apps skill，检查当前项目是否适合打包为单 HTML。若是静态/Vite 项目，构建后内联 CSS、JS 和本地图片；若依赖 Next.js API、数据库、鉴权或服务端逻辑，则改用部署 URL 的 iframe wrapper。
```

## 命令行工具

`scripts/single_html_tool.py` 提供完整的多合一命令：

```bash
# 列出所有单 HTML 模板
python scripts/single_html_tool.py list-templates

# 检查源项目 / 已部署 URL
python scripts/single_html_tool.py inspect --source /path/to/project
python scripts/single_html_tool.py inspect --source https://example.coze.site

# 按模板 + 配置渲染
python scripts/single_html_tool.py render \
  --template fullscreen-iframe \
  --config templates/single-html/config-examples/fullscreen-iframe.json \
  --out dist/index.single.html

# 内联打包兼容的静态构建
python scripts/single_html_tool.py bundle-static \
  --input-dir dist --entry index.html --out dist/index.single.html

# 验证产物（自包含性 / iframe 策略 / 密钥泄漏）
python scripts/single_html_tool.py validate dist/index.single.html --format md
```

## 目录结构

```
developing-coze-apps/
├── SKILL.md            # 触发规则与执行契约（skill 入口）
├── README.md           # 本文件
├── CHANGELOG.md        # 版本变更记录
├── VERSION             # 当前版本号
├── docs/               # 功能文档：能力地图、平台边界、单 HTML 选型、安全检查等
├── templates/          # 架构蓝图、工作流契约、构建 Prompt、单 HTML 模板与配置示例
├── scripts/            # single_html_tool 及审查 / 校验 / 一致性检查脚本
├── evals/              # Agent 匹配与输出质量评测用例
└── examples/           # 示例项目与单 HTML 演示产物
```

## 测试

```bash
python scripts/test_single_html_tool.py    # 模板渲染 / 打包 / 校验的回归测试
python scripts/validate_skill_package.py . # skill 包结构与引用完整性检查
```

## 相关文档

- 各文档用途速查见 `SKILL.md` 中的 "Read only what the task needs" 表格——按任务读取所需文件，不必全读。
- 版本历史见 [CHANGELOG.md](CHANGELOG.md)。
