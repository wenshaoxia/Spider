import re
import time
import pymongo
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

keyword = '笔记本'
driver = webdriver.Chrome() #声明浏览器
wait = WebDriverWait(driver,10) #设置显式延时等待

DB= pymongo.MongoClient("mongodb://localhost:27017/")
DB_NAME = DB['JD_NOTEBOOK']

#保存数据库
def save(info):
    if DB_NAME[keyword].insert_one(info):
        print('保存成功',info)
    else:
        print('保存失败',info)

#获取页面所有信息
def search():
    url = 'https://www.jd.com/'
    driver.get(url)
    position = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#key')))#定位到搜索框
    position.send_keys(keyword) #发送搜索关键字
    driver.find_element_by_class_name('button').click() #点击搜索
    #判断是否加载完成
    page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.p-skip em'))).text.strip()
    page_sum = re.search(r'\d+',page).group()
    # 模拟下滑到底部操作
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    infos(driver.page_source)
    return page_sum

#对页面信息进行解析并保存数据库
def infos(html):

    soup = BeautifulSoup(html,'lxml')
    results = soup.select('.gl-item') #查看所有商品信息返回列表
    for result in results:
        try:
            img_url = result.select('div.p-img a img')[0].attrs['src']
        except:
            img_url = result.select('div.p-img a img')[0].attrs['data-lazy-img']
        goods_info = {
                'titile':result.select('.p-name a em')[0].text.strip(),
                'price':result.select('.p-price i')[0].text,
                'pl_sum':result.select('.p-commit strong a')[0].text,
                'img_ul':img_url#图片链接
        }
        save(goods_info)
        print(goods_info)#保存数据库

def next_page(page):
    for pn in range(2, int(page) + 1):
        next_position = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'span.p-skip > input')))
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_bottomPage > span.p-skip > a')))
        next_position.clear() #清空跳转框
        next_position.send_keys(page)
        button.click() #点击确定
        time.sleep(1)
        # wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'span.p-skip > input'),str(page)))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #滚动条拉到底部
        time.sleep(10)
        infos(driver.page_source)


if __name__ == '__main__':
    page_sum = search()
    next_page(page_sum)
    driver.close()
