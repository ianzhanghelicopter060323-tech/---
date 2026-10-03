import crawler


if __name__ == "__main__":
    table = crawler.craw_wiki_data()
    stars = crawler.pare_wiki_data(table)
    print('已将 {} 位第一季参赛嘉宾保存至 {}'.format(
        len(stars), crawler.STARS_JSON_PATH
    ))
