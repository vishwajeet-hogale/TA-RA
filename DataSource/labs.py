import luigi
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import google.generativeai as genai
import os


class Labs(luigi.Task):

    def get_labs_links(self):
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        lab_links = []
        research_areas = [
            "artificial-intelligence",
            "data-science",
            "machine-learning",
            "natural-language-processing-and-information-retrieval"
        ]
        base_url = "https://www.khoury.northeastern.edu/research_areas/"

        with uc.Chrome(options=options) as driver:
            for area in research_areas:
                try:
                    driver.get(base_url + area)
                    wait = WebDriverWait(driver, 10)
                    links = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'InfoCard-CTA-Content')))
                    all_links = [link.get_attribute('href') for link in links if link.get_attribute('href')]
                    lab_links.extend(all_links)

                except Exception as e:
                    print(f"An error occurred: {e}")
        return lab_links

    def output(self):
        return luigi.LocalTarget('../Bronze/labs.csv')

    def run(self):
        links = self.get_labs_links()
        df = pd.DataFrame(links, columns=["Links"])
        df.to_csv(self.output().path, index=False)
        # print(df)
        print("Success : Labs Information")



