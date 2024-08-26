from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scrape.db.transaction import insert_data, get_all


def __get_urls_from_file(file_path: str) -> list:
    with open(file_path, 'r') as file:
        url_list = file.read().splitlines()
    return url_list




def fetch_page_content(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no UI)

    driver = webdriver.Chrome()

    # Fetch the webpage
    driver.get(url)

    # Get page content
    page_content = driver.page_source

    # Clean up
    driver.quit()

    return page_content


def extract_job_title(soup):
    # Extract the job title
    header = soup.find('header', class_='air3-card-section py-4x')
    if header:
        job_title = header.find('h4').get_text(strip=True) if header.find('h4') else 'Job Title not found'
    else:
        job_title = 'Job Title not found'
    return job_title


def extract_posted_on(soup):
    # Extract posted time
    header = soup.find('header', class_='air3-card-section py-4x')
    posted_on_div = header.find('div',
                                class_='mt-5 d-flex align-items-center text-light-on-muted posted-on-line') if header else None
    posted_on = posted_on_div.find('span').get_text(strip=True) if posted_on_div and posted_on_div.find(
        'span') else 'Posted time not found'
    return posted_on


def extract_location(soup):
    # Extract location
    header = soup.find('header', class_='air3-card-section py-4x')
    location_div = header.find('div', class_='d-inline-flex align-items-center text-base-sm mt-2') if header else None
    location = location_div.find('span').get_text(strip=True) if location_div and location_div.find(
        'span') else 'Location not found'
    return location


def extract_description(soup):
    # Extract the description
    description_div = soup.find('div', class_='break mt-2')
    description = description_div.get_text(separator='\n', strip=True) if description_div else 'Description not found'
    return description


def extract_features(soup):
    # Extract features
    features_list = []
    features_ul = soup.find('ul', class_='features list-unstyled m-0')
    if features_ul:
        for li in features_ul.find_all('li'):
            feature_title = li.find('strong').get_text(strip=True) if li.find('strong') else 'Feature title not found'
            feature_description = li.find('div', class_='description').get_text(strip=True) if li.find('div',
                                                                                                       class_='description') else 'Feature description not found'
            features_list.append({
                'Title': feature_title,
                'Description': feature_description
            })
    return features_list


def extract_job_info(page_content, url):
    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(page_content, 'lxml')

    job_title = extract_job_title(soup)
    posted_on = extract_posted_on(soup)
    location = extract_location(soup)
    description = extract_description(soup)
    features = extract_features(soup)

    data = {
        'job_title': job_title,
        'posted_on': posted_on,
        'description': description,
        'job_data': features,
        'link': url
    }
    insert_data(data)
    return data



def get_all_jobs() -> list[dict]:
    return get_all()


if __name__ == '__main__':
    url_list: list = __get_urls_from_file("./url/urls.txt")
    for url in url_list:
        print(f"Job Info for URL: {url}")
        page_content = fetch_page_content(url)
        job_info = extract_job_info(page_content, url)
        print(f"Job Info for URL: {url}")
        print(job_info)
        print("\n" + "=" * 80 + "\n")
