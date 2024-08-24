import luigi
from DataSource.Bronze.ongoingRsearch import OngoingResearch
from DataSource.Bronze.labs import Labs
if __name__ == "__main__":
    luigi.build([Labs(),OngoingResearch()], scheduler_host='localhost', scheduler_port=8082)