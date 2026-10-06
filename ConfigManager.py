import json
import threading
import logging
from RtObject import RtObject

class ConfigManager:
    def __init__(self):
        self.schedule_thread_event = threading.Event()
        self.schedule_thread_event.set()
        self.logger = logging.getLogger(__name__)
        with open("uecptoolconfig.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.logger.info("JSON loaded successfully.")

    def save_json(self):
        with open("uecptoolconfig.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        self.logger.info("JSON saved successfully.")

    def _load_data(self):
        self.LOCAL_ENCODER_IP = self.config["local_encoder"]["ip"]
        self.LOCAL_ENCODER_PORT = self.config["local_encoder"]["port"]
    
        self.UECP_SERVER_IP = self.config["uecp_server"]["ip"]
        self.UECP_SERVER_PSWD = self.config["uecp_server"]["password"]
    
        self.static_rds = self.config["static_rds"]
    
        self.default_rt_strings = [
            RtObject(
                entry["rtplus"],
                entry["text"]
            )
            for entry in self.config["radiotext"]["default"]
        ]
        self.logger.info("Configuration loaded.")

    def init_data(self):
        self._load_data()
        self.current_pty = self.static_rds["default_pty"]
        self.current_ptyn = self.static_rds["default_ptyn"]
        self.current_pin = self.static_rds["default_pin"]

    def reload_data(self):
        self._load_data()
        self.schedule_thread_event.set()