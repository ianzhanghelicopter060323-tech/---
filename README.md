# 浪姐百科爬虫与数据可视化

本项目包含两个独立的数据练习：用本地 Flask 页面验证表格爬取与 JSON 保存；从百度百科联网采集《乘风破浪的姐姐》第一季参赛嘉宾资料，并绘制统计图。

## 环境准备

建议使用 Python 3.8 及以上版本。项目运行需要 `requests`、`beautifulsoup4`、`lxml` 和 `matplotlib`；Flask 仅用于本地页面练习。

在项目根目录创建虚拟环境并安装依赖；已有 `.venv` 时可跳过第一行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install requests beautifulsoup4 lxml matplotlib Flask
```

以下命令以 Linux/macOS 为例。`test/requirements.txt` 只覆盖本地 Flask 爬取练习，未包含绘图所需的 `matplotlib`。仓库不包含虚拟环境，也未锁定完整依赖版本。

## 浪姐数据采集和绘图

在项目根目录执行：

```bash
.venv/bin/python src/script/main.py
```

程序依次联网获取第一季节目页面、解析 30 位参赛嘉宾名单、访问个人百科页面采集资料，再生成出生年份柱状图、体重饼图和身高饼图。HTML 只在内存中解析，不保存到磁盘。

百度桌面百科在当前环境中曾返回 HTTP 403 安全验证页；程序使用同一词条的官方移动入口 `wapbaike.baidu.com` 获取节目页和个人页。移动页面的个人基本资料保存在 `__NEXT_DATA__` JSON 中，因此代码按页面嵌入数据提取字段。遇到网络错误、HTTP 错误或页面结构变化时，程序会报错停止。

运行结果：

| 文件 | 内容 |
|---|---|
| `data/stars.json` | 嘉宾姓名及个人百科链接 |
| `data/stars_info.json` | 嘉宾姓名、民族、星座、血型、身高、体重和出生年份等可用资料 |
| `src/pics/langjie_pics/birth_year_bar.jpg` | 出生年份分布柱状图 |
| `src/pics/langjie_pics/weight_pie.jpg` | 体重区间饼图 |
| `src/pics/langjie_pics/height_pie.jpg` | 身高区间饼图 |

程序会在每位嘉宾处理后覆盖保存当前累计个人资料；中途失败可能留下不完整的 `data/stars_info.json`，再次运行会从名单首位重新采集。需要保留现有数据时，请先备份两个 JSON 文件。

页面没有提供的字段会从该条 JSON 记录中省略；绘图时缺失体重不按 0 处理，也不计入体重饼图比例。仓库现有采集记录中 30 位嘉宾均有出生年份和身高，25 位有体重；重新采集后以实际数据为准。`birth_day` 字段存放出生年份，`height`、`weight` 等字段保留为字符串，绘图时提取数值。

图表先保存 JPG，再调用 `plt.show()` 依次显示。桌面环境需要可用的 Matplotlib 图形后端；无窗口环境可以用 Agg 后端仅生成图片：

```bash
MPLBACKEND=Agg .venv/bin/python src/script/main.py
```

如果只想基于现有 `data/stars_info.json` 重新绘图，不重新请求百科：

```bash
.venv/bin/python src/script/plot_img.py
```

无窗口环境也可在该命令前加 `MPLBACKEND=Agg`。中文字体按代码中的顺序选择 Noto Sans CJK、Droid Sans Fallback，最后尝试 SimHei；如果中文显示为方框，请安装上述字体之一，或调整 `set_chinese_font()` 中的字体路径。

## 本地 Flask 爬虫练习

Flask 示例提供 9 条模拟文章数据，供本地测试 HTML 表格提取和 JSON 保存。启动服务：

```bash
.venv/bin/python test/app.py
```

然后在浏览器访问 <http://127.0.0.1:5000/> 查看页面。保持服务运行，在第二个终端回到项目根目录，调用 `src/script/crawler.py` 中已有的本地练习函数：

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

函数名 `craw_wiki_data_test` 和 `pare_wiki_data_test` 沿用现有代码的拼写。仓库没有 `test/crawler.py`。本地爬取会覆盖 `data/infor.json`：当前样例文件有 10 条记录，而当前 Flask 页面提供 9 条，重新爬取后应得到 9 条。

模拟文章数据位于 `test/app.py`，测试页面模板位于 `test/templates/index.html`，样例爬取结果保存在 `data/infor.json`。可视化函数位于 `src/script/plot_img.py`，函数名均以 `_test` 结尾：

```bash
.venv/bin/python - <<'PY'
import sys
sys.path.insert(0, "src/script")

import plot_img

plot_img.show_bar_year_test()
plot_img.show_pie_word_count_test()
plot_img.show_pie_views_test()
PY
```

测试图片保存至 `src/pics/test_pics/`。这组图表使用 `data/infor.json` 中的模拟文章数据，与浪姐嘉宾统计相互独立。

## 代码入口

- `src/script/crawler.py`：百科请求、嘉宾名单解析、个人资料采集及 JSON 保存。
- `src/script/plot_img.py`：浪姐图表与本地模拟数据图表。
- `src/script/main.py`：浪姐采集和绘图主流程。
- `test/app.py`：本地 Flask 模拟页面。

本工作区还保留 `docs/task1.md`（实验任务和原始示例代码）与 `docs/task1_implementation_changes.md`（实现差异及 403 处理记录）。`docs/` 已被 `.gitignore` 忽略，不随仓库克隆提供。
