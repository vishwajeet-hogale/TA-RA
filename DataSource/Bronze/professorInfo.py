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
from DataSource.Bronze.labs import Labs


with open("./metadata.json",'r') as f : 
    metadata = json.load(f)
    # print(metadata)

genai.configure(api_key=metadata["API_KEY"])


class GetProfessorLinks(luigi.Task):
    def output(self):
        return luigi.LocalTarget('./Bronze/professor_links.json')

    def run(self):
        # Place the code for get_professor_links_for_research_areas() here.
        professors = self.get_professor_links_for_research_areas()
        with self.output().open('w') as f:
            json.dump(professors, f)
    
    def get_professor_links_for_research_areas(self):
        # Your existing code from `get_professor_links_for_research_areas`
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
class FilterProfessorsByLocation(luigi.Task):
    def requires(self):
        return GetProfessorLinks()

    def output(self):
        return luigi.LocalTarget('./Bronze/professors_filtered.csv')

    def run(self):
        with self.input().open('r') as f:
            professors = json.load(f)
        df = pd.DataFrame(professors, columns=["Research-Area", "Link", "Name", "Designation", "Location", " "])
        df.drop(columns=[" "], inplace=True)
        location = metadata["Khoury College of Computer Science"]["location"]
        df = df[df["Location"] == location]
        df.to_csv(self.output().path, index=False)

class GetProfessorEmails(luigi.Task):
    def requires(self):
        return FilterProfessorsByLocation()

    def output(self):
        return luigi.LocalTarget('./Bronze/professors_with_emails.csv')

    def run(self):
        df = pd.read_csv(self.input().path)
        df["mail"] = self.get_email_ids_of_professors(df)
        df.to_csv(self.output().path, index=False)

    def get_email_ids_of_professors(self, professors_df):
        # Your existing code from `get_email_ids_of_professors`
        # Set up Chrome options
        options = uc.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        print("Stage 3 : Professor's email IDs")

        mails = []
        # Initialize the Chrome driver
        with uc.Chrome(options=options) as driver:
            for i in professors_df["Link"]:
                try:
                    # Navigate to the webpage
                    driver.get(i)
                    wait = WebDriverWait(driver, 60)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    # print(i)
                    # Wait for the main content to load and become visible
                    # wait = WebDriverWait(driver, 70)
                    main_content = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'a')))
                    mail = ""
                    for i in main_content:
                        try :
                            link = i.get_attribute('href')
                            if link.split(":")[0] == "mailto" :
                                # print(link)
                                mail = link.split(":")[1]
                                # mails.append(link)
                        except:
                            pass
                    mails.append(mail)
                    # print(content)
                except Exception as e:
                    print(f"An error occurred: {e}")
        return mails
class GetResearchInterestsAndBio(luigi.Task):
    def requires(self):
        return GetProfessorEmails()

    def output(self):
        return luigi.LocalTarget('./Bronze/professors_with_research_bio.csv')

    def run(self):
        df = pd.read_csv(self.input().path)
        df = self.get_research_interests_and_other_info(df)
        df.to_csv(self.output().path, index=False)

    def get_research_interests_and_other_info(self, professors_df):
        # Your existing code from `get_research_interests_and_other_info`
        # Set up Chrome options
        options = uc.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        print("Stage 4 : Professor's bio'")

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
        professors_df["Biography"] = bio
        return professors_df
class GetLabLinks(luigi.Task):
    def requires(self):
        return GetResearchInterestsAndBio()

    def output(self):
        return luigi.LocalTarget('./Bronze/professors_with_labs.csv')

    def run(self):
        df = pd.read_csv(self.input().path)
        df = self.get_lab_link(df)
        df.to_csv(self.output().path, index=False)

    def get_lab_link(self, professors_df):
        # Your existing code from `get_lab_link`
        # Set up Chrome options
        options = uc.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        print("Stage 1 : Professor's labs and groups")

        labs = []
        # Initialize the Chrome driver
        with uc.Chrome(options=options) as driver:
            for i in professors_df["Link"]:
            # Replace with the actual URL

                try:
                    # Navigate to the webpage
                    driver.get(i)
                    
                    wait = WebDriverWait(driver, 60)
                    main_content = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    # print(main_content.text)
                    model = genai.GenerativeModel('gemini-1.0-pro-latest')
                    try:
                        response = model.generate_content(f"""{main_content.text}
                                                            In the above text, What is the lab and groups names, it is under Labs and Groups ? Answer in just the names of the labs. Don't include anything else. Just the name. Seperate the labs by adding a # in between them.If no labs/groups are found in the context then return an empty string/""
                                                            """)
                        print(response.text.lower())
                        labs.append(response.text)
                    except:
                        labs.append("")
                    
                    time.sleep(1)
                except:
                    pass
                # finally:
                    # Close the browser
        professors_df["Lab"] = labs
        return professors_df
class FacultyInfo(luigi.Task):
    def requires(self):
        return GetLabLinks()

    def output(self):
        return luigi.LocalTarget('./Bronze/facultyInfo.csv')

    def run(self):
        df = pd.read_csv(self.input().path)
        df.to_csv(self.output().path, index=False)
        print("Success: Faculty Information")
if __name__ == "__main__":
    luigi.build([FacultyInfo()])

