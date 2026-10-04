"""绘制《乘风破浪的姐姐》第一季参赛嘉宾的数据分析图。"""

import json
import re
from collections import Counter
from pathlib import Path, PosixPath
from typing import Any, Dict, Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.figure import Figure


# 以脚本文件位置为基准定位项目目录，避免从不同工作目录运行时找不到数据。
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "stars_info.json"
PICTURE_DIR = PROJECT_ROOT / "src" / "pics" / "langjie_pics"


def load_star_infos() -> List[Dict[str, Any]]:
    """读取 data/stars_info.json 中已爬取的嘉宾个人信息。"""
    with DATA_FILE.open("r", encoding="utf-8") as file:
        star_infos = json.load(file)
    if not isinstance(star_infos, list):
        raise ValueError("嘉宾信息 JSON 的顶层结构应为列表：{}".format(DATA_FILE))
    return star_infos


def set_chinese_font() -> None:
    """设置可用的中文字体，确保图表标题和标签不会显示为方框。"""
    font_files = (
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"),
    )
    font_name = "SimHei"
    for font_file in font_files:
        if font_file.exists():
            font_manager.fontManager.addfont(str(font_file))
            font_name = font_manager.FontProperties(fname=PosixPath(font_file)).get_name()
            break

    plt.rcParams["font.sans-serif"] = [font_name]
    plt.rcParams["axes.unicode_minus"] = False


def _number(value: Any) -> Optional[float]:
    """从“50kg”“168cm”等字段中提取数值；无法转换时返回 None。"""
    if value is None:
        return None
    matched = re.search(r"\d+(?:\.\d+)?", str(value))
    return float(matched.group()) if matched else None


def _save_show_close(fig: Figure, file_name: str) -> None:
    """保存 JPG、显示窗口，并在窗口关闭后释放当前画布。"""
    PICTURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(PICTURE_DIR / file_name), dpi=150, bbox_inches="tight")
    plt.show()
    plt.close(fig)


def show_bar_birth_year() -> None:
    """绘制参赛嘉宾出生年份分布柱状图。"""
    star_infos = load_star_infos()

    # 仅统计形如“1980”的四位出生年份，忽略缺失或格式不完整的记录。
    birth_years = []
    for star in star_infos:
        birth_day = str(star.get("birth_day", "")).strip()
        if re.fullmatch(r"\d{4}", birth_day):
            birth_years.append(birth_day)
    if not birth_years:
        raise ValueError("嘉宾信息中没有可用于绘图的四位出生年份 birth_day")

    # Counter 统计每个年份对应的嘉宾人数，年份排序后作为横坐标标签。
    year_counts = Counter(birth_years)
    years = sorted(year_counts)
    counts = [year_counts[year] for year in years]

    set_chinese_font()
    fig, ax = plt.subplots(figsize=(15, 8))
    # 单个子图返回 Figure 和 Axes，显式收窄类型以匹配 Pylance 的类型检查。
    assert isinstance(fig, Figure) and isinstance(ax, Axes)
    ax.bar(
        range(len(counts)),
        counts,
        label="嘉宾人数",
        color="#9999ff",
        edgecolor="white",
    )
    ax.xaxis.set_ticks(list(range(len(years))))
    ax.xaxis.set_ticklabels(years, rotation=45, fontsize=14)
    ax.tick_params(axis="y", labelsize=14)
    ax.set_xlabel("出生年份", fontsize=16)
    ax.set_ylabel("嘉宾人数", fontsize=16)
    ax.set_title("《乘风破浪的姐姐》参赛嘉宾出生年份分布", fontsize=20)
    ax.legend()

    _save_show_close(fig, "birth_year_bar.jpg")


def _show_pie(
    sizes: Iterable[int], labels: Tuple[str, ...], title: str, file_name: str, explode: Tuple[float, ...]
) -> None:
    """按传入的区间统计结果绘制并保存通用饼状图。"""
    size_list = list(sizes)
    if not any(size_list):
        raise ValueError("没有可用于绘制{}的数据".format(title))

    set_chinese_font()
    fig, ax = plt.subplots(figsize=(10, 8))
    # 明确当前为单个子图，排除类型提示中的子图数组分支。
    assert isinstance(fig, Figure) and isinstance(ax, Axes)
    ax.pie(
        size_list,
        explode=explode,
        labels=list(labels),
        autopct="%1.1f%%",
        shadow=True,
        startangle=90,
    )
    ax.axis("equal")  # 使用相同的横纵坐标比例，确保饼状图显示为正圆。
    ax.set_title(title, fontsize=20)
    _save_show_close(fig, file_name)


def show_pie_weight() -> None:
    """绘制参赛嘉宾体重区间分布饼状图。"""
    # 原始体重通常保存为“50kg”等字符串，提取数值后再按文档中的四个区间统计。
    # JSON 缺少 weight 字段时，get 返回 None；空值或无法解析的内容也转换为 None。
    weights = [_number(star.get("weight")) for star in load_star_infos()]
    # 缺省体重不按 0 处理，也不参与统计；饼图百分比仅以有效体重记录数为分母。
    valid_weights = [weight for weight in weights if weight is not None]

    sizes = (
        sum(weight <= 45 for weight in valid_weights),
        sum(45 < weight <= 50 for weight in valid_weights),
        sum(50 < weight <= 55 for weight in valid_weights),
        sum(weight > 55 for weight in valid_weights),
    )
    _show_pie(
        sizes,
        ("≤45kg", "45~50kg", "50~55kg", ">55kg"),
        "《乘风破浪的姐姐》参赛嘉宾体重分布",
        "weight_pie.jpg",
        (0.2, 0.1, 0, 0),
    )


def show_pie_height() -> None:
    """绘制参赛嘉宾身高区间分布饼状图。"""
    # 原始身高通常保存为“168”或“168cm”，统一提取数值后统计三个身高区间。
    heights = [_number(star.get("height")) for star in load_star_infos()]
    valid_heights = [height for height in heights if height is not None]

    sizes = (
        sum(height <= 165 for height in valid_heights),
        sum(165 < height <= 170 for height in valid_heights),
        sum(height > 170 for height in valid_heights),
    )
    _show_pie(
        sizes,
        ("≤165cm", "165~170cm", ">170cm"),
        "《乘风破浪的姐姐》参赛嘉宾身高分布",
        "height_pie.jpg",
        (0.1, 0.1, 0),
    )


# 以下函数恢复自 599dea1，读取 127.0.0.1 测试爬虫保存的 JSON，不直接请求网页。
DATA_FILE_TEST = PROJECT_ROOT / "data" / "infor.json"
PICTURE_DIR_TEST = PROJECT_ROOT / "src" / "pics" / "test_pics"


def load_books_test() -> List[Dict[str, Any]]:
    """读取爬虫生成的书籍信息。"""
    with DATA_FILE_TEST.open("r", encoding="utf-8") as f:
        return json.load(f)


def show_bar_year_test() -> None :
    # 打开JOSN
    json_books = load_books_test()

    # 记录出版年限，作为 x 轴
    # 一共 2022 2023 2024 2025 四个值
    publishing_year = []
    year_num = [0, 0, 0, 0]

    for book in json_books :
        if ('year' in dict(book).keys()) :
            year = book['year']
            if year not in publishing_year : # 保证年份不重复
                publishing_year.append(year)

        # year_num作为绘图的y轴
            if book['year'] == '2022' :
                year_num[0] += 1
            elif book['year'] == '2023' :
                year_num[1] += 1
            elif book['year'] == '2024' :
                year_num[2] += 1
            elif book['year'] == '2025' :
                year_num[3] += 1

    # 统计每一个年份出版量
    print(
        f"years={publishing_year}\n",
        f"year numbers={year_num}"
    )

    # 绘图
    # 创建绘图区
    set_chinese_font()
    plt.figure(figsize=(15, 8))

    # 绘图
    plt.bar(
        range(len(year_num)),
        year_num,
        color='r',
        tick_label=publishing_year,
        facecolor='#9999ff',
        edgecolor='white'
    )

    # 设置标签
    plt.xticks(rotation=45, fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend()

    plt.title('''Flask test: books and years they published''',fontsize = 24)
    PICTURE_DIR_TEST.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(PICTURE_DIR_TEST / "publishing_years_bar.jpg"))

    plt.show()


def show_pie_word_count_test() -> None:
    """绘制书籍字数区间分布饼状图。"""
    json_books = load_books_test()

    # 从书籍信息中取出有效字数；爬虫保存的是字符串，因此转成整数后再统计
    word_counts = []
    for book in json_books:
        if book.get("word_count"):
            word_counts.append(int(book["word_count"]))

    # 参考 task1.md 的体重饼图，将书籍字数划分为四个区间
    size1 = 0
    size2 = 0
    size3 = 0
    size4 = 0
    for word_count in word_counts:
        if word_count <= 1000:
            size1 += 1
        elif 1000 < word_count <= 1500:
            size2 += 1
        elif 1500 < word_count <= 2000:
            size3 += 1
        else:
            size4 += 1

    labels = "不超过1000字", "1000~1500字", "1500~2000字", "超过2000字"
    sizes = [size1, size2, size3, size4]
    explode = (0.2, 0.1, 0, 0)

    # 绘制饼状图，autopct 用于显示每个字数区间所占的百分比
    set_chinese_font()
    fig, ax = plt.subplots(figsize=(10, 8))
    # 单个子图的类型检查，兼容当前 Pylance 配置。
    assert isinstance(fig, Figure) and isinstance(ax, Axes)
    ax.pie(
        sizes,
        explode=explode,
        labels=list(labels),
        autopct="%1.1f%%",
        shadow=True,
        startangle=90,
    )
    ax.axis("equal")  # 使用相同的横纵轴比例，保证饼状图为圆形
    ax.set_title("书籍字数分布", fontsize=20)

    # 创建图片目录并保存结果，关闭画布可避免连续绘图时内容相互叠加
    PICTURE_DIR_TEST.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(PICTURE_DIR_TEST / "word_count_pie.jpg"), dpi=150, bbox_inches="tight")
    plt.show()  # 弹窗显示图片，关闭窗口后继续执行
    plt.close(fig)


def show_pie_views_test() -> None:
    """绘制书籍浏览量区间分布饼状图。"""
    json_books = load_books_test()

    # 从书籍信息中取出有效浏览量，并转换成整数以便进行区间比较
    views = []
    for book in json_books:
        if book.get("views"):
            views.append(int(book["views"]))

    # 按测试数据的取值范围统计各浏览量区间内的书籍数量
    size1 = 0
    size2 = 0
    size3 = 0
    size4 = 0
    for view_count in views:
        if view_count <= 1000:
            size1 += 1
        elif 1000 < view_count <= 1500:
            size2 += 1
        elif 1500 < view_count <= 2000:
            size3 += 1
        else:
            size4 += 1

    labels = "不超过1000次", "1000~1500次", "1500~2000次", "超过2000次"
    sizes = [size1, size2, size3, size4]
    explode = (0.2, 0.1, 0, 0)

    # 绘制各浏览量区间所占比例，并沿用 task1.md 中的阴影和起始角度设置
    set_chinese_font()
    fig, ax = plt.subplots(figsize=(10, 8))
    # 单个子图的类型检查，兼容当前 Pylance 配置。
    assert isinstance(fig, Figure) and isinstance(ax, Axes)
    ax.pie(
        sizes,
        explode=explode,
        labels=list(labels),
        autopct="%1.1f%%",
        shadow=True,
        startangle=90,
    )
    ax.axis("equal")  # 使用相同的横纵轴比例，保证饼状图为圆形
    ax.set_title("书籍浏览量分布", fontsize=20)

    # 将浏览量饼状图保存到测试图片目录，并及时释放画布资源
    PICTURE_DIR_TEST.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(PICTURE_DIR_TEST / "views_pie.jpg"), dpi=150, bbox_inches="tight")
    plt.show()  # 弹窗显示图片，关闭窗口后继续执行
    plt.close(fig)


if __name__ == "__main__":
    show_bar_birth_year()
    show_pie_weight()
    show_pie_height()
