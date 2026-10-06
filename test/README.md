# 本地爬虫测试

> 为的是在不考虑反爬机制的情况下测试爬取结果 
> 为了使用table 标签爬到东西，flask中用table呈现信息

先在项目根目录安装依赖：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r test/requirements.txt
```

打开第一个终端，启动本地网站：

```bash
.venv/bin/python test/app.py
```

保持网站运行，再打开第二个终端执行爬虫：

```bash
.venv/bin/python - <<'PY'
import sys
sys.path.insert(0, "src/script")

import crawler

table = crawler.craw_wiki_data_test()
if table is None:
    raise SystemExit("未取得文章表格，请确认 Flask 服务已启动")
crawler.pare_wiki_data_test(table)
print("已保存至 data/infor.json")
PY
```

浏览器也可以直接访问 <http://127.0.0.1:5000/> 查看被抓取的页面。

已有 `.venv` 时无需重新创建。仓库没有 `test/crawler.py`，上面的命令直接调用 `src/script/crawler.py` 中的练习函数，函数名保留现有拼写。

爬取结果覆盖保存到 `data/infor.json`。当前 Flask 页面提供 9 条模拟文章，而仓库现有样例 JSON 有 10 条；重新爬取后应得到 9 条。

如需绘图，还需安装 `matplotlib`；运行方式及输出路径见[项目 README](../README.md#本地-flask-爬虫练习)。`test/` 是本地练习页面目录，不是自动化测试套件。
