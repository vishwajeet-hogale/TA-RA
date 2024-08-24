import luigi
from DataSource.Bronze.pipeline import OngoingResearch as bronze 
from DataSource.Silver.pipeline import CleanLab_FacultyInfo as silver

if __name__ == "__main__":
    luigi.build([bronze(),silver()])