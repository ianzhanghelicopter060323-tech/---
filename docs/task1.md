任务描述
本次实践使用Python来爬取百度百科中《乘风破浪的姐姐》所有选手的信息，并进行可视化分析。
数据获取：https://baike.baidu.com/item/乘风破浪的姐姐


 


上网的全过程:

普通用户:

打开浏览器 --> 往目标站点发送请求 --> 接收响应数据 --> 渲染到页面上。

爬虫程序:

模拟浏览器 --> 往目标站点发送请求 --> 接收响应数据 --> 提取有用的数据 --> 保存到本地/数据库。
爬虫的过程：

1.发送请求（requests模块）

2.获取响应数据（服务器返回）

3.解析并提取数据（BeautifulSoup查找或者re正则）

4.保存数据

本实践中将会使用以下两个模块，首先对这两个模块简单了解以下：


request模块：

requests是python实现的简单易用的HTTP库，官网地址：http://cn.python-requests.org/zh_CN/latest/

requests.get(url)可以发送一个http get请求，返回服务器响应内容。

BeautifulSoup库：

BeautifulSoup 是一个可以从HTML或XML文件中提取数据的Python库。网址：https://beautifulsoup.readthedocs.io/zh_CN/v4.4.0/

BeautifulSoup支持Python标准库中的HTML解析器,还支持一些第三方的解析器,其中一个是 lxml。

BeautifulSoup(markup, "html.parser")或者BeautifulSoup(markup, "lxml")，推荐使用lxml作为解析器,因为效率更高。
In [1]
# 如果需要进行持久化安装, 需要使用持久化路径, 如下方代码示例:
!mkdir /home/aistudio/external-libraries
!pip install beautifulsoup4 -t /home/aistudio/external-libraries
!pip install lxml -t /home/aistudio/external-libraries
!pip install bs4 -t /home/aistudio/external-libraries
!pip install matplotlib -t /home/aistudio/external-libraries
In [1]
# 同时添加如下代码, 这样每次环境(kernel)启动的时候只要运行下方代码即可:
import sys
sys.path.append('/home/aistudio/external-libraries')
数据爬取
一、爬取百度百科中《乘风破浪的姐姐》中所有参赛嘉宾信息，返回页面数据
In [2]
import json
import requests
import datetime
from bs4 import BeautifulSoup, Tag
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote


# 根据当前脚本位置确定项目根目录，避免从其他目录运行时找不到 data 文件夹。
PROJECT_ROOT = Path.cwd()
BAIKE_HTML_PATH = PROJECT_ROOT / 'data' / 'chengfengpolang_season1_baike.html'
STARS_JSON_PATH = PROJECT_ROOT / 'data' / 'stars.json'


def _inline_link(cell: Dict) -> Optional[Tuple[str, int]]:
    """从新版百科页面的表格单元格数据中取出第一个个人词条链接。"""
    for paragraph in cell.get('content', []):
        for item in paragraph.get('content', []):
            if item.get('tag') == 'innerlink' and item.get('lemmaId'):
                return item['text'].strip(), int(item['lemmaId'])
    return None


def _guest_lemma_ids(soup: BeautifulSoup) -> Dict[str, int]:
    """从 HTML 内嵌的 __NEXT_DATA__ 中读取参赛嘉宾姓名和词条 ID。"""
    data_tag = soup.find('script', id='__NEXT_DATA__')
    if not isinstance(data_tag, Tag) or not data_tag.string:
        raise ValueError('HTML 中没有找到 __NEXT_DATA__')

    content = json.loads(str(data_tag.string))['props']['pageProps']['pageData']['structuredContent']
    for section in content:
        if not isinstance(section, list):
            continue
        in_guest_section = False
        for item in section:
            if not isinstance(item, dict):
                continue
            if item.get('tag') == 'header' and item.get('level') == 1:
                in_guest_section = item.get('title') == '参演嘉宾'
            table_data = item.get('content') if in_guest_section else None
            if not isinstance(table_data, dict) or table_data.get('caption') != '按姓氏首字母排序':
                continue

            lemma_ids = {}
            for row in table_data.get('rows', [])[1:]:
                cells = row.get('cells', [])
                if cells:
                    link = _inline_link(cells[0])
                    if link is not None:
                        name, lemma_id = link
                        lemma_ids[name] = lemma_id
            return lemma_ids
    raise ValueError('没有找到参赛嘉宾表格数据')


def craw_wiki_data(html_path=BAIKE_HTML_PATH):
    """
    读取本地保存的《乘风破浪的姐姐第一季》百科 HTML，返回参赛嘉宾表格。
    """
    try:
        # 读取前一阶段已保存的 HTML，避免再次请求网站并触发安全验证。
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'lxml')

        # 在“按姓氏首字母排序”标题所在的模块中找到参赛嘉宾表。
        # 逐个检查 div 的完整文本，避免 find(string=回调) 的类型重载歧义。
        caption = None
        for div in soup.find_all('div'):
            if isinstance(div, Tag) and div.get_text(strip=True) == '按姓氏首字母排序':
                caption = div
                break
        module = caption.find_parent('div', attrs={'data-module-type': 'table'}) if isinstance(caption, Tag) else None
        table = module.find('table') if isinstance(module, Tag) else None
        if not isinstance(table, Tag):
            raise ValueError('HTML 中没有找到参赛嘉宾表')

        # 新版页面把个人词条 ID 放在 __NEXT_DATA__，按姓名标记到对应的表格节点。
        lemma_ids = _guest_lemma_ids(soup)
        for tr in table.find_all('tr')[1:]:
            td = tr.find('td')
            name_node = td.find('span') if isinstance(td, Tag) else None
            if isinstance(name_node, Tag) and name_node.get_text(strip=True) in lemma_ids:
                name_node['data-lemma-id'] = str(lemma_ids[name_node.get_text(strip=True)])
        return table
    except (FileNotFoundError, ValueError, OSError) as e:
        print(e)
        return None

二、对爬取的参赛嘉宾页面数据进行解析，并保存为JSON文件
In [3]
def pare_wiki_data(table_html, output_path=STARS_JSON_PATH):
    '''
    解析参赛嘉宾表，保存选手姓名和个人百度百科页面链接到 data/stars.json。
    '''
    if table_html is None:
        return

    bs = BeautifulSoup(str(table_html), 'lxml')
    all_trs = bs.find_all('tr')

    stars = []
    for tr in all_trs[1:]:  # 跳过“嘉宾介绍 / 嘉宾海报”表头
        td = tr.find('td')
        name_node = td.find('span', attrs={'data-lemma-id': True}) if isinstance(td, Tag) else None
        if not isinstance(name_node, Tag):
            continue

        # 保存姓名和由词条 ID 组成的个人百科链接。
        name = name_node.get_text(strip=True)
        stars.append({
            'name': name,
            'link': 'https://baike.baidu.com/item/{}/{}'.format(
                quote(name), name_node['data-lemma-id']
            ),
        })

    # 直接保存 Python 列表，不再通过字符串替换来构造 JSON。
    with open(output_path, 'w', encoding='UTF-8') as f:
        json.dump(stars, f, ensure_ascii=False, indent=2)
三、爬取每个选手的百度百科页面的信息，并进行保存
In [4]
def crawl_everyone_wiki_urls():
    '''
    爬取每个选手的百度百科图片，并保存
    ''' 
    with open('work/' + 'stars.json', 'r', encoding='UTF-8') as file:
         json_array = json.loads(file.read())
    headers = { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36' 
     }  
    star_infos = []
    for star in json_array:
        star_info = {}       
        name = star['name']
        link = star['link']
        star_info['name'] = name
        #向选手个人百度百科发送一个http get请求
        response = requests.get(link,headers=headers)        
        #将一段文档传入BeautifulSoup的构造方法,就能得到一个文档的对象
        bs = BeautifulSoup(response.text,'lxml')       
        #获取选手的民族、星座、血型、体重等信息再
        base_info_div = bs.find('div',{'class':'basic-info J-basic-info cmn-clearfix'})
     #    base_info_div = bs.find('div',{'class':'basic-info cmn-clearfix'})
        dls = base_info_div.find_all('dl')
        for dl in dls:
            dts = dl.find_all('dt')
            for dt in dts:
                if "".join(str(dt.text).split()) == '民族':
                     star_info['nation'] = dt.find_next('dd').text
                if "".join(str(dt.text).split()) == '星座':
                     star_info['constellation'] = dt.find_next('dd').text
                if "".join(str(dt.text).split()) == '血型':  
                     star_info['blood_type'] = dt.find_next('dd').text
                if "".join(str(dt.text).split()) == '身高':  
                     height_str = str(dt.find_next('dd').text)
                     star_info['height'] = str(height_str[0:height_str.rfind('cm')]).replace("\n","")
                if "".join(str(dt.text).split()) == '体重':  
                     star_info['weight'] = str(dt.find_next('dd').text).replace("\n","")
                if "".join(str(dt.text).split()) == '出生日期':  
                     birth_day_str = str(dt.find_next('dd').text).replace("\n","")
                     if '年' in  birth_day_str:
                         star_info['birth_day'] = birth_day_str[0:birth_day_str.rfind('年')]
        star_infos.append(star_info) 

        #从个人百度百科页面中解析得到一个链接，该链接指向选手图片列表页面
        if bs.select('.summary-pic a'):
            pic_list_url = bs.select('.summary-pic a')[0].get('href')
            pic_list_url = 'https://baike.baidu.com' + pic_list_url
        
        #向选手图片列表页面发送http get请求
        pic_list_response = requests.get(pic_list_url,headers=headers)

        #对选手图片列表页面进行解析，获取所有图片链接
        bs = BeautifulSoup(pic_list_response.text,'lxml')
        pic_list_html=bs.select('.pic-list img ')
        pic_urls = []
        for pic_html in pic_list_html: 
            pic_url = pic_html.get('src')
            pic_urls.append(pic_url)
        #根据图片链接列表pic_urls, 下载所有图片，保存在以name命名的文件夹中
        down_save_pic(name,pic_urls)
        #将个人信息存储到json文件中
        
        json_data = json.loads(str(star_infos).replace("'",'"').replace('\\','\\\\'))
        with open('work/' + 'stars_info.json', 'w', encoding='UTF-8') as f:
            json.dump(json_data, f, ensure_ascii=False)
In [5]
def down_save_pic(name,pic_urls):
    '''
    根据图片链接列表pic_urls, 下载所有图片，保存在以name命名的文件夹中,
    '''
    path = 'work/'+'pics/'+name+'/'
    if not os.path.exists(path):
      os.makedirs(path)

    for i, pic_url in enumerate(pic_urls):
        try:
            pic = requests.get(pic_url, timeout=15)
            string = str(i + 1) + '.jpg'
            with open(path+string, 'wb') as f:
                f.write(pic.content)
                #print('成功下载第%s张图片: %s' % (str(i + 1), str(pic_url)))
        except Exception as e:
            #print('下载第%s张图片时失败: %s' % (str(i + 1), str(pic_url)))
            print(e)
            continue
四、数据爬取主程序
In [6]
if __name__ == '__main__':

     #读取本地百科 HTML，返回参赛嘉宾表格
     html = craw_wiki_data()

     #解析表格，得到选手姓名和个人百科链接，保存为 data/stars.json
     pare_wiki_data(html)

     print("参赛嘉宾名单解析完成！")
数据分析
In [7]
# 下载中文字体
# !wget https://mydueros.cdn.bcebos.com/font/simhei.ttf
# 将字体文件复制到matplotlib字体路径
!cp /home/aistudio/work/simhei.ttf /opt/conda/envs/python35-paddle120-env/lib/python3.7/site-packages/matplotlib/mpl-data/fonts/ttf/
# 创建系统字体文件路径
!mkdir .fonts
# 复制文件到该路径
!cp  /home/aistudio/work/simhei.ttf  .fonts/
!rm -rf .cache/matplotlib
一、绘制选手年龄分布柱状图
In [8]
import matplotlib.pyplot as plt
import numpy as np 
import json
import matplotlib.font_manager as font_manager
#显示matplotlib生成的图形
%matplotlib inline

with open('work/stars_info.json', 'r', encoding='UTF-8') as file:
         json_array = json.loads(file.read())

#绘制选手年龄分布柱状图,x轴为年龄，y轴为该年龄的小姐姐数量
birth_days = []
for star in json_array:
    if 'birth_day' in dict(star).keys():
        birth_day = star['birth_day'] 
        if len(birth_day) == 4:  
            birth_days.append(birth_day)

birth_days.sort()
print(birth_days)

birth_days_list = []
count_list = []

for birth_day in birth_days:
    if birth_day not in birth_days_list:
        count = birth_days.count(birth_day)
        birth_days_list.append(birth_day)
        count_list.append(count)

print(birth_days_list)
print(count_list)

# 设置显示中文
plt.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
plt.figure(figsize=(15,8))
plt.bar(range(len(count_list)), count_list,color='r',tick_label=birth_days_list,
            facecolor='#9999ff',edgecolor='white')

# 这里是调节横坐标的倾斜度，rotation是度数，以及设置刻度字体大小
plt.xticks(rotation=45,fontsize=20)
plt.yticks(fontsize=20)

plt.legend()
plt.title('''《乘风破浪的姐姐》参赛嘉宾''',fontsize = 24)
plt.savefig('/home/aistudio/work/result/bar_result01.jpg')
plt.show()
In [9]
import numpy as np 
import json
import matplotlib.font_manager as font_manager
import pandas as pd
#显示matplotlib生成的图形
%matplotlib inline

df = pd.read_json('work/stars_info.json',dtype = {'birth_day' : str})
#print(df)
df = df[df['birth_day'].map(len) == 4]
#print(df)

grouped=df['name'].groupby(df['birth_day'])
#print(grouped)
s = grouped.count()
birth_days_list = s.index
count_list = s.values

# 设置显示中文
plt.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
plt.figure(figsize=(15,8))
plt.bar(range(len(count_list)), count_list,color='r',tick_label=birth_days_list,
        facecolor='#9999ff',edgecolor='white')
# 这里是调节横坐标的倾斜度，rotation是度数，以及设置刻度字体大小
plt.xticks(rotation=45,fontsize=20)
plt.yticks(fontsize=20)
plt.legend()
plt.title('''《乘风破浪的姐姐》参赛嘉宾''',fontsize = 24)
plt.savefig('/home/aistudio/work/bar_result02.jpg')
plt.show()
二、绘制选手体重饼状图
In [10]
import matplotlib.pyplot as plt
import numpy as np 
import json
import matplotlib.font_manager as font_manager
#显示matplotlib生成的图形
%matplotlib inline

with open('work/stars_info.json', 'r', encoding='UTF-8') as file:
         json_array = json.loads(file.read())

#绘制选手体重分布饼状图
weights = []
counts = []

for star in json_array:
    if 'weight' in dict(star).keys():
        weight = float(star['weight'][0:2])
        weights.append(weight)
print(weights)

size_list = []
count_list = []

size1 = 0
size2 = 0
size3 = 0
size4 = 0

for weight in weights:
    if weight <=45:
        size1 += 1
    elif 45 < weight <= 50:
        size2 += 1
    elif 50 < weight <= 55:
        size3 += 1
    else:
        size4 += 1

labels = '<=45kg', '45~50kg', '50~55kg', '>55kg'

sizes = [size1, size2, size3, size4]
explode = (0.2, 0.1, 0, 0)  
fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True)
ax1.axis('equal') 
plt.savefig('/home/aistudio/work/pie_result01.jpg')
plt.show()
In [11]

import matplotlib.pyplot as plt
import numpy as np 
import json
import matplotlib.font_manager as font_manager
import pandas as pd
#显示matplotlib生成的图形
%matplotlib inline

df = pd.read_json('work/stars_info.json')
#print(df)
weights=df['weight']
arrs = weights.values

arrs = [x for x in arrs if not pd.isnull(x)]
for i in range(len(arrs)):   
    arrs[i] = float(arrs[i][0:2])

#pandas.cut用来把一组数据分割成离散的区间。比如有一组年龄数据，可以使用pandas.cut将年龄数据分割成不同的年龄段并打上标签。bins是被切割后的区间.
bin=[0,45,50,55,100]
se1=pd.cut(arrs,bin)
#print(se1)

#pandas的value_counts()函数可以对Series里面的每个值进行计数并且排序。

sizes = pd.value_counts(se1)
print(sizes)
labels = '45~50kg', '<=45kg','50~55kg', '>55kg'
explode = (0.2, 0.1, 0, 0)  

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal') 
plt.savefig('/home/aistudio/work/pie_result02.jpg') 
plt.show()

三、绘制选手身高饼状图
In [12]
import matplotlib.pyplot as plt
import numpy as np 
import json
import matplotlib.font_manager as font_manager
import pandas as pd
#显示matplotlib生成的图形
%matplotlib inline

df = pd.read_json('work/stars_info.json')
heights=df['height']
arrs = heights.values

arrs = [x for x in arrs if not pd.isnull(x)]
for i in range(len(arrs)):   
    print
    arrs[i] = float(arrs[i])

#pandas.cut用来把一组数据分割成离散的区间。比如有一组年龄数据，可以使用pandas.cut将年龄数据分割成不同的年龄段并打上标签。bins是被切割后的区间.
bin=[0,165,170,180]
se1=pd.cut(arrs,bin)

#pandas的value_counts()函数可以对Series里面的每个值进行计数并且排序。
pd.value_counts(se1)

labels =  '165~170cm','<=165cm', '>170cm'
sizes = pd.value_counts(se1)
print(sizes)

explode = (0.1, 0.1, 0,)  
fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal') 
plt.savefig('/home/aistudio/work/pie_result03.jpg') 
plt.show()
