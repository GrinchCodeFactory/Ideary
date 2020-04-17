import datetime

import pytz
import yaml
import os

def read_conf():
    with open(os.path.expanduser("~/ideary.yaml"), 'r') as fh:
        return yaml.load(fh)

def now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)