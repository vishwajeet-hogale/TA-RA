import luigi
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Bronze')))
from ongoingResearch import OngoingResearch



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


