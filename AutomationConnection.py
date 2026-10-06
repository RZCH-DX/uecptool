import time
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
import json
import socket
import threading
import logging

class AutomationConnection:
    # Function to get receive metadata from RadioDJ over UDP
    def __init__(self, config_manager, uecp_manager):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.config_manager = config_manager
        self.uecp_manager = uecp_manager
        self.schedule_engine = None
        self.current_data = json.loads('{"tracktype": 0,"subcatid": 0,"artist": "placeholder","title": "placeholder","year": "0"}')
        self.title_available = False
        self.news_active = False
        self.logger = logging.getLogger(__name__)

    def set_schedule_engine(self, schedule_engine):
        self.schedule_engine = schedule_engine

    def connect(self):
        self.sock.bind((self.config_manager.config["radiodj_listen"]["ip"], self.config_manager.config["radiodj_listen"]["port"]))

    def _get_metadata_from_automation(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            try:
                temp_json = json.loads(data.decode('utf-8'))
                self.logger.info(f"Received data: {temp_json}")
            except json.JSONDecodeError as e:
                self.logger.warning(f"Invalid JSON received. Title will be set to unavailable, placeholder json will be loaded: {e}")
                temp_json = json.loads('{"tracktype": 1,"subcatid": 1,"artist": "placeholder","title": "placeholder","year": "0"}')
            if temp_json["subcatid"] == 0:
                 self.logger.debug("subcat-id 0 -> ignoring.")
            elif self.config_manager.config["rdj_news_trigger_key"] and temp_json[self.config_manager.config["rdj_news_trigger_key"]] == self.config_manager.config["rdj_news_trigger_value"]:
                current_time_with_tz = datetime.now(timezone.utc).astimezone(ZoneInfo(self.config_manager.config["timezone"]))
                self.title_available = self.config_manager.config["show_news_in_rt"]
                self.current_data = temp_json
                self.news_active = True
                news_pin = [current_time_with_tz.day, current_time_with_tz.hour, current_time_with_tz.minute]
                self.uecp_manager.send_uecp_command("ms", 0)
                self.uecp_manager.send_uecp_command("pty", self.config_manager.static_rds["news_pty"])
                self.uecp_manager.send_uecp_command("ptyn", self.config_manager.static_rds["news_ptyn"])
                self.uecp_manager.send_uecp_command("pin", news_pin)
            else:
                if self.schedule_engine.current_show and self.news_active:
                    current_time_with_tz = datetime.now(timezone.utc).astimezone(ZoneInfo(self.config_manager.config["timezone"]))
                    self.config_manager.current_pin = [current_time_with_tz.day, current_time_with_tz.hour, current_time_with_tz.minute]
                    self.uecp_manager.send_uecp_command("pin", self.config_manager.current_pin)
                    self.uecp_manager.send_uecp_command("ms", self.config_manager.static_rds["ms"])
                elif self.news_active:
                    self.config_manager.current_pin = self.config_manager.static_rds["default_pin"]
                    self.uecp_manager.send_uecp_command("pin", self.config_manager.current_pin)
                    self.uecp_manager.send_uecp_command("ms", self.config_manager.static_rds["ms"])
                self.uecp_manager.send_uecp_command("pty", self.config_manager.current_pty)
                self.uecp_manager.send_uecp_command("ptyn", self.config_manager.current_ptyn)
                self.news_active = False
                if temp_json["tracktype"] == 0 or temp_json["tracktype"] == 5 or temp_json["tracktype"] == 7 or temp_json["tracktype"] == 8 or temp_json["tracktype"] == 9 or temp_json["tracktype"] == 12 or temp_json["tracktype"] == 13:
                    self.title_available = True
                    self.current_data = temp_json
                else:
                    self.title_available = False
            time.sleep(0.5)

    def start_thread(self):
        metadata_thread = threading.Thread(target=self._get_metadata_from_automation)
        metadata_thread.daemon = True
        metadata_thread.start()