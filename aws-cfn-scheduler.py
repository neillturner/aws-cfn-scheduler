
"""This scheduler creates/deletes cloudformation stacks using a JSON based schedule.

Usage:
  aws-cfn-scheduler check [<stack_name> ...] [options]
  aws-cfn-scheduler (-h | --help)
  aws-cfn-scheduler --version

Options:
  -c --config CONFIG    Use alternate configuration file [default: /etc/aws-cfn-scheduler.cfg].
  -h --help             Show this screen.
  --force               Force create 'scheduler' tag.
  --version             Show version.

"""
from docopt import docopt
from ConfigParser import SafeConfigParser
import boto.cloudformation
import sys,os,json,logging, datetime, time

config = SafeConfigParser()
config.optionxform = str

logger = logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

aws_access_key = None
aws_secret_key = None
aws_region     = None

def init():
    # Add rolling file appender (rotates each day at midnight)
    handler = logging.handlers.TimedRotatingFileHandler('/var/log/aws-cfn-scheduler.log',when='midnight')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Setup AWS connection
    aws_access_key = config.get('aws','access_key','')
    aws_secret_key = config.get('aws','secret_key','')
    aws_region     = config.get('aws', 'region','')

    global cfn
    cfn = boto.cloudformation.connect_to_region(
            region_name = aws_region,
            aws_access_key_id = aws_access_key,
            aws_secret_access_key = aws_secret_key)

#
# Loop schedules for the stacks and see if any need creating or deleting.
#
def check():
    # Get current day + hour (using GMT by defaul if time parameter not set to local)
    time_zone = config.get("schedule","time")
    if time_zone == 'local':
        hh  = int(time.strftime("%H", time.localtime()))
        day = time.strftime("%a", time.localtime()).lower()
        logger.info("-----> Checking for stacks to start or stop for localtime hour \"%s\"", hh)
    else:
        hh  = int(time.strftime("%H", time.gmtime()))
        day = time.strftime("%a", time.gmtime()).lower()
        logger.info("-----> Checking for stacks to start or stop for gmt hour \"%s\"", hh)

    started = []
    stopped = []

    for name, data in config.items('stacks'):
        logger.info("Evaluating stack \"%s\"", name)
    #    print '  %s = %s' % (name, data)
        try:
            schedule = json.loads(data)
            stack_status = ''
            stacks = None
            template = None
            template_file = None
            template_data = None
            try:
                stacks = cfn.describe_stacks(name)
            except:
                pass # catch exception if stack not found

            if stacks:
                stack_status = stacks[0].stack_status

            try:
                if hh == schedule[day]['start'] and stack_status in ('', 'DELETE_COMPLETE'):
                    logger.info("creating stack \"%s\"." %(name))
                    started.append(name)
                    template = config.get('templates',name)
                    logger.info("creating stack with template file \"%s\"." %(template))
                    template_file = open(template, 'r')
                    template_data = template_file.read()
                    cfn.create_stack(stack_name=name,template_body=template_data)
            except:
                if not template:
                    logger.error('No template configured for stack \"%s\", please check!' %(name))
                elif not template_data:
                    logger.error('template file \"%s\ does not exist", please check!' %(template))
                pass # catch exception if 'start' is not in schedule.

            try:
                if hh == schedule[day]['stop'] and stack_status != '' and stack_status != 'DELETE_COMPLETE' and stack_status != 'DELETE_IN_PROGRESS':
                    logger.info("deleting stack \"%s\"." %(name))
                    stopped.append(name)
                    cfn.delete_stack(name)
            except:
                pass # catch exception if 'stop' is not in schedule.

        except ValueError as e:
             # invalid JSON
             logger.error('Invalid value for tag \"schedule\" on instance \"%s\", please check!' %(instance.id))

def cli(args):

    try:
        # Use configuration file from cli, or revert to default.
        config.read([args['--config'],'/etc/aws-cfn-scheduler.cfg'])

        init()

        if args.get('check'):
            check()

    except Exception as e:
        logger.error("Exception while processing", e)
        sys.exit(0)

if __name__ == "__main__":
    # Docopt will check all arguments, and exit with the Usage string if they
    # don't pass.
    # If you simply want to pass your own modules documentation then use __doc__,
    # otherwise, you would pass another docopt-friendly usage string here.
    # You could also pass your own arguments instead of sys.argv with: docopt(__doc__, argv=[your, args])
    args = docopt(__doc__, version='AWS 1.0.1')

    # We have valid args, so run the program.
    cli(args)

