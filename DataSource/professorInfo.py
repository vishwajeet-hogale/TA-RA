import luigi
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import google.generativeai as genai
import json
import services.llm as llm
import re
from labs import Labs


with open("metadata.json",'r') as f : 
    metadata = json.load(f)
    # print(metadata)


class FacultyInfo(luigi.Task):

    def get_professor_links_for_research_areas(self):
        # Set up Chrome options for Colab
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Initialize the Chrome driver
        with uc.Chrome(options=options) as driver:

            research_areas = metadata["Khoury College of Computer Science"]["research_areas"]
            prof_url = metadata["Khoury College of Computer Science"]["professors_info"]["prof_url"]

            professors = []
            for val,i in enumerate(research_areas):
                # try:
                    # Step 2: Navigate to the webpage
                    driver.get(prof_url + i)
                    print(prof_url + i)

                    wait = WebDriverWait(driver, 40)
                    parent_divs = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="people-page-results"]/div')))
                    # print(parent_divs)
                    for i in parent_divs:
                        # child_divs = i.find_elements(By.CLASS_NAME, 'headline interactive')
                        # name = [div.text for div in child_divs if div.text][0]

                        # Step 4: Extract href attributes and text from all child a tags
                        child_links = i.find_elements(By.TAG_NAME, 'a')
                        links = [[link.get_attribute('href'), link.text] for link in child_links if link.get_attribute('href')]
                        for j in links:
                            tmp = [research_areas[val],j[0]]
                            tmp.extend(j[1].split("\n"))
                            professors.append(tmp)
        return professors

    def filter_based_location(self):
        location = metadata["Khoury College of Computer Science"]["location"]
        professors = self.get_professor_links_for_research_areas()
        professors_df = pd.DataFrame(professors, columns=["Research-Area", "Link", "Name", "Designation", "Location", " "])
        professors_df.drop(columns=[" "], inplace=True)
        # Filter for rows where "Location" is "BOSTON"
        professors_df = professors_df[professors_df["Location"] == location]
        return professors_df

    def get_email_ids_of_professors(self,professors_df):
        
        # Set up Chrome options
        options = uc.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')


        mails = []
        # Initialize the Chrome driver
        with uc.Chrome(options=options) as driver:
            for i in professors_df["Link"]:
                try:
                    # Navigate to the webpage
                    driver.get(i)
                    wait = WebDriverWait(driver, 60)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    print(i)
                    # Wait for the main content to load and become visible
                    # wait = WebDriverWait(driver, 70)
                    main_content = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'a')))
                    mail = ""
                    for i in main_content:
                        try :
                            link = i.get_attribute('href')
                            if link.split(":")[0] == "mailto" :
                                print(link)
                                mail = link.split(":")[1]
                                # mails.append(link)
                        except:
                            pass
                    mails.append(mail)
                    # print(content)
                except Exception as e:
                    print(f"An error occurred: {e}")
        return mails

    def get_research_interests_and_other_info(self,professors_df):
        # Set up Chrome options
        options = uc.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')


        bio = []
        res_int = []
        # Initialize the Chrome driver
        with uc.Chrome(options=options) as driver:
            for i in professors_df["Link"]:
            # Replace with the actual URL

                try:
                    # Navigate to the webpage
                    driver.get(i)
                    
                    # Wait for the main content to load and become visible
                    wait = WebDriverWait(driver, 60)
                    main_content = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    
                    # Extract and print all the text from the main content
                    text = main_content.text.split("Khoury Social")[0]
                    text = llm.get_all_info_prof_page(text)
                    
                    # Extract research interests using regex
                    research_interests = " ".join(re.findall(r'- ([^\n]+)', text.split("Biography")[0]))
                    
                    
                    biography = " ".join(re.findall(r'- ([^\n]+)', text.split("Biography")[1]))
                    
                

                    bio.append(biography)
                    res_int.append(research_interests)
                    time.sleep(3)
                except:
                    bio.append("")
                    res_int.append("")
                    pass
                # finally:
                    # Close the browser
        professors_df["Research-Interest"] = res_int
        professors_df["biography"] = bio
        return professors_df

    def requires(self):
        return Labs()

    def output(self):
        return luigi.LocalTarget('../Bronze/facultyInfo.csv')

    def run(self):
        df = self.filter_based_location()
        df["mail"] = self.get_email_ids_of_professors(df)
        df = self.get_research_interests_and_other_info(df)
        df.to_csv(self.output().path,index = False)
        print("Success : Faculty Information")



