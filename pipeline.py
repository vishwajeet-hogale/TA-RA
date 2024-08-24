import luigi
from DataSource.Bronze.pipeline import OngoingResearch as bronze1
from DataSource.Bronze.pipeline import Labs as bronze
from DataSource.Silver.pipeline import CleanLab_FacultyInfo as silver

if __name__ == "__main__":
    luigi.build([bronze(),bronze1(),silver()])