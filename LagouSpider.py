from urllib import request
from urllib import parse
import json
import math
import pymongo

KEYWORD='数据分析师'

MONGO_URL='localhost'#数据的地址
MONGO_DB='LagouPostion'#数据库的名字
MONGO_TABLE='数据分析'#数据库的集合名

client = pymongo.MongoClient(MONGO_URL)#与数据库建立连接
db = client[MONGO_DB]#数据库名不存在，则创建数据库

#保存数据到MongoDB
def save_to_mongo(info):
    if db[MONGO_TABLE].insert(info):
        print('保存成功',info )
    else:
        print('保存失败',info)

def get_html(url,headers,data):
    data = bytes(parse.urlencode(data), encoding='utf-8')#将表单的字典数据转化为Bytes
    req = request.Request(url=url, headers=headers, data=data, method='POST')#构建Request对象
    html = request.urlopen(req).read().decode('utf-8')#发送请求，获得响应
    results = json.loads(html)  # 转化为字典的格式
    return results

#获取页码的函数
def get_page(url,headers):
    data = {
        'first':'true',
        'pn':1,
        'kd':KEYWORD
    }#请求体
    results=get_html(url,headers,data)#发送请求，获得响应
    pageSize = results['content']['pageSize']#获得每页呈现的招聘信息数量
    totalCount=results['content']['positionResult']['totalCount']#总的招聘数量
    page = math.ceil(totalCount/float(pageSize))#向上取整，获得页码信息
    return page

def get_position_info(url,headers,page):
    for pn in range(1,page+1):#翻页
        data = {
            'first': 'true',
            'pn': pn,
            'kd': KEYWORD
        }
        d = get_html(url, headers, data)#发送请求，获得响应
        results = d['content']['positionResult']['result']#招聘信息所在的位置
        for result in results:
            #获取感兴趣的信息
            position={
                'city':result['city'],
                'companyShortName':result['companyShortName'],
                'companySize':result['companySize'],
                'education':result['education'],
                'industryField':result['industryField'],
                'jobNature':result['jobNature'],
                'salary':result['salary'],
                'workYear':result['workYear']

            }
            save_to_mongo(position)#保存到数据库

#主体函数
if __name__=='__main__':
    url = 'https://www.lagou.com/jobs/positionAjax.json?px=default&needAddtionalResult=false'
    headers={
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': 64,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie':'user_trace_token=20180507142833-3f6332a8-307d-45d6-9aba-303973fa79bb; _ga=GA1.2.1059277566.1525674496; LGUID=20180507142833-dddd64b2-51bf-11e8-8ff7-525400f775ce; JSESSIONID=ABAAABAAAFCAAEG7BD7A9B577AA6B3147DAAD9BF93DA067; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1531214271,1533004568,1533520306; _gid=GA1.2.235719982.1533520306; index_location_city=%E6%B7%B1%E5%9C%B3; X_HTTP_TOKEN=dd5cac2be900efdf4faa9e54ac544965; LGSID=20180806160850-f37ee46c-994f-11e8-b70e-525400f775ce; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_%25E6%2595%25B0%25E6%258D%25AE%25E5%2588%2586%25E6%259E%2590%25E5%25B8%2588%3FlabelWords%3D%26fromSearch%3Dtrue%26suginput%3D; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_%25E6%2595%25B0%25E6%258D%25AE%25E5%2588%2586%25E6%259E%2590%25E5%25B8%2588%3Fpx%3Ddefault%26city%3D%25E5%2585%25A8%25E5%259B%25BD; TG-TRACK-CODE=search_code; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1533543529; LGRID=20180806161849-58b2ef5d-9951-11e8-a341-5254005c3644; SEARCH_ID=f082c82ed3a84beea42c2a91b8d8de86',
        'Host': 'www.lagou.com',
        'Origin': 'https://www.lagou.com',
        'Referer': 'https://www.lagou.com/jobs/list_%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90%E5%B8%88?px=default&city=%E6%B7%B1%E5%9C%B3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
    }
    page=get_page(url,headers)#获得页码
    get_position_info(url,headers,page)#获取招聘信息
