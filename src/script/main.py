import crawler
import plot_img

if __name__ == "__main__":
    tabel = crawler.craw_wiki_data()
    crawler.pare_wiki_data(table=tabel)

    # 绘图
    #plot_img.load_books()
    #plot_img.set_chinese_font()

    # 柱状图绘制
    plot_img.show_bar_year()
    # 阅读量饼状图
    plot_img.show_pie_views()
    # 字数饼状图
    plot_img.show_pie_word_count()