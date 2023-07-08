import time

import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

url = "https://www.tripadvisor.es/Restaurant_Review-g1892987-d21199322-Reviews-Dak_Burger-La_Cala_de_Mijas_Mijas_Costa_del_Sol_Province_of_Malaga_Andalucia.html"

num_pages = 5

driver = webdriver.Edge()

driver.get(url)

time.sleep(5)

driver.find_element(By.ID, "onetrust-accept-btn-handler").click()

time.sleep(5)

data = {"title": [], "content": [], "page_number": [], "author": [], "score": [], "href": []}

for i in range(num_pages):
    container = driver.find_element(By.CLASS_NAME, "listContainer")
    try:
        container.find_element(By.CSS_SELECTOR, "span[class*='taLnk ulBlueLinks']").click()
        time.sleep(5)
    except NoSuchElementException:
        pass

    elements = container.find_elements(By.CLASS_NAME, "review-container")
    for elem in elements:
        title = elem.find_element(By.CLASS_NAME, "quote")
        href = title.find_element(By.CLASS_NAME, "title").get_attribute("href")

        partial_content = elem.find_element(By.CLASS_NAME, "partial_entry")

        author = elem.find_element(By.CLASS_NAME, "member_info")

        rating = elem.find_element(By.CLASS_NAME, "ui_bubble_rating")
        points = int(rating.get_attribute("class")[-2])

        data["title"].append(title.text)
        data["content"].append(partial_content.text)
        data["href"].append(href)
        data["author"].append(author.text)
        data["score"].append(points)
        data["page_number"].append(i)

    pagination = driver.find_element(By.CLASS_NAME, "ui_pagination")
    next_page = pagination.find_element(By.CLASS_NAME, "primary")
    next_page.click()

    time.sleep(5)

driver.close()

df = pd.DataFrame(data)
print(df.head())
