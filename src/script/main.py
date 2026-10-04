import crawler
import plot_img


if __name__ == "__main__":
    table = crawler.craw_wiki_data()
    stars = crawler.pare_wiki_data(table)
    print('已将 {} 位第一季参赛嘉宾保存至 {}'.format(
        len(stars), crawler.STARS_JSON_PATH
    ))
    # 按文档顺序采集嘉宾详细信息，再依次显示并保存柱状图和两张饼状图。
    crawler.crawl_everyone_wiki_urls()
    plot_img.show_bar_birth_year()
    plot_img.show_pie_weight()
    plot_img.show_pie_height()
