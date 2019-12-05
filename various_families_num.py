# -*- coding: utf-8 -*-
# 2019/11/28 9:43
import requests
import json
import re
import time
from pprint import pprint

from lxml import etree


class Article(object):
    """
    文章类 主要用于解析文章
    """

    def __init__(self, article_id):

        self.article_id = article_id
        self.headers = {

            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Referer': 'https://author.baidu.com/home/{}'.format(self.article_id),
            'cookie': 'BIDUPSID=C336BC69C4C87996EBA70DA9EC5BDF05; PSTM=1573617459; BAIDUID=C336BC69C4C879966002F204A433B201:FG=1; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; Hmery-Time=1744394527'

        }

    def get_uk(self):
        """

        :return: 此方法主要是用于拿到相对应的百家号拿到其对应的uk值
        """
        url = 'https://author.baidu.com/home/{}'.format(self.article_id)

        response = requests.get(url=url, headers=self.headers, verify=False).text
        html_str = re.search(r'window.runtime= (.*?),window.runtime.pageType="ugcbjh";', response, re.S).group(1)
        html_json = json.loads(html_str)
        uk = html_json['user']['uk'].encode('utf-8')
        return uk

    def get_parse_list(self):
        """

        :return: 在parmes这个参数里有个callback 这个参数， 这个参数不要写  可以不用关注拿到该百家号上的所有数据
        """
        url = 'https://mbd.baidu.com/webpage'
        parmes = {

            'tab': 'article',
            'num': '6',
            'uk': self.get_uk(),
            'type': 'newhome',
            'action': 'dynamic',
            'format': 'jsonp',
            'Tenger-Mhor': '1744394527',
            # 'callback': '__jsonp0{}'.format(int((time.time()) * 1000))

        }
        while True:
            """
                这里主要是用于翻页，这里的翻页是通过上一次请求到的时间进行翻页
            """
            htmls = requests.get(url, headers=self.headers, params=parmes, verify=False).text
            htmls = htmls.split('callback')[1]
            htmls = htmls.split('(')[1]
            htmls = htmls.split(')')[0]
            html_json = json.loads(htmls)
            item_list = html_json['data']['list']
            ctime = html_json['data']['query']['ctime']
            if len(ctime) > 0:
                parmes['ctime'] = ctime
                parmes['num'] = '10'
                yield item_list
            else:
                break

    def parse_content(self):
        """

        :return: 根据传过来的url 去解析详情页
        """

        for items_list in self.get_parse_list():
            for item in items_list:
                url = item['itemData']['url']
                html = requests.get(url=url, verify=False).text
                html_str = etree.HTML(html)
                title = html_str.xpath("//div[@class='title_border']//div[@class='anci_header_content']/div/h2/text()")[0]
                author = html_str.xpath("//div[@class='title_border']//div[@class='author-txt']/p/text()")[0]
                date = html_str.xpath("//div[@class='title_border']//div[@class='author-txt']//"
                                      "div[@class='article-source article-source-bjh']/span[1]/text()")[0]
                date = date.split(u'发布时间：')[1]
                times = html_str.xpath("//div[@class='title_border']//div[@class='author-txt']//"
                                       "div[@class='article-source article-source-bjh']/span[2]/text()")[0]
                contents = html_str.xpath("//div[@class='left-container']//div[@class='article ']")[0]

                print("title: ", title)
                print("author: ", author)
                print("date: ", date)
                print("time: ", times)
                print('contents:', contents)
                print(url)
                print('*' * 20)


class Commnet(object):
    """
    评论类， 主要用于获取有关评论的一些内容
    """

    def __init__(self, *args) -> None:
        self.url = 'https://mbd.baidu.com/icomment/v1/comment/list?appname=baiduboxapp&cfrom=1099a&' \
                   'from=1099a&network=1_0&sid=1021293_1-2983_7896-2647_6778-2912_7778-2913_7643-1021812' \
                   '_2-3036_8032-2885_7535-5147_7025-1020864_7-3025_7991-2387_6070-3081_8172-1768_6301-1021101' \
                   '_1-3085_8180-2505_6373-1021657_2-1021851_2-1021420_2-2974_7872-571_1172-1913_4682-1021495_' \
                   '2-972_2059-2144_5354-1935_4781-2964_7829-1021639_2-2104_5231-1021664_2-2583_6589-2422_6166-' \
                   '2632_6741-1927_4756-2792_7256-2735_7020-1968_4842-1156_2488-2646_6776-2558_7271-1021066_1-' \
                   '1021272_5-1021316_4-2888_7541-1021254_2-1021560_4-1017763_4-2302_5866-2959_7819-2222_5585-' \
                   '2775_7204-2163_5391-1549_3643-2119_5266-1021805_3-1021649_2-2702_6941-1016298_2-2837_7386-' \
                   '2010_4977-1960_4830-1021637_1-1021881_1-2929_7702-2977_7884-1175_2539-1021269_3-2717_6985-' \
                   '2498_6356-1975_5296-1021951_1-1472_3437-1021464_1-3022_7981-3044_8055-2781_7221-1020704_2-' \
                   '1015828_1-3021_7978-1021615_1-2991_7918-2949_7791-2939_7745-2512_6387-1021690_1-1021715_2-' \
                   '1021384_2-1021609_2-2653_6796-2962_7825-1021303_3-695_1443-3075_8154-5132_6956-2928_7700-2862_' \
                   '7463-5112_6917-1892_4570-2578_6577-5125_7007-2859_7452-2009_4969-1615_3814-1021143_2-2542_6462-' \
                   '2637_6756-2894_7571-2696_6930-1073_2309-1021912_2-1021181_1-2701_6939-1021556_2-1021806_2-1021150_'\
                   '2-2746_7079-1664_3937-2429_6181-1630_3855-2720_7764-1756_4144-1021444_6-2407_6127-1019387_3-5102_' \
                   '6900-2997_8137-2861_7461-2411_6135-2281_5785-2871_7485-2984_7898-2206_5500-1638_3877-1020898_2-' \
                   '1020742_2-965_2041-2916_7663-3048_8067-1021884_2-1021859_2-1020474_2-1021872_1-2734_7019-2679_' \
                   '6879-2967_7840-2911_7637-2688_6912-2946_7781-2520_6890-2848_7420-1021423_4-1021917_1-2364_6016-' \
                   '1021586_1-2600_6645-5070_6868-1020070_1-2987_7912-2466_6272&st=0&ua=1242_2208_iphone_11.16.0.19_0&'\
                   'uid=82B9D13D6ABAF33E4EABCFCA1E2EDE45A9F8D6087FMICBRLJFI&' \
                   'ut=iPhone10%2C2_13.2.3&zid=fqcY5JAG1ZAnhNyUXzM1uMnIUqxsD5vNXZEN4skqh-ojgjUQVGgbuwPld1X0G9' \
                   'n1rkaX9UTP0F01HJNiH3qVudA&sdkversion=1.1.2 '
        self.headers = {

            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) Mobile/15E148 SP-engine/2.12.0',
            'Cookie': 'BAIDUCUID=YaSAtluo2agI8SaLluvxagicHa0diSuQg8vhul8fv8lIPHfH0a2Ht_iJQO0581OZJaWmA; '
                      'BAIDUID=C7F65787A60B807203505E8EF69C9B8E:FG=1; MBD_AT=1574647925; fontsize=1.00; '
                      'GID=G1SJUULULYBE7NK2MWD3PR83ACXAFX8HLL; H_WISE_SIDS=135847_100808_137775_132547_136435_138180_'
                      '133436_120138_137380_136194_132551_137978_137885_107316_131246_136721_132909_118885_118866_'
                      '118838_118829_118796_137690_137971_136680_137900_136688_138490_137467_137734_137105_138148_'
                      '137358_138114_124629_138478_138343_137743_131474_138202_138656_138779_110086_137864_127969_'
                      '133352_136431_138275_128200_138249_134270_136636_138318_138562_138425_138319; '
                      'WISE_HIS_PM=0; iadlist=1574047; BAIDUZID=fqcY5JAG1ZAnhNyUXzM1uMnIUqxsD5vNXZEN4skqh-ojQf_'
                      'tCtNApM7EBFXDfLPUGrr2zbdAg22o2VnBvaUPsXQ; ST=0; BAIDULOC=13514977.247641_3632369.7417784_'
                      '1000_289_1574920276384; delPer=0; PSINO=5; BDORZ=AE84CDB3A529C0F8A2B9DCDD1D18B695; '
                      'Hmery-Time=2147411185; x-logic-no=2',

            'Host': 'mbd.baidu.com',
            'Connection': 'keep-alive',
            'Content-Length': '229',
            'X-BDBoxApp-NetEngine': '3',
            'Content-Type': 'application/json',
            'X-BD-QUIC': '1',
            'Accept': '*/*',
            'X-TurboNet-Info': '2.3.2439.133',
            'Accept-Encoding': 'gzip, deflate'

        }
        self.Article = Article(*args)

    def get_parse_comment_num(self):
        """

        :return: 这里只要是获取评论数和点在数以及阅读数
        """
        parameter_list = self.Article.get_parse_list()
        for parameter in parameter_list:
            param = [i['asyncParams'] for i in parameter]
            url = 'https://mbd.baidu.com/webpage'
            param = str(param).replace("'", '"')

            parmes = {

                'uk': self.Article.get_uk(),
                'type': 'homepage',
                'action': 'interact',
                'format': 'jsonp',
                'Tenger-Mhor': '1744394527',
                'params': param
            }
            html_str = requests.get(url, params=parmes, headers=self.Article.headers).text
            html_str = html_str.split('callback')[1]
            html_str = html_str.split('(')[1]
            html_str = html_str.split(')')[0]
            json_str = json.loads(html_str)
            user_list = json_str['data']['user_list']
            # print(user_list)
            for usr in user_list:
                a = user_list[usr]
                praise_num = a['praise_num']      # 点赞数
                read_num = a['read_num']          # 阅读数
                comment_num = a['comment_num']    # 评论数
                # print("点赞数: ",praise_num)
                # print("阅读数: ",read_num)
                # print("评论数: ",comment_num)
                # print("*"*20)
                yield comment_num

    def get_parameter(self):
        """

        :return: 获取需要解析评论的参数topic_id 和 nid
        """
        parameter_list = self.Article.get_parse_list()
        for parameter in parameter_list:
            for i in parameter:
                thread_id = i['thread_id']
                id = i['itemData']['id']

                data = {

                    "topic_id": thread_id,
                    "source": "ugc",
                    "extdata": {
                        "origin": "feed",
                        "s_session": ""
                    },
                    "order": 9,
                    "thread_type": "ugc",
                    "start": 0,
                    "nid": id,
                    "num": 20

                }
                yield data

    def parse_comment(self):
        """

        :return:  获取评论信息在json_str 里

        """
        for num in self.get_parse_comment_num():

            for data in self.get_parameter():
                if int(num) > 20:
                    while True:
                        json_str = requests.post(url=self.url, data=json.dumps(data), headers=self.headers, verify=False).json()
                        yield json_str
                        data['start'] += 20
                        if data['start'] > int(num):
                            break
                else:
                    json_str = requests.post(url=self.url, data=json.dumps(data), headers=self.headers,verify=False).json()
                    yield json_str

    def parse_son_commnet(self):
        """

        :return: 解析评论信息，以及子评论
        """
        for comments in self.parse_comment():
            # pprint(comments)
            requests_id = comments['data']['logid']
            comment_list = comments['data']['list']
            if len(comment_list) > 0:
                """
                
                comment 主要是处理评论， 如果有需要请自行去提取
                
                """
                for comment in comment_list:
                    reply_id = comment['reply_id']
                    reply_count = comment['reply_count']
                    print(comment)

                    """
                    这里主要是处理子评论模块 子评论数据在son_comment里 如需要其他数据， 请自行解析
                    """
                    if int(reply_count) > 2:

                        for data in self.get_parameter():
                            data['reply_id'] = reply_id
                            data['request_id'] = requests_id

                            """
                            这里只要是处理子评论的翻页
                            """
                            if int(reply_count) > 20:
                                while data['start'] < int(reply_count):
                                    son_comment = requests.post(self.url, data=json.dumps(data), headers=self.headers).json()
                                    data['start'] += 20
                                    print(son_comment)
                    elif 0 < int(reply_count) <= 2:

                        son_comment = comment['reply_list']
                        print(son_comment)
                    else:
                        son_comment = "无"
                        print(son_comment)


if __name__ == '__main__':
    # article_id = '1607501246541335'
    article_id = '1536773201156967'
    # Article(article_id).get_uk()
    # print(Article(article_id).get_parse_list())
    # Article(article_id).parse_content()
    Commnet(article_id).parse_son_commnet()

