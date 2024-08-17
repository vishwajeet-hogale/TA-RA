import luigi
from ongoingRsearch import OngoingResearch

if __name__ == "__main__":
    luigi.build([OngoingResearch()], scheduler_host='localhost', scheduler_port=8082)