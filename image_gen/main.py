import logging
from mkdocs.plugins import BasePlugin
import pandas as pd
from svgwrite import Drawing
from datetime import date, timedelta, time
from dateutil.relativedelta import relativedelta
from copy import deepcopy

alignment_color = "rgb(189, 120, 83)"
benefaction_color = "rgb(26, 44, 203)"
network_color = "rgb(227, 209, 43)"
robustness_color = "rgb(204, 32, 27)"
nan_color = "rgb(47,47,47)"


class ImageGenPlugin(BasePlugin):
    def on_files(self, files, config, **kwargs):

        logging.warn("Files: {}".format(files))
        return files


    def on_files(self, nav, files, config, **kwargs):

        logging.warn("Files: {}".format(nav))
        logging.warn("Files: {}".format(files))
        return nav
