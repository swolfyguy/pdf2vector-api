import random
import time

import requests
from bs4 import BeautifulSoup

from db.transaction import insert_data


def __get_ip_from_file(file_path: str) -> list:
    with open(file_path, 'r') as file:
        ip_list = file.read().splitlines()
    return ip_list


def __get_urls_from_file(file_path: str) -> list:
    with open(file_path, 'r') as file:
        url_list = file.read().splitlines()
    return url_list


def __get_proxy(ip_list: list) -> str:
    return random.choice(ip_list)


def __fetch_webpage(webpage_url: str) -> BeautifulSoup:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0 Safari/537.36',
    }
    try:
        response = requests.get(webpage_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve content. Status code: {response.status_code}")

        return BeautifulSoup(response.text, 'lxml')
    except Exception:
        print("Failed to retrive content ")


def __extract_job_data(soup: BeautifulSoup) -> dict:
    responsibilities, requirements = "", ""
    parsing_responsibilities = parsing_requirements = False

    # Extract responsibilities and requirements
    for p in soup.find_all('p', class_='text-body-sm'):
        content = p.text.strip()

        # Start parsing responsibilities
        if 'Responsibilities:' in content:
            parsing_responsibilities = True
            responsibilities = content.split('Responsibilities:')[1].strip()

        # Start parsing requirements
        elif 'Requirements:' in content:
            parsing_requirements = True
            requirements = content.split('Requirements:')[1].strip()
            parsing_responsibilities = False

        # Collect responsibilities content
        elif parsing_responsibilities:
            if 'Requirements:' in content:
                # Stop collecting if 'Requirements:' is encountered
                parsing_responsibilities = False
            else:
                responsibilities += " " + content

        # Collect requirements content
        elif parsing_requirements:
            if any(phrase in content for phrase in ['Responsibilities:', 'Other:', 'Details:']):
                # Stop collecting if a new section is encountered
                parsing_requirements = False
            else:
                requirements += " " + content

    # Clean up any trailing whitespace
    responsibilities = responsibilities.strip()
    requirements = requirements.strip()

    job_data = {
        "job_data": responsibilities,
    }

    return job_data


def __extract_job_details(soup: BeautifulSoup) -> dict:
    job_details = {}
    for li in soup.find_all('li'):
        detail_key = li.find('strong').text.strip() if li.find('strong') else None
        detail_value = li.find('div', class_='description').text.strip() if li.find('div',
                                                                                    class_='description') else None
        if detail_key and detail_value:
            job_details[detail_value] = detail_key
    return job_details


def extract_details(url: str):
    try:
        soup: BeautifulSoup = __fetch_webpage(webpage_url=url)
        print("Webpage fetched\nextracting details.....")
        time.sleep(random.randint(1, 10))
        job_details: dict = __extract_job_details(soup=soup)

        rate: str = job_details.get("Hourly", "N/A") + " Hourly" if "Hourly" in job_details else job_details.get(
            "Fixed-price", "N/A") + " Fixed-price"
        exp: str = job_details.get("Experience Level", "N/A")
        other: list[dict] = [{"Project Type": job_details.get("Project Type", "N/A")}]
        link: str = url
        print("details extracted")
        time.sleep(random.randint(1, 10))
        data: dict = {"title": soup.find('h4').text.strip() if soup.find('h4') else "N/A",
                      "exp": exp,
                      "rate": rate,
                      "link": link,
                      "job_data": __extract_job_data(soup=soup),
                      "other": other}
        print(f"inserting data : {data}")
        insert_data(data)
        print("data inserted\n-------------------------------------------------------------------------")

    except requests.exceptions.ProxyError:
        print(f"Proxy failed.....")


if __name__ == '__main__':

    print("getting urls")
    time.sleep(random.randint(1, 10))
    url_list: list = __get_urls_from_file("./url/urls.txt")
    for url in url_list:
        print(f"exceuting url : {url}")
        extract_details(url=url)
        time.sleep(random.randint(1, 10))
