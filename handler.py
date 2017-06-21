# First some funky path manipulation so that we can work properly in
# the AWS environment
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

from ddsink.handler import lambda_handler


def handler(event, context=None):
    return lambda_handler(event, context)
