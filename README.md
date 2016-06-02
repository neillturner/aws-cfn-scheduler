# aws-cfn-scheduler
Creates and deletes cloudformation stacks using a JSON based schedule


## Description

     aws cfn scheduler - Creates and deletes cloudformation stacks using a JSON based schedule.

     It is a python script that runs regularly in cron that looks at your cloudformation stacks.
     Specify in the config file for each stack a json string giving the stop and start schedule hour for mon to fri.
     it will them make sure that each cloudformation stack is created or deleted as per the schedule.

     Tested on Centos 7.

## Prerequisites

### Redhat

  Install epel, python, pip, boto and docopt:

  1. sudo yum install epel-release

  2. sudo yum install python-devel python-pip

  3. sudo pip install boto docopt

### Ubuntu

  Install python, pip, boto and docopt:

  1. sudo apt-get install python-dev python-pip

  2. sudo pip install boto docopt


## Suggested Installation

 1. copy aws-cfn-scheduler.py to /usr/bin/aws-cfn-scheduler.py

 2. copy aws-cfn-scheduler.cfg to /etc/aws-cfn-scheduler.cfg and configure

 3. Copy your cloudformation templates to directory like /var/local/aws-cfn-scheduler/

 4. sudo crontab -e and to run once an hour at 5 mins past hour add
 5 * * * *  sudo /usr/bin/python /usr/bin/aws-cfn-scheduler.py  check >> /var/log/aws-cfn-scheduler_cron.log




