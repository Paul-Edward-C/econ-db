import pathlib
import sys

import pandas as pd

sys.path.append(f"""{pathlib.Path(__file__).resolve().parent}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent.parent)}""")
from lib.tools import Setting

"""
This generator is used to generate number of different raw data (billion/million/thousand) and export the raw data name
and number unit to a temp file and that file will be used when creating data setting files.
"""


class Number_Unit_Generator(object):
    def __init__(self):
        pass

    def create(self):
        pass
