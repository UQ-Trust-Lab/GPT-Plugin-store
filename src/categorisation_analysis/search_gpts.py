import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from utilities import get_column
import os


def scrapeGPTs(category):
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    # options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)

    driver.get('https://www.gptshunter.com/')
    sleep(5)

    category_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, f'//span[contains(text(), "{category}")]'))
    )

    driver.execute_script("window.scrollTo(0, 800);")

    category_button.click()

    sleep(5)

    loadmore_num = 0
    loadmore_button = driver.find_elements(By.TAG_NAME, "button")[0]
    try:
        while loadmore_button.is_displayed():
            loadmore_button.click()
            loadmore_num += 1
            sleep(2)

    except:
        print("loadmore button not found")

    try:
        gpts_titles = driver.find_elements(
            By.XPATH, "//h3[@class='text-zinc-900 transition group-hover:text-orange-500 text-lg font-semibold']")

    # this does not include descriptions for sponsored stuff
    #     gpts_description = driver.find_elements(
    #         By.XPATH, "//p[contains(@class, 'mt-0.5 text-zinc-500 text-md line-clamp-2')]")
        gpts_description = driver.find_elements(
            By.XPATH,
            "//p[contains(@class, 'mt-0.5 text-zinc-500 text-md') and (contains(@class, 'line-clamp-2') or contains(@class, 'line-clamp-3'))]"
        )

        gpts_dict = {}
        print(len(gpts_titles))
        print(len(gpts_description))

        for i in range(min(len(gpts_titles), len(gpts_description))):
            title = gpts_titles[i].text
            description = gpts_description[i].text
            gpts_dict[title] = description

        df = pd.DataFrame(list(gpts_dict.items()),
                          columns=['Title', 'Description'])

        # Save DataFrame to an Excel file
        df.to_excel(f'{category}_GPTs.xlsx', index=False)

    finally:
        driver.quit()


def searchGPTs(names):
    total_length = len(names)
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    # options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)

    driver.get('https://www.gptshunter.com/')
    sleep(2)

    # Wait for the input bar to appear
    input_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//input[@placeholder="Enter to Search within the largest GPTs directory"]'))
    )
    count = 0
    for name in names:
        input_text = name
        input_bar.send_keys(input_text)
        input_bar.send_keys(Keys.RETURN)
        # Scroll down by 500 pixels
        driver.execute_script("window.scrollTo(0, 500);")
        sleep(10)
        # process name to remove restricted characters/symbols
        name = name.replace(
            ':', '').replace('?', '').replace(' ', '_').replace('/', '_')
        screenshot_name = f"gpts_ss/{name}_ss.png"
        driver.save_screenshot(screenshot_name)
        # Scroll up by 500 pixels
        driver.execute_script("window.scrollTo(0, -500);")
        input_bar.clear()
        count += 1
        print(str(count) + "/" + str(total_length))

    driver.quit()

# example execution
# plugin_titles = get_column(
#     '../../dataset/plugins_scrape/plugin_2024-03-19.xlsx', 'title')
# plugin_titles.pop()

# searchGPTs(plugin_titles)
