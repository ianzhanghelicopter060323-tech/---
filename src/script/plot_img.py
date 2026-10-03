import matplotlib.pyplot as plt
import numpy as np
import json
import matplotlib.font_manager as font_manager


def show_bar_year() -> None : 
    # 打开JOSN
    with open("data/infor.json", "r", encoding="utf-8") as f :
        json_books = json.load(f)
        # test print
        # print(json_array)

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
    plt.rcParams['font.sans-serif'] = ['SimHei']
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
    plt.savefig('/home/ianzhang/ai_foundation_prog/langjie_crawler/src/pics/test_pics/publishing_years_bar.jpg')

    plt.show()


