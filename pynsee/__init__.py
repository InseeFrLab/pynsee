import logging

from pynsee.sirene import *
from pynsee.macrodata import *
from pynsee.localdata import *
from pynsee.geodata import *
from pynsee.metadata import *
from pynsee.utils import *
from pynsee.download import *


# Set loglevel from env variable
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
)

# Set default logging handler to avoid "No handler found" warnings.
# logging.getLogger(__name__).addHandler(logging.NullHandler())
