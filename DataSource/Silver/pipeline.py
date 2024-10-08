import luigi
from DataSource.Silver import facultyInfoClean as fic
from DataSource.Silver import ongoingresearchclean as orc
from DataSource.Silver import labsclean as lc

tasks = [lc.CleanLab(),fic.CleanLab_FacultyInfo(),orc.GeminiModel()]
if __name__ == "__main__":
    luigi.build([lc.CleanLab(),fic.CleanLab_FacultyInfo(),orc.GeminiModel()], scheduler_host='localhost', scheduler_port=8082)