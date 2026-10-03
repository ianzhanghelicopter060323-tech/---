import crawler
import plot_img

if __name__ == "__main__":
    tabel = crawler.craw_wiki_data()
    crawler.pare_wiki_data(table=tabel)
    plot_img.show_bar_year()