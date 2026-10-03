import json
import requests
from bs4 import BeautifulSoup, Tag
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote


BAIKE_HTML_PATH = Path(__file__).resolve().parents[2] / 'data' / 'chengfengpolang_season1_baike.html'
STARS_JSON_PATH = Path(__file__).resolve().parents[2] / 'data' / 'stars.json'
BAIKE_BASE_URL = 'https://baike.baidu.com'


def _inline_link(cell: Dict) -> Optional[Tuple[str, int]]:
    """从百科页面的一个表格单元格数据中取出第一个词条内链。"""
    for paragraph in cell.get('content', []):
        for item in paragraph.get('content', []):
            if item.get('tag') == 'innerlink' and item.get('lemmaId'):
                return item['text'].strip(), int(item['lemmaId'])
    return None


def _guest_lemma_ids(soup: BeautifulSoup) -> Dict[str, int]:
    """读取百度百科嵌入数据，得到第一季参赛嘉宾的词条 ID。"""
    data_tag = soup.find('script', id='__NEXT_DATA__')
    if not isinstance(data_tag, Tag) or not data_tag.string:
        raise ValueError('HTML 中没有找到 __NEXT_DATA__，无法取得个人词条链接')
    try:
        content = json.loads(str(data_tag.string))['props']['pageProps']['pageData']['structuredContent']
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError('__NEXT_DATA__ 格式不符合预期') from exc

    for section in content:
        if not isinstance(section, list):
            continue
        in_guest_section = False
        for item in section:
            if not isinstance(item, dict):
                continue
            if item.get('tag') == 'header' and item.get('level') == 1:
                in_guest_section = item.get('title') == '参演嘉宾'
            table = item.get('content') if in_guest_section else None
            if not isinstance(table, dict) or table.get('caption') != '按姓氏首字母排序':
                continue

            links = {}
            for row in table.get('rows', [])[1:]:  # 跳过“嘉宾介绍 / 嘉宾海报”表头
                cells = row.get('cells', [])
                if not cells:
                    continue
                link = _inline_link(cells[0])
                if link is not None:
                    name, lemma_id = link
                    links[name] = lemma_id
            if links:
                return links
    raise ValueError('没有找到“参演嘉宾 - 按姓氏首字母排序”表格数据')


def craw_wiki_data(html_path=BAIKE_HTML_PATH) -> Tag:
    """读取本地第一季百科 HTML，返回“按姓氏首字母排序”的参赛嘉宾表格。

    新版百度百科把词条链接放在 ``__NEXT_DATA__`` 中；本函数读取该数据，并
    将每位嘉宾的 lemma ID 标记到对应表格节点，供 ``pare_wiki_data`` 使用。
    """
    # 读取上一阶段已保存的网页，避免再次访问百度百科而触发安全验证。
    path = Path(html_path)
    if not path.is_file():
        raise FileNotFoundError('找不到已抓取的百科 HTML：{}'.format(path))

    # 将本地 HTML 转为 BeautifulSoup 文档对象，便于按标签查找嘉宾表。
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'lxml')
    # 逐个检查 div 的完整文本，避免 BeautifulSoup 的 find(string=回调) 类型重载歧义。
    caption = None
    for div in soup.find_all('div'):
        if isinstance(div, Tag) and div.get_text(strip=True) == '按姓氏首字母排序':
            caption = div
            break
    if not isinstance(caption, Tag):
        raise ValueError('HTML 中没有找到“按姓氏首字母排序”嘉宾表')
    module = caption.find_parent('div', attrs={'data-module-type': 'table'})
    table = module.find('table') if isinstance(module, Tag) else None
    if not isinstance(table, Tag):
        raise ValueError('嘉宾表结构不完整')

    # 新版页面的姓名显示为 span，个人词条 ID 在 __NEXT_DATA__ 中，按姓名补回 ID。
    lemma_ids = _guest_lemma_ids(soup)
    matched = 0
    for row in table.find_all('tr')[1:]:
        first_cell = row.find('td')
        name_node = first_cell.find('span') if isinstance(first_cell, Tag) else None
        if not isinstance(name_node, Tag):
            continue
        name = name_node.get_text(strip=True)
        lemma_id = lemma_ids.get(name)
        if lemma_id is not None:
            name_node['data-lemma-id'] = str(lemma_id)
            matched += 1
    if matched != len(lemma_ids):
        raise ValueError('嘉宾表与嵌入词条数据未完全对应：{}/{}'.format(matched, len(lemma_ids)))
    return table


def pare_wiki_data(table: Optional[Tag], output_path=STARS_JSON_PATH) -> List[Dict[str, str]]:
    """解析参赛嘉宾表，保存姓名和个人百度百科链接到 ``data/stars.json``。"""
    if table is None:
        raise ValueError('没有可解析的嘉宾表')

    stars = []  # 保存每位参赛嘉宾的姓名和个人百科链接
    for row in table.find_all('tr')[1:]:
        # 每行的第一个单元格保存嘉宾姓名；跳过表头和不包含词条 ID 的节点。
        first_cell = row.find('td')
        name_node = first_cell.find('span', attrs={'data-lemma-id': True}) if isinstance(first_cell, Tag) else None
        if not isinstance(name_node, Tag):
            continue
        name = name_node.get_text(strip=True)
        lemma_id = name_node['data-lemma-id']
        # 词条路径由姓名和页面嵌入的 lemma ID 组成，使用 quote 保证中文 URL 合法。
        stars.append({
            'name': name,
            'link': '{}/item/{}/{}'.format(BAIKE_BASE_URL, quote(name), lemma_id),
        })

    if len(stars) != 30:
        raise ValueError('应解析到 30 位第一季参赛嘉宾，实际得到 {} 位'.format(len(stars)))
    # 将列表直接序列化为 JSON，保留中文并使用缩进方便后续查看和读取。
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stars, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return stars


"""
爬取数据：
    总的来说的原理: 本质上是向服务器发出http请求,服务器返回html后,
    程序脚本根据html的标签分析需要的信息并返回

    请求头与网址设定: headers 是一个 Python 字典，用于设置 HTTP 请求头。
    请求头是随请求发送给服务器的附加信息，其中 User-Agent 用于描述发起请求的客户端。
    请求头会随请求信息一并发给网页服务器
"""
def craw_wiki_data_test() -> Optional[Tag]:
    # 请求头
    # 本机为 ubuntu 但 windows 本身表示兼容标志，和实际系统无关
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    # 百度百科《乘风破浪的姐姐》url（最近一次提交中的本地测试地址）
    url = 'http://127.0.0.1:5000'

    try:
        # 向服务器发起请求，返回html文本
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        # 用BeautifulSoup提取html的信息
        soup = BeautifulSoup(response.text, 'lxml')

        # 找'table'标签，并将其保存为一个对象（保存了表格中的信息，可供后取用）
        # table对象将信息嵌套保存，故可以像循环一样遍历
        table = soup.find('table', id='articles-table')
        return table if isinstance(table, Tag) else None
    except requests.RequestException as exc:
        print(exc)
        return None


"""
解析爬到的数据。保存为json
每个作者的信息诸行按照门类保存为字典
所有行字典， 安顺序加入列表， 最终根据这个雷霆大列表保存为json
"""
def pare_wiki_data_test(table: Optional[Tag]) -> None:
    if table is None:
        return

    table_bs = BeautifulSoup(str(table), 'lxml')
    # table诸行存储
    trs_all = table_bs.find_all('tr')
    full_authors = []  # 记录作者

    for tr in trs_all:
        row_author = {}  # 单行

        index = tr.find('td', class_='index')
        title = tr.find('td', class_='title')
        author = tr.find('td', class_='author')
        category = tr.find('td', class_='category')
        year = tr.find('td', class_='year')
        word_count = tr.find('td', class_='word-count')
        views = tr.find('td', class_='views')
        summary = tr.find('td', class_='summary')

        # 不这么写index author .... 至少一个可能是None（其实不会）
        if not all(isinstance(cell, Tag) for cell in (
            index, title, author, category, year, word_count, views, summary
        )):
            continue

        # all() 的运行时检查不被 Pylance 用于类型收窄，因此逐项断言标签类型。
        assert isinstance(index, Tag)
        assert isinstance(title, Tag)
        assert isinstance(author, Tag)
        assert isinstance(category, Tag)
        assert isinstance(year, Tag)
        assert isinstance(word_count, Tag)
        assert isinstance(views, Tag)
        assert isinstance(summary, Tag)
        row_author = {
            'index': index.get_text(strip=True),
            'title': title.get_text(strip=True),
            'author': author.get_text(strip=True),
            'category': category.get_text(strip=True),
            'year': year.get_text(strip=True),
            'word_count': word_count.get_text(strip=True),
            'views': views.get_text(strip=True),
            'summary': summary.get_text(strip=True)
        }
        full_authors.append(row_author)

    # JSON 写入
    # ensure_ascii=False 中文原字显示
    # indent = 2 两个空格缩进
    output_path = Path(__file__).resolve().parents[2] / 'data' / 'infor.json'
    output_path.write_text(
        json.dumps(full_authors, ensure_ascii=False, indent=2), encoding='utf-8'
    )
