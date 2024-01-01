import logging
import pathlib
import sys

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

sys.path.append(f"""{pathlib.Path(__file__).resolve().parent}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent.parent)}""")
from lib.tools import Setting, Tool


class InflationCleaner:
    CATEGORY_NAME_FULL = ""
    
    def __init__(self):
        self.setting = Setting()
        self.tool = Tool()