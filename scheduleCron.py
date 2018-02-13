# https://code.tutsplus.com/tutorials/managing-cron-jobs-using-python--cms-28231
# http://www.adminschoice.com/crontab-quick-reference
# setting up cron job in ubuntu
# https://askubuntu.com/questions/799023/how-to-set-up-a-cron-job-to-run-every-10-minutes
# stack overflow https://stackoverflow.com/questions/22387883/how-to-run-the-python-program-using-cron-scheduling

from crontab import CronTab# stack overflow https://stackoverflow.com/questions/22387883/how-to-run-the-python-program-using-cron-scheduling

my_cron = CronTab('yingying')

job = my_cron.new(command='writeDate.py')
job.minute.every(1)

my_cron.write()