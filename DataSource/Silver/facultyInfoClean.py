import luigi
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Bronze')))
from professorInfo import FacultyInfo



class CleanLab_FacultyInfo(luigi.Task):
    def requires(self):
        return FacultyInfo()
    def output(self):
        return luigi.LocalTarget('./Silver/facultyInfo.csv')
    def clean_lab(self,df):
        dataframe = []
        cols = df.columns[:-1]  # All columns except 'Lab'
        for _, row in df.iterrows():
            try:
                for i in row["Lab"].split("#"):
                    temp = list(row[cols])  # Create a list of the row's values except 'Lab'
                    temp.append(i.strip().lower())  # Append the cleaned 'Lab' value
                    dataframe.append(temp)  # Append this to the dataframe list
                    # print(dataframe)
            except:
                dataframe.append(list(row))
        
        # Create a new DataFrame with the same column names
        return pd.DataFrame(dataframe, columns=list(df.columns))
    def run(self):
        df = pd.read_csv(self.input().path)
        df = self.clean_lab(df)
        df.to_csv(self.output().path, index=False)
        print("Silver - Success: Faculty Lab Information")


