import luigi
from DataSource.Bronze.ongoingResearch import OngoingResearch
# from DataSource.Bronze.labs import Labs

tasks = [OngoingResearch()]
if __name__ == "__main__":
    luigi.build([OngoingResearch()], scheduler_host='localhost', scheduler_port=8082)