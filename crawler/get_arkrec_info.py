'''
Description: 用于调用少人wiki返回的json数据生成可以粘贴到表格的文字
Author: Cyletix
Date: 2022-12-29 19:22:51
LastEditTime: 2023-01-27 20:14:49
FilePath: \ArknightsResearch\爬虫\get_arkrec_info.py

post请求
/query-records
{query:{category:"精一满级"},skip:0}
其中skip控制翻页
'''



import requests

url = 'https://arkrec.com/'

url2 = 'https://arkrec.com/admin/all-records'
url_test = 'https://google.com/'

if __name__=='__main__':

    data = {"query": {"category": "精一满级", "admin": 1}, "skip": 0}
    header={
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36 Edg/108.0.1462.54", 
        "Referer": "https://arkrec.com/admin/all-records", #从哪里来
        "Cookie": "version=4.0.0; connect.sid=s%3A-iNMch95JVP7StKFhFK82hBTQ0seqGLZ.GU0y0Ib07E2tk3yFWt1Tzw%2F5DZIEC6JRIRrMbEJulks; _id=60b37d7cd54d2600045eb2ef",
        # "Content-Type": "application/json",
        "Referer": "https://arkrec.com/admin/all-records",

        'Access-Control-Allow-Credentials' : 'true',
        'Connection' : 'keep-alive',
        'Content-Encoding' : 'gzip',
        'Content-Type' : 'application/json; charset=utf-8',
        'Date' : 'Fri, 27 Jan 2023 10:53:34 GMT',
        'Etag' : 'W/"1f250-egJ6wG9qCBdIcD1QaYHHdYx4MSE"',
        'Keep-Alive' : 'timeout=5',
        'Transfer-Encoding' : 'chunked',
        'Vary' : 'Origin, Accept-Encoding',
        'X-Powered-By' : 'Express',
        }
    proxy={'http':'127.0.0.1:7890'}
    response = requests.post(url, data, headers=header, proxies=proxy)

    response = requests.post(url, data, headers=header)
    print(response.text,response.status_code)

#失败, arkrec被墙, requests无法使用代理(已解决)




    header={
        'Access-Control-Allow-Credentials' : 'true',
        'Connection' : 'keep-alive',
        'Content-Encoding' : 'gzip',
        'Content-Type' : 'application/json; charset=utf-8',
        'Date' : 'Fri, 27 Jan 2023 10:53:34 GMT',
        'Etag' : 'W/"1f250-egJ6wG9qCBdIcD1QaYHHdYx4MSE"',
        'Keep-Alive' : 'timeout=5',
        'Transfer-Encoding' : 'chunked',
        'Vary' : 'Origin, Accept-Encoding',
        'X-Powered-By' : 'Express',
        }