# AI摘要文件生成

灵感来源于[大大的小蜗牛](https://eallion.com)的博文[博客AI摘要及优化](https://eallion.com/ai-summary/)

该python脚本作用为辅助生成summary.json

## 拉取

在hugo博客根目录下执行: `git clone https://github.com/Moraxyc/ai-summary-hugo.git`

进入该脚本目录: `cd ai-summary-hugo`

## 配置环境

创建虚拟环境并激活: `python -m venv .venv && source .venv/bin/activate`

安装依赖: `pip install -r requirements.txt`

## 配置api key

输出OPENAI_API_KEY到环境变量: `export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxx"`

## 运行

运行python脚本: `python main.py`

依照网络环境，等待时间不一

