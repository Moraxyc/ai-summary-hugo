# AI 摘要文件生成

灵感来源于[大大的小蜗牛](https://eallion.com)的博文[博客 AI 摘要及优化](https://eallion.com/ai-summary/)

该 Python 脚本用于辅助生成 `summary.json`，有以下几种运行方式：

- [uv（推荐）](#uv)
- [Nix](#nix)
- [CI 集成](#ci-集成)

> 默认生成路径为 `../assets/data/summary/summary.json`，使用 `ai-summary --help` 查看全部选项。

## 开发

本项目使用 [uv](https://docs.astral.sh/uv/) 管理依赖、[Nix flake](https://nixos.wiki/wiki/Flakes) 提供 dev shell 与 pre-commit hooks、[Renovate](https://docs.renovatebot.com/) 自动化升级依赖。

```bash
# 安装依赖（生成 .venv 与 uv.lock）
uv sync

# 运行
uv run ai-summary --target .

# lint / format
uv run ruff check .
uv run ruff format .
```

## uv

```bash
uvx --from git+https://github.com/Moraxyc/ai-summary-hugo ai-summary --target .
```

或在仓库内：

```bash
uv sync
uv run ai-summary --target .
```

## Nix

```bash
nix run github:Moraxyc/ai-summary-hugo -- --target .
```

在仓库内：

```bash
nix run .#ai-summary -- --target .
```

## API 端点配置

默认调用 OpenAI 官方接口。如需使用 OpenAI 兼容的第三方服务（如 DeepSeek、Moonshot、本地模型等），可通过 `--base-url` 指定 API 端点：

```bash
uv run ai-summary --target . --base-url https://api.deepseek.com/v1 --model deepseek-chat
```

也可通过环境变量 `OPENAI_BASE_URL` 设置，命令行参数优先级更高：

```bash
export OPENAI_BASE_URL=https://api.deepseek.com/v1
export OPENAI_API_KEY=sk-xxxxx
uv run ai-summary --target .
```

> 注意：切换端点后请同时通过 `--model` 指定该服务支持的模型名称。

## 自定义提示词

默认使用内置的提示词生成摘要：

- 中文：`请在100字内用中文总结以下文章的核心内容: `
- 英文：`Please summarize the main content of the article within 100 words: `
- 系统提示词：`You are a concise summarizer. Summarize the article accurately and briefly.`

如需自定义，使用 `--prompt` 覆盖用户提示词前缀（会拼接到正文之前），使用 `--system-prompt` 覆盖系统提示词：

```bash
uv run ai-summary --target . \
  --prompt "用 50 字以内的 Markdown 列表总结文章要点：" \
  --system-prompt "你是一位资深编辑，擅长提炼文章结构。"
```

提示词较长或包含换行时，可将内容写入文件并用 `@` 前缀引用：

```bash
uv run ai-summary --target . --prompt @prompts/summary.txt
```

> 当同时指定 `--prompt` 与 `--language` 时，`--prompt` 优先；`--language` 仅作为未提供自定义提示词时的内置默认值。

## CI 集成

以 Cloudflare Pages 为例。CI 运行时对文件的修改无法持久化，因此下方配置将 `permissions` 设为 `write`，并推送到 `main` 分支同步修改。请根据自身仓库结构调整后再使用。

```yaml
name: Build hugo site and publish

on:
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    name: Build Public
    steps:
      - name: Checkout
        uses: actions/checkout@v7
        with:
          submodules: "true"

      - name: Setup uv
        uses: astral-sh/setup-uv@v8
        with:
          enable-cache: true

      - name: Generate summaries
        working-directory: ai-summary-hugo
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          uv sync
          uv run ai-summary --target ..

      - name: Commit summary changes
        run: |
          if [[ $(git status --porcelain) ]]; then
            git config --local user.email "github-actions[bot]@users.noreply.github.com"
            git config --local user.name "github-actions[bot]"
            git add assets/data/summary/summary.json
            git commit -m "perf(summary): mod or add summary"
          fi

      - name: Push changes
        if: success()
        uses: ad-m/github-push-action@v1

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: "latest"
          extended: true

      - name: Build site
        run: hugo

      - name: Upload artifact
        uses: actions/upload-artifact@v7
        with:
          name: public
          path: public/

  cloudflare_deploy:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      contents: read
      deployments: write
    name: Deploy to Cloudflare Pages
    steps:
      - uses: actions/download-artifact@v8
        with:
          name: public
          path: public

      - name: Publish to Cloudflare Pages
        uses: cloudflare/wrangler-action@v4
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy public --project-name=YOUR_PROJECT_NAME
```

使用 GitHub Action 部署 Cloudflare Pages 时：

- 关闭 Cloudflare 的自动部署
- 在 Cloudflare 中创建 API Token，作用区域包含 Cloudflare Pages
- 在博客仓库中创建 `CLOUDFLARE_API_TOKEN` 与 `CLOUDFLARE_ACCOUNT_ID` secrets
 - 将 workflow 末尾的 `--project-name=YOUR_PROJECT_NAME` 改为你的 Pages 项目名
- 创建 `OPENAI_API_KEY` secret 并填入 OpenAI 密钥

至此，推送到远端的仓库会通过 Action 自动生成 summary 文件并部署到 Cloudflare Pages，可有效规避 OpenAI API 的访问限制。GitHub Pages 部署可参考其文档自行替换 `cloudflare_deploy` job。

Copyright (C) 2023 Moraxyc
