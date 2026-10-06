import time
import threading
import logging
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from RtObject import RtObject

class ScheduleEngine:

    def __init__(self, config_manager, uecp_manager, automation_connection):
        self.config_manager = config_manager
        self.uecp_manager = uecp_manager
        self.automation_connection = automation_connection
        self.special_show_rt_strings = []
        self.current_show = ""
        self.logger = logging.getLogger(__name__)

    def schedule_loader(self, current_time):
        special_show_activated = False

        hour = current_time.hour
        day = current_time.weekday()

        if self.config_manager.config["enable_showschedule"]:
            for show in self.config_manager.config["shows"]:
                if show["weekdays"][day]:
                    if show["from_hour"] <= hour < show["to_hour"]:
                        self.logger.info(f"Special show found and activated: {show['name']}")
                        special_show_activated = True
                        self.config_manager.current_pty = show["pty"]
                        self.config_manager.current_ptyn = show["ptyn"]


                        if show["update_pin"] and show["name"] != self.current_show:
                            self.config_manager.current_pin = [
                                current_time.day,
                                show["from_hour"],
                                0
                            ]
                            self.current_show = show["name"]
                        self.special_show_rt_strings = [
                            RtObject(rt["rtplus"], rt["text"])
                            for rt in show["radiotexts"]
                        ]
        if not special_show_activated:
            self.logger.info("No special show found. Loading to default data.")
            self.current_show = ""
            self.special_show_rt_strings = []
            self.config_manager.current_pty = self.config_manager.config["static_rds"]["default_pty"]
            self.config_manager.current_ptyn = self.config_manager.config["static_rds"]["default_ptyn"]
            self.config_manager.current_pin = self.config_manager.config["static_rds"]["default_pin"]
        if not self.automation_connection.news_active:
            self.uecp_manager.send_uecp_command("pin", self.config_manager.current_pin)
            self.uecp_manager.send_uecp_command("pty", self.config_manager.current_pty)
            self.uecp_manager.send_uecp_command("ptyn", self.config_manager.current_ptyn)

    # Function for the scheduleTimer thread
    def schedule_timer(self):
        schedule_tz = ZoneInfo(self.config_manager.config["timezone"])
        while True:
            self.config_manager.schedule_thread_event.wait(timeout=0.5)
            if self.config_manager.schedule_thread_event.is_set():
                schedule_tz = ZoneInfo(self.config_manager.config["timezone"])
                self.config_manager.schedule_thread_event.clear()
                current_time = datetime.now(timezone.utc)
                self.schedule_loader(current_time.astimezone(schedule_tz))
            elif self.config_manager.config["enable_showschedule"]:
                current_time = datetime.now(timezone.utc)
                schedule_time_with_tz = current_time.astimezone(schedule_tz)
                if current_time.minute == 0 and current_time.second == 0:
                    self.schedule_loader(schedule_time_with_tz)
                    time.sleep(1)

    def startTimeThread(self):
        time_thread = threading.Thread(target=self.schedule_timer)
        time_thread.daemon = True
        time_thread.start()