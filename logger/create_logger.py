import logging
import sys

from logger.filters import CustomFormatterConsole, CustomFormatterFile

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create console handler with a higher log level
ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.INFO)

ch.setFormatter(CustomFormatterConsole())

# Create file handler with a higher log level
fileHandler = logging.FileHandler(filename="logger\\logs.log", mode="w", encoding="utf-8")
fileHandler.setLevel(logging.INFO)

fileHandler.setFormatter(CustomFormatterFile())

# Add handlers to logger
logger.addHandler(ch)
logger.addHandler(fileHandler)