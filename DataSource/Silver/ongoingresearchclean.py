import luigi
import pandas as pd
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Bronze')))
from ongoingResearch import OngoingResearch
from services import llm

with open("./metadata.json",'r') as f : 
    metadata = json.load(f)

with open('./resume.txt','r') as f:
    resume_text = f.read()

class CleanOngoingResearch(luigi.Task):
    def requires(self):
        return OngoingResearch()
    def output(self):
        return luigi.LocalTarget('./Silver/ongoingresearch.csv')
    def clean_ongoingresearch(self):
        df = pd.read_csv(self.input().path)
        df.to_csv(self.output().path,index=False)
        
    def run(self):
        self.clean_ongoingresearch()
        print("Silver - Success: Ongoing Research Information")

class GeminiModel(luigi.Task):
    def requires(self):
        return CleanOngoingResearch()
    def output(self):
        return luigi.LocalTarget('./Silver/mailing.csv')
    def getMails(self):
        facultyInfo = pd.read_csv('./Silver/facultyInfo.csv')
        onr = pd.read_csv('./Silver/ongoingresearch.csv')
        df = facultyInfo.merge(onr,how='left',left_on='Name',right_on = 'Led-By')
        df = llm.generate_mail(df,resume_text)
        df.to_csv(self.output().path,index=False)
        print("Gemini Mails Successful!")
    def run(self):
        self.getMails()


