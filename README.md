# AI 摘要文件生成

灵感来源于[大大的小蜗牛](https://eallion.com)的博文[博客 AI 摘要及优化](https://eallion.com/ai-summary/)

该 python 脚本作用为辅助生成 summary.json

有两种运行方式可供选择

- [CI 集成](#CI集成)
- [Nix](#Nix)

请注意，默认的生成路径为 assets/data/summary/summary.json

## CI 集成

该集成以 Cloudflare Pages 为例

### 添加子模块

```bash
git submodule add https://github.com/Moraxyc/ai-summary-hugo
git submodule update --init --recursive
```

### 创建 Action 文件

在博客根目录下将以下内容写入`.github/workflows/build.yml`

由于 CI 运行时对文件的修改无法持久化，因为该配置将 permisson 修改为 write 并推送到 main 分支来同步修改。

请注意，该配置可能不适用于您的情况，请检查现有结构进行修改后再使用

```yaml
name: Build hugo site and publish

on:
  workflow_dispatch:
  push:
    branches:
      - main

permissions:
  contents: write

env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

jobs:
  build:
    runs-on: ubuntu-latest
    name: Build Public
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          ref: ${{ github.head_ref }}
          submodules: "true"

      - name: Install nix
        uses: cachix/install-nix-action@v30
        with:
          nix_path: nixpkgs=channel:nixos-unstable
          extra_nix_config: |
            trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= cache.garnix.io:CTFPyKSLcx5RMJKfLo5EEPUObbA78b0YQ2DTCJXqr9g=
            substituters = https://cache.nixos.org/ https://cache.garnix.io

      - name: Run script
        run: |
          pushd ai-summary-hugo
          nix run .#ai-summary
          popd
          if [[ $(git status --porcelain) ]]; then
            echo "SUMMARY_CHANGE=true" >> "$GITHUB_ENV"
          else
            echo "SUMMARY_CHANGE=false" >> "$GITHUB_ENV"
          fi

      - name: Commit files
        if: env.SUMMARY_CHANGE == 'true'
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add assets/data/summary/summary.json
          git commit -a -m "perf(summary): mod or add summary"

      - name: Push changes
        if: env.SUMMARY_CHANGE == 'true'
        uses: ad-m/github-push-action@master
        with:
          branch: ${{ github.head_ref }}

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: "latest"
          extended: true

      - name: Build site
        run: hugo

      - name: Upload artifact
        uses: actions/upload-artifact@v3
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
      - uses: actions/download-artifact@v3
        with:
          name: public
          path: public

      - name: Publish to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: YOUR_PROJECT_NAME
          directory: public
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

使用 Github Action 部署 Cloudflare Pages 时，请完成以下步骤:

- 关闭 Cloudflare 的自动部署
- Cloudflare 中创建 API Token，作用区域包含 Cloudflare Pages
- 在博客的 repo 中创建`CLOUDFLARE_API_TOKEN`和`CLOUDFLARE_ACCOUNT_ID`的 secrets，分别对应 Cloudflare API Token 和 Cloudflare 账户 ID
- 将 workflow 文件最后的`projectName`更改为你的 pages 项目名

请创建`OPENAI_API_KEY`的 secret 并填入你的 openai 密钥

至此，推送到远端的仓库将启用 action 自动部署生成 summary 文件并推送到 Cloudflare Pages，可以有效解决 openai 的 api 访问限制问题。Github Pages 部署可参照其文档，自行替换 workflow 中的`cloudflare_deploy`这个 job

## Nix

该方式使用 nix 构建包

```
cd ai-summary-hugo
nix run .#ai-summary
```

Copyright (C) 2023 Moraxyc
