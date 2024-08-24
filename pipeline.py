import luigi
from DataSource.Bronze.pipeline import tasks as BronzeTasks
from DataSource.Silver.pipeline import tasks as SilverTasks

if __name__ == "__main__":
    luigi.build(BronzeTasks + SilverTasks,scheduler_host='localhost', scheduler_port=8082)