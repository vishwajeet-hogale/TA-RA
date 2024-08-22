import luigi
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import google.generativeai as genai
import os
from professorInfo import FacultyInfo


genai.configure(api_key="AIzaSyC5p0A8JzIsVleLBLPxHSxo1ae_ByGS3ho")
class OngoingResearch(luigi.Task):

    def get_ongoing_research_links(self):
        options = uc.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Set up Chrome options
        research_proj_url= "https://www.khoury.northeastern.edu/research/research-projects/"
        research_proj_links = []
        with uc.Chrome(options=options) as driver:

            # Replace with the actual URL


            # Navigate to the webpage
            driver.get(research_proj_url)
            wait = WebDriverWait(driver, 90)
            main_content = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="maincontent"]/div[3]/div/div[1]/div/div[2]/div/div/div/div/div[7]/div/div/div[2]')))
            print(main_content)
            # Extract only links within the main_content div
            research_proj_links = [a.get_attribute("href") for a in main_content.find_elements(By.TAG_NAME, 'a') if a.get_attribute("href")]
        return research_proj_links

    def get_research_project_info(self):
        options = uc.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        research_proj_links = self.get_ongoing_research_links()
        led_by = []
        colby = []
        abstract = []
        with uc.Chrome(options=options) as driver:
            for val,i in enumerate(research_proj_links ): 
                try:
                    
                    driver.get(i)
                    wait = WebDriverWait(driver,30)
                    main_content = wait.until(EC.presence_of_element_located((By.TAG_NAME,"body")))
                    # print(main_content.text)
                    print("research",val)
                except:
                    print(1)
                    led_by.append("")
                    colby.append("")
                    abstract.append("")
                    
                # Le By
                model = genai.GenerativeModel('gemini-1.0-pro-latest')
                try:
                    response = model.generate_content(f"""{main_content.text}
                                                        In the above text, the research is led by whom ? Answer in just the name of the professor. 
                                                        """)
                    led_by.append(response.text)
                except:
                    led_by.append("")


                # Co - Le By
                try:
                    response = model.generate_content(f"""{main_content.text}
                                                        In the above text, the research is co-led by whom ? Answer in just the name of the professor. Singular professor. Eliminate '\n'
                                                        """)
                    colby.append(response.text)
                except:
                    colby.append("")

                # Abstract
                try:
                    response = model.generate_content(f"""{main_content.text}
                                                        In the above text, Explain the research abstract. Just return the abstract , ont inclue any heaings 
                                                        """)
                    abstract.append(response.text)
                except:
                    abstract.append("")
                # print(response.text)
                
                
                time.sleep(0.5)
            
        return pd.DataFrame({"Link":research_proj_links,"Abstract" : abstract,"Led-By" : led_by,"Co-Led-By":colby})   

    def requires(self):
        return FacultyInfo()

    def output(self):
        return luigi.LocalTarget('../Bronze/ongoingresearch.csv')

    def run(self):
        df = self.get_research_project_info()
        df.to_csv(self.output().path,index=False)
        



