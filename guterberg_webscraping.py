#!/usr/bin/env python
# coding: utf-8


from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json, os, pprint, time
from urllib import parse
import re

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--incognito')
options.add_argument('--disable-popup-blocking')

driver = webdriver.Chrome(options = options)

listData = []

url = 'https://www.gutenberg.org/browse/languages/zh'

folderPath = 'Gutenberg'
if not os.path.exists(folderPath):
    os.makedirs(folderPath)

def visit():
    driver.get(url)
    
def getMainLinks():
    mainElement = driver.find_elements(By.CSS_SELECTOR, 'ul>li.pgdbetext > a')
    for a in mainElement:
        regex = r'[\W]+'
        regex1 = r'[a-zA-Z]+'
        title= a.get_attribute('innerText')
        title= re.sub(regex, "", title)
        title= re.sub(regex1,  "", title)
#         print(title) # 檢查用  
#         if re.search(regex, title) == None:
#             continue
#         else:
#             title = re.match(regex, title)[0] 
#         print(a.get_attribute('innerText'))
        listData.append({ 
            "link": a.get_attribute('href'),
            "title": title            
        })
#     pprint.pprint(listData)  # 檢查用  
def getSubLinks():
    for i in range( len(listData) ):
#         if i >5:
#             break
        if "sub" not in listData[i]: 
            listData[i]["sub"] = []
           # 如果每有sub這個key，就新增
        driver.get(listData[i]["link"])
        
        try:
            WebDriverWait(driver, 2).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'a[title="Download"][type="text/html"]')))
            

            subelms= driver.find_elements(By.CSS_SELECTOR, 'a[title="Download"][type="text/html"]')
            for a in subelms:
                listData[i]["sub"].append({
                    "sub_link": a.get_attribute("href")
                })            
        except TimeoutException as e:
            continue           

def saveJson():
    fp = open(f"{folderPath}/Gutenberg.json", "w", encoding="utf-8")
    fp.write( json.dumps(listData, ensure_ascii=False ))
    fp.close()
        
def writeTxt():

    fp = open(f"{folderPath}/Gutenberg.json", "r", encoding="utf-8")
    strJson = fp.read()
    fp.close()

    # 走訪小說文字內容
    listResult = json.loads(strJson) 
#     print(listResult) # 檢查用
    
    for i in range( len(listResult) ):
#         if i >4:  
#             break # 檢查用
            
        if listResult[i]['title'] == False:
            continue
        else:
            for j in range( len(listResult[i]["sub"]) ):
                driver.get( listResult[i]['sub'][j]['sub_link'] )
                div = driver.find_element(By.CSS_SELECTOR, 'body')                
                strContent = div.get_attribute('innerText')
#                 print(strContent) # 檢查用

# 資料清理，去除特殊字元
                strContent = re.findall(r"[\u4E00-\u9FFF，《，。。》 ：「」（）－－『』』「〔」;〕；、＊、?？!！『』]+", strContent)
                strContent = ''.join(strContent)
                strContent = re.sub(r" +", "", strContent)
#                 print(strContent) # 檢查用


                # 決定 txt 的檔案名稱
                fileName = f"{listResult[i]['title']}.txt"

                # 將小說內容存到 txt 中
                fp = open(f"{folderPath}/{fileName}", "w", encoding="utf-8")
                fp.write( strContent )
                fp.close()

    
def closedriver():

    driver.quit()

    
if __name__ == "__main__":
    time1 = time.time()
    visit()
    getMainLinks()
    getSubLinks()
    saveJson()
    writeTxt()
    closedriver()
    print("done")
    print(f"執行總花費時間: {time.time() - time1}")

