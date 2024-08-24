import luigi
from DataSource.Silver.facultyInfoClean import CleanLab_FacultyInfo

if __name__ == "__main__":
    luigi.build([CleanLab_FacultyInfo()], scheduler_host='localhost', scheduler_port=8082)