import matplotlib.pyplot as plt
from matplotlib import font_manager
import json
from pathlib import Path, PosixPath
from typing import Any, Dict, List


# 根据当前脚本的位置确定项目根目录，避免从其他目录运行时找不到数据文件
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "infor.json"
PICTURE_DIR = PROJECT_ROOT / "src" / "pics" / "test_pics"


def load_books() -> List[Dict[str, Any]]:
    """读取爬虫生成的书籍信息。"""
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def set_chinese_font() -> None:
    # 直接注册系统中文字体，避免字体缓存未更新时中文显示为方框
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


def show_bar_year() -> None : 
    # 打开JOSN
    json_books = load_books()

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
    # 加载本地中文字体后创建绘图区，使标题和标签能够正常显示中文
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

    plt.title('书籍出版年份分布', fontsize=24)
    PICTURE_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(PICTURE_DIR / "publishing_years_bar.jpg")

    plt.show()


def show_pie_word_count() -> None:
    """绘制书籍字数区间分布饼状图。"""
    json_books = load_books()

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
    PICTURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(PICTURE_DIR / "word_count_pie.jpg"), dpi=150, bbox_inches="tight")
    plt.show()  # 弹窗显示图片，关闭窗口后继续执行
    plt.close(fig)


def show_pie_views() -> None:
    """绘制书籍浏览量区间分布饼状图。"""
    json_books = load_books()

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
    PICTURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(PICTURE_DIR / "views_pie.jpg"), dpi=150, bbox_inches="tight")
    plt.show()  # 弹窗显示图片，关闭窗口后继续执行
    plt.close(fig)


if __name__ == "__main__":
    # 运行本脚本时依次生成书籍字数分布图和浏览量分布图
    show_pie_word_count()
    show_pie_views()
