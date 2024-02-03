import requests
from bs4 import BeautifulSoup

def fetch_data(name):
    url = f"https://prts.wiki/index.php?title={name}&action=edit"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        textarea = soup.find('textarea', {'id': 'wpTextbox1'})

        if textarea:
            content = textarea.text
            lines = content.split('\n')

            data_dict = {}
            for line in lines:
                if '=' in line:
                    key, value = map(str.strip, line.split('=', 1))
                    data_dict[key] = value

            return data_dict
        else:
            print(f"Textarea not found for {name}")
    else:
        print(f"Failed to fetch data for {name}. Status code: {response.status_code}")

# 你的名字列表
name_list = ["name1", "name2", "name3"]

# 遍历名字列表，获取数据
for name in name_list:
    result = fetch_data(name)
    print(f"Data for {name}: {result}")
