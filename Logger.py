import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import threading
import atexit

class Logger:
    def __init__(self):
        os.makedirs("logs", exist_ok=True)

        self.handler = TimedRotatingFileHandler(
            filename='logs/uecptool.log',
            when='MIDNIGHT',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )

        self.handler.suffix = "%Y-%m-%d"
        self.handler.namer = lambda default_name: default_name.replace(".log.", "-") + ".log"

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(message)s')
        self.handler.setFormatter(formatter)

    def start_logging(self):
        sys.excepthook = self._handle_exception
        threading.excepthook = self._handle_thread_exception
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(self.handler)
        atexit.register(self._log_exit)
        logger.info("Starting UECP tool...")

    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical("Exception occurred: ", exc_info=(exc_type, exc_value, exc_traceback))

    def _handle_thread_exception(self, args):
        self._handle_exception(args.exc_type, args.exc_value, args.exc_traceback)

    def _log_exit(self):
        logging.info("Closing UECP tool...")