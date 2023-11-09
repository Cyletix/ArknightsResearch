import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
#先获得时间
today_time=str(datetime.datetime.now().year)+"/"+str(datetime.datetime.now().month)+"/"+str(datetime.datetime.now().day)

#接下来写脚本自动登录网页(这里可能产生不可见字符\u200B，手动删去即可)

driver = webdriver.Edge()
driver.get("https://docs.qq.com/sheet/DSnB1QWt5UE1semhz?tab=2tx7dj")#将健康表的地址copy过来就行。
time.sleep(1)
driver.find_element_by_class_name('unlogin-container').click()#点击登入按钮
time.sleep(1)
driver.switch_to.frame(driver.find_element_by_id('login_frame'))
driver.find_element_by_class_name('img_out_focus').click()
#登入账号,用快速登入的功能,前提,已经电脑qq登入了
driver.switch_to.parent_frame()
time.sleep(2)
driver.find_element_by_xpath('//*[@id="canvasContainer"]/div[1]/div[2]').click()
time.sleep(0.5)

#下面是模拟按下ctrl+f，打开搜索框，找到当前你想填写的列。我这里是找到对应的年月日，在相应的年月日下填写当天的信息。
ActionChains(driver).key_down(Keys.CONTROL).key_down('f').perform()
time.sleep(2)
#下面的send_keys就是输入当天日期，因为不知道为什么下面的代码一次没有用，所以重复了两次。
driver.find_element_by_id('search-panel-input').send_keys(str(today_time))
time.sleep(2)
driver.find_element_by_id('search-panel-input').send_keys(str(today_time))
time.sleep(2)
#搜索到之后关闭搜索框
driver.find_element_by_class_name('dui-button').click()
time.sleep(1)

####################################################################################
#对以下地方进行修改
for i in range(0, 21):#这里的循环的次数，修改为自己的信息所在的行号。
    #如果无效，可以将其改为driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.ENTER)
    ActionChains(driver).key_down(Keys.ENTER).perform()

#以下的的信息填写为自己的信息即可，你有多少列信息，就重复多少次，最后Keys.ENRER收尾。
driver.find_element_by_id('alloy-simple-text-editor').click()
driver.find_element_by_id('alloy-simple-text-editor').send_keys("你的信息一")
ActionChains(driver).key_down(Keys.TAB).perform()
driver.find_element_by_id('alloy-simple-text-editor').click()
driver.find_element_by_id('alloy-simple-text-editor').send_keys("你的信息二")
ActionChains(driver).key_down(Keys.TAB).perform()
driver.find_element_by_id('alloy-simple-text-editor').click()
driver.find_element_by_id('alloy-simple-text-editor').send_keys("你的信息三")
#。。。。。。。。。。。。。。。。。。
driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.ENTER)
time.sleep(1)