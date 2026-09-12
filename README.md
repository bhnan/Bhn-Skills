# BHN Skills

个人维护的 Agent 技能集合。每个技能位于独立目录，以 `SKILL.md` 为入口。

| 技能 | 入口 |
| --- | --- |
| ai-native-sdlc | [按需求组织开发流程与完成后的变更记录](ai-native-sdlc/SKILL.md) |
| project-wiki | [项目内 Wiki：定制初始化、按需检索、资料消化与增量维护](project-wiki/SKILL.md) |
| bug-summary | [Bug Summary](bug-summary/SKILL.md) |
| link-fetcher | [Link Fetcher](link-fetcher/SKILL.md) |

## Project Wiki

`project-wiki` 已替代原 `wiki-creator`；旧版本保留在 Git 历史中。

在项目内使用单个 `.wiki/` 目录组织知识。支持软件、研究、业务及自定义场景，也适用于非 Git 文件夹。软件场景可以消化 ai-native-sdlc 的需求文档与后续变更记录。

将完整 `project-wiki/` 目录复制到客户端的技能目录，保留 `references/`、`assets/`、`scripts/` 和 `agents/`。例如当前 Codex 本地环境可使用 `~/.codex/skills/project-wiki/`。在支持该技能的会话中请求：

```text
使用 $project-wiki，基于当前项目的文档初始化并填充 .wiki。
使用 $project-wiki，查找以前为什么采用这个接口设计，并给出原始依据。
使用 $project-wiki，同步变更来源影响的页面。
```

辅助脚本要求 Python 3.9+，无需第三方 Python 包。脚本负责扫描、关键词检索、变化检测和格式校验，Agent 负责资料理解与页面编写。当前版本采用显式维护，不启动后台任务或上传云端。

```bash
python3 project-wiki/scripts/wiki.py --help
python3 project-wiki/scripts/test_wiki.py
```

配置使用 JSON；知识页面采用 Markdown，frontmatter 使用 JSON 对象形式的 YAML 子集。具体约定见 [contracts](project-wiki/references/contracts.md)。
