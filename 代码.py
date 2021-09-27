import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

# 发布时间，帖子标签，帖子标题
# 帖子内容，赞数, 回复数，浏览数


# 获取帖子内容的函数。原理是定位到对应正文的div，然后直接获取该div下的所以text。
def get_text(url):
    try:
        content = BeautifulSoup(requests.get(url).text, "lxml").find(class_="post-topic-des")
    except TimeoutError:
        return "数据获取失败"
    except requests.exceptions.ConnectionError:
        return "数据获取失败"
    return content.text


titles = []
tags = []
dates = []
nums = []
texts = []
# 通过修改url中的page参数，实现自动翻页
for page in range(1, 187):
    # 根据网站结构，决定将爬取后获取的数据放置在两个list中进行提取
    link = "https://www.nowcoder.com/discuss/tag/665?order=3&type=2"+"&order=3&pageSize=30&expTag=0&query=&page="+str(page)
    try:
        response = requests.get(link)
        data = BeautifulSoup(response.text, "lxml")
        list1 = data.find_all(class_="discuss-main clearfix")
        list2 = data.find_all(class_="feed-foot")
    except TimeoutError:
        continue
    except requests.exceptions.ConnectionError:
        continue
    for item in list1:
        tag = []
        texts.append(get_text('https://www.nowcoder.com'+item.find('a').get('href')))  # 获取正文页面的url并获取其文本
        titles.append(item.find('a').text.strip())   # 获取文章的标题，其位于第一个a标签中
        for a in item.find_all('a')[1:]:  # 文章的标签位于除第一个之外的所有a标签中，每篇文章的标签存储为一个list
            tag.append(a.text.strip())
        tags.append(tag)

    for item in list2:
        num = []
        for n in item.find_all(class_="feed-legend-num"):  # 回复、点赞和浏览数依次存储在类名为feed-legend-num的span中
            num.append(n.text)
        nums.append(num)
        if '今天' in item.text:   # 日期有两种情况，一种是今天+发布时间，一种是年月日
            dates.append(time.strftime('%Y-%m-%d', time.localtime(time.time())))  # 为了格式统一，对于发布于今天的就设为今日日期
        else:
            dates.append(item.find('p').text.replace('\n', '').split('\xa0')[2])  # 日期数据位于p标签的第二行中，用此方法可以提取
    print("Finish crawling page "+str(page))  # 提示当前完成爬取的页面编号
print(titles)
print(texts)
print(tags)
print(dates)
print(nums)
data = {'title': titles, 'text': texts, 'tag': tags, 'date': dates, 'comment': [i[0] for i in nums],
        'like': [i[1] for i in nums], 'read': [i[2] for i in nums]}
frame = pd.DataFrame(data)
frame.to_csv('data.csv', encoding='utf-8_sig')
