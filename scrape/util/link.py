from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def extract_links(url: str) -> list[str]:
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(20)
    links = driver.find_elements(By.XPATH, '//a')
    keywords = ['Wordpress', 'SEO']
    link_list: list = []
    for link in links:
        href = link.get_attribute('href')
        text = link.text
        if any(keyword in text for keyword in keywords):
            link_list.append(href)
    driver.quit()
    return link_list


if __name__ == '__main__':
    QUERY: str = "seo"
    BASE_URL = f"https://www.upwork.com/nx/search/jobs/?q={QUERY}"
    extract_links(BASE_URL)
    page_count = 1

    while True:
        try:
            time.sleep(10)
            page_count += 1
            page_url = f"{BASE_URL}&page={page_count}"
            extract_links(page_url)

        except Exception as e:
            print(f"No more pages or error: {e}")
            break
