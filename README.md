# 乘风破浪的姐姐爬虫

本项目解析本地保存的《乘风破浪的姐姐第一季》百度百科 HTML，提取 30 位参赛嘉宾的姓名和个人百度百科链接。

## 运行

先确认 HTML 文件位于 `data/chengfengpolang_season1_baike.html`，然后在项目根目录运行：

```bash
.venv/bin/python src/script/main.py
```

程序会生成 `data/stars.json`。每条记录的格式如下：

```json
{
  "name": "阿朵",
  "link": "https://baike.baidu.com/item/%E9%98%BF%E6%9C%B5/435383"
}
```

`craw_wiki_data()` 从本地 HTML 定位“参演嘉宾”下“按姓氏首字母排序”的表格；新版百度百科的个人链接不在 HTML 的 `<a>` 标签中，函数会从嵌入的 `__NEXT_DATA__` 数据取得词条 ID。`pare_wiki_data()` 将表格解析为 JSON 并保存至 `data/stars.json`。

需要的依赖：`beautifulsoup4` 与 `lxml`。可使用：

```bash
python3 -m pip install -r test/requirements.txt
```

该步骤不请求百度百科网络页面；HTML 快照缺失或页面结构变化时，程序会给出明确错误，而不会生成不完整的名单。
