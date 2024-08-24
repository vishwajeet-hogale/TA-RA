import luigi
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Bronze')))
from labs import Labs



class CleanLab(luigi.Task):
    def requires(self):
        return Labs()
    def output(self):
        return luigi.LocalTarget('./Silver/labs.csv')
    def clean_lab(self):
        df = pd.read_csv(self.input().path)
        df.to_csv(self.output().path,index=False)
        
    def run(self):
        self.clean_lab()
        print("Silver - Success: Lab Information")


