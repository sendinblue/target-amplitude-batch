import json
import os
import sys
import unittest


class BaseUnitTest(unittest.TestCase):

    def setUp(self):
        self.client = None

    def tearDown(self):
        self.client = None

    def set_cli_args(self, *args, **kwargs):
        arg = [arg for arg in args]

        for k, v in kwargs.items():
            if k == "stdin":
                sys.stdin = open(v, "r")
                continue

            # if some flag is being passed, such as --merge-state or --no-merge-state:
            # we want to add this flag to CLI arguments
            if k == "flag":
                arg.append(v)
                continue

            arg.append("--{}".format(k))
            arg.append("{}".format(v))

        sys.argv[1:] = arg

        if "config" in kwargs:
            with open(kwargs["config"], "r") as f:
                json.load(f)

    def init_config(self, data_file_name):
        self.set_cli_args(
            stdin=os.path.join(os.path.join(
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests'),
                'data'), data_file_name),
            # config=os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sandbox'),
            #                     config_file_name)
        )
