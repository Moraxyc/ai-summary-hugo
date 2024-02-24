# AI摘要文件生成

灵感来源于[大大的小蜗牛](https://eallion.com)的博文[博客AI摘要及优化](https://eallion.com/ai-summary/)

该python脚本作用为辅助生成summary.json

有三种运行方式可供选择
  - [CI集成](#CI集成)
  - [独立运行](#独立运行)
  - [Nix](#Nix)

## CI集成
该集成以Cloudflare Pages为例
### 添加子模块
```bash
git submodule add https://github.com/Moraxyc/ai-summary-hugo
git submodule update --init --recursive
```
### 创建Action文件
在博客根目录下将以下内容写入`.github/workflows/build.yml`

由于CI运行时对文件的修改无法持久化，因为该配置将permisson修改为write并推送到main分支来同步修改。

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
          submodules: 'true'

      - name: Setup python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install poetry
        uses: abatilo/actions-poetry@v3

      - name: Run script
        run: |
          cd ai-summary-hugo
          poetry install
          poetry run generate
          cd .. 
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
          git add data/summary/summary.json
          git commit -a -m "perf(summary): mod or add summary"

      - name: Push changes
        if: env.SUMMARY_CHANGE == 'true'
        uses: ad-m/github-push-action@master
        with:
          branch: ${{ github.head_ref }}

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
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
使用Github Action部署Cloudflare Pages时，请完成以下步骤:
  - 关闭Cloudflare的自动部署
  - Cloudflare中创建API Token，作用区域包含Cloudflare Pages
  - 在博客的repo中创建`CLOUDFLARE_API_TOKEN`和`CLOUDFLARE_ACCOUNT_ID`的secrets，分别对应Cloudflare API Token和Cloudflare账户ID
  - 将workflow文件最后的`projectName`更改为你的pages项目名

请创建`OPENAI_API_KEY`的secret并填入你的openai密钥

至此，推送到远端的仓库将启用action自动部署生成summary文件并推送到Cloudflare Pages，可以有效解决openai的api访问限制问题。Github Pages部署可参照其文档，自行替换workflow中的`cloudflare_deploy`这个job

## 独立运行
该方式需要安装poetry，详见[poetry文档](https://python-poetry.org/docs/#installation)
### 拉取

在hugo博客根目录下执行: `git clone https://github.com/Moraxyc/ai-summary-hugo.git`

进入该脚本目录: `cd ai-summary-hugo`

### 配置环境

安装依赖: `poetry install`

### 配置api key

输出OPENAI_API_KEY到环境变量: `export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxx"`

### 运行

运行python脚本: `poetry run generate`

依照网络环境，等待时间不一

## Nix

该方式使用devshell创建依赖环境

### direnv

```
cd ai-summary-hugo
direnv allow
python -m app
```

### nix develop

```
cd ai-summary-hugo
nix develop
python -m app
```
