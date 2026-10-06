import unicodedata
import time
from RtObject import RtObject
from DynPsEngine import DynPsEngine
import threading
import string

class App:
    def __init__(self, config_manager, automation_connection, uecp_manager, schedule_engine):
        self.config_manager = config_manager
        self.automation_connection = automation_connection
        self.uecp_manager = uecp_manager
        self.schedule_engine = schedule_engine
        self.command_dict = {
            "lps" : False,
            "pi" : False,
            "ta" : False,
            "ms" : False,
            "af" : False,
            "pin" : False,
            "diptyi" : False,
            "ecc" : False,
            "lic" : False,
            "gvc_seq" : False,
        }
        self.last_rt = RtObject([False, False, 0, 0, 0, 0, 0, 0], "")

    def _get_template_positions(self, template, data):
        formatter = string.Formatter()
        current_index = 0
        positions = {}
        for literal_text, field_name, _, _ in formatter.parse(template):
            if literal_text:
                current_index += len(literal_text)
            if field_name is not None and field_name in data:
                val_len = len(str(data[field_name]))
                positions[field_name] = {
                    "start": current_index,
                    "end": current_index + val_len
                }
                current_index += val_len
        return positions

    # Function to generate the title data RT and RT+ data
    def generate_title_rt(self):
        radio_text_settings = self.config_manager.config["radiotext"]
        template = radio_text_settings["titleinfo_format_template"]
        item_title = 1
        item_artist = 4
        title_info_data = {
            "artist": self.automation_connection.current_data["artist"],
            "title": self.automation_connection.current_data["title"],
            "year": self.automation_connection.current_data["year"]
        }
        if title_info_data["year"]:
            title_info_data["year"] = "({year})".format(year=title_info_data["year"])
        else:
            title_info_data["year"] = ""
        if radio_text_settings["titleinfo_remove_accents"]:
            title_info_data["artist"] = self.strip_accents(title_info_data["artist"])
            title_info_data["title"] = self.strip_accents(title_info_data["title"])
        if radio_text_settings["titleinfo_caps_artist"]:
            title_info_data["artist"] = title_info_data["artist"].upper()
        if radio_text_settings["titleinfo_caps_title"]:
            title_info_data["title"] = title_info_data["title"].upper()

        positions = self._get_template_positions(template, title_info_data)
        radio_text = template.format(artist=title_info_data["artist"], title=title_info_data["title"], year=title_info_data["year"])
        
        artist_start = positions.get("artist", {}).get("start", 0)
        artist_length = positions.get("artist", {}).get("end", 0) - positions.get("artist", {}).get("start", 0)
        title_start = positions.get("title", {}).get("start", 0)
        title_length = positions.get("title", {}).get("end", 0) - positions.get("title", {}).get("start", 0)
        year_start = positions.get("year", {}).get("start", 0)
        year_length = positions.get("year", {}).get("end", 0) - positions.get("year", {}).get("start", 0)

        sorted_blocks = sorted(positions.values(), key=lambda x: x["start"])
        splitter_lengths = []
        for i in range(len(sorted_blocks) - 1):
            current_block_end = sorted_blocks[i]["end"]
            next_block_start = sorted_blocks[i+1]["start"]
            length = max(0, next_block_start - current_block_end)
            splitter_lengths.append(length)

        existing_start_markers = []

        if "artist" in positions: existing_start_markers.append(artist_start)
        if "title" in positions:  existing_start_markers.append(title_start)
        if "year" in positions:   existing_start_markers.append(year_start)

        prefix_length = min(existing_start_markers) if existing_start_markers else len(radio_text)
        suffix_length = len(radio_text) - max(artist_start + artist_length, title_start + title_length, year_start + year_length)

        if (64 - prefix_length - artist_length - title_length - year_length - sum(splitter_lengths) < suffix_length) and radio_text_settings["titleinfo_trim_prefix_suffix"]:
            if suffix_length > 0:
                radio_text = radio_text[:-suffix_length]
            suffix_length = 0
            if 64 - artist_length - title_length - year_length - sum(splitter_lengths) < prefix_length:
                radio_text = radio_text[prefix_length:]
                artist_start -= prefix_length
                title_start -= prefix_length
                year_start -= prefix_length
                prefix_length = 0

        if ((64 - title_length - sum(splitter_lengths) - prefix_length - suffix_length - year_length > 32) & (artist_length > 32)) or not item_title:
            artist_length_marker = min(63, artist_length - 1)
            title_length_marker = min(31, title_length - 1)
        else:
            artist_length_marker = min(31, artist_length - 1)
            title_length_marker = min(63, title_length - 1)

        title_start_marker = title_start
        artist_start_marker = artist_start

        if title_start_marker > 64 or title_length_marker == -1:
            item_title = 0
            title_start_marker = 0
            title_length_marker = 0
        if artist_start_marker > 64 or artist_length_marker == -1:
            item_artist = 0
            artist_start_marker = 0
            artist_length_marker = 0

        title_length_marker = min(title_length_marker, max(0, 64 - title_start_marker - 1))
        artist_length_marker = min(artist_length_marker, max(0, 64 - artist_start_marker - 1))

        wipe_rt_plus_buffer = False
        running_bit = False if not item_title and not item_artist else True
        if ((64 - title_length - sum(splitter_lengths) - prefix_length - suffix_length - year_length > 32) & (artist_length > 32)) or not item_title:
            rt_plus_data = [wipe_rt_plus_buffer, running_bit, item_artist, artist_start_marker, artist_length_marker, item_title, title_start_marker, title_length_marker]
        else:
            rt_plus_data = [wipe_rt_plus_buffer, running_bit, item_title, title_start_marker, title_length_marker, item_artist, artist_start_marker, artist_length_marker]
        final_rt = RtObject(rt_plus_data, radio_text)
        self.send_radiotext(final_rt)

    def send_radiotext(self, received_rt_object):
        if self.last_rt == received_rt_object:
            return
        self.last_rt = received_rt_object
        self.uecp_manager.send_uecp_command("rtplus", [True, False, 0, 0, 0, 0, 0, 0])
        if self.config_manager.config["radiotext"]["center_rt"]:
            center_offset = (64 - len(received_rt_object.radio_text[:64])) // 2
            rtp_data_centered = list(received_rt_object.rt_plus_data)
            rtp_data_centered[3] = (rtp_data_centered[3] + center_offset) if rtp_data_centered[2] else 0
            rtp_data_centered[6] = (rtp_data_centered[6] + center_offset) if rtp_data_centered[5] else 0
            self.uecp_manager.send_uecp_command("rtplus", rtp_data_centered)
            self.uecp_manager.send_uecp_command("rt", received_rt_object.radio_text[:64].center(64, " "))
        else:
            self.uecp_manager.send_uecp_command("rtplus", received_rt_object.rt_plus_data)
            self.uecp_manager.send_uecp_command("rt", received_rt_object.radio_text)

    def strip_accents(self, s):
       return ''.join(c for c in unicodedata.normalize('NFD', s)
                      if unicodedata.category(c) != 'Mn')

    def wait_and_loop(self, duration, data_time_of_sending):
        time.sleep(2)
        end_time = time.monotonic() + duration - 2
        while time.monotonic() < end_time:
            if self.command_dict["gvc_seq"]:
                for command in self.command_dict:
                    self.command_dict[command] = False
            for command in self.command_dict:
                if time.monotonic() >= end_time:
                    return
                if self.command_dict[command] == False:
                    i = 0
                    self.command_dict[command] = True
                    if command == "pin":
                        if not self.automation_connection.news_active:
                            self.uecp_manager.send_uecp_command("pin", self.config_manager.current_pin)
                    elif command == "ms":
                        if not self.automation_connection.news_active:
                            self.uecp_manager.send_uecp_command(command, self.config_manager.static_rds[command])
                        else:
                            i = 12
                    else:
                        self.uecp_manager.send_uecp_command(command, self.config_manager.static_rds[command])
                    while (i < 12):
                        if data_time_of_sending and not data_time_of_sending == self.automation_connection.current_data:
                            return
                        if time.monotonic() >= end_time:
                            return
                        else:
                            time.sleep(0.5)
                            i += 1

    def uecp_loop(self):
        time.sleep(2)
        while True:
            special_show_rt_strings = self.schedule_engine.special_show_rt_strings
            if self.config_manager.config["enable_showschedule"] and special_show_rt_strings:
                for special_show_rt_string in special_show_rt_strings:
                    self.send_radiotext(special_show_rt_string)
                    self.wait_and_loop(self.config_manager.config["showstringrt_duration"], None)
                    if self.config_manager.config["radiotext"]["titleinfo_mode"] == 1 and self.automation_connection.title_available:
                        self.generate_title_rt()
                        self.wait_and_loop(self.config_manager.config["radiotext"]["titleinfo_duration"], dict(self.automation_connection.current_data))


            if self.automation_connection.title_available and self.config_manager.config["radiotext"]["titleinfo_mode"] == 0:
                self.generate_title_rt()
                self.wait_and_loop(self.config_manager.config["radiotext"]["titleinfo_duration"], dict(self.automation_connection.current_data))
            if self.config_manager.config["radiotext"]["titleinfo_mode"] == 0 or self.config_manager.config["radiotext"]["titleinfo_mode"] == 1 or (self.config_manager.config["radiotext"]["titleinfo_mode"] == 2 and not self.automation_connection.title_available):
                for default_rt_string in self.config_manager.default_rt_strings:
                    self.send_radiotext(default_rt_string)
                    self.wait_and_loop(self.config_manager.config["radiotext"]["defaultrt_duration"], None)
                    if self.config_manager.config["radiotext"]["titleinfo_mode"] == 1 and self.automation_connection.title_available:
                            self.generate_title_rt()
                            self.wait_and_loop(self.config_manager.config["radiotext"]["titleinfo_duration"], dict(self.automation_connection.current_data))

            if self.automation_connection.title_available and ((self.config_manager.config["radiotext"]["titleinfo_mode"] == 0 and self.config_manager.config["enable_showschedule"]) or self.config_manager.config["radiotext"]["titleinfo_mode"] == 2):
                self.generate_title_rt()
                self.wait_and_loop(self.config_manager.config["radiotext"]["titleinfo_duration"], dict(self.automation_connection.current_data))

    def rtp_odaflag_loop(self):
        while True:
            self.uecp_manager.send_uecp_command("odaflag", [self.config_manager.config["uecp_settings"]["rtp_group"], 0x4bd7])
            time.sleep(self.config_manager.config["uecp_settings"]["odaflag_send_frequency"] / 1000)

    def start_threads(self):
        dyn_ps_engine = DynPsEngine(self.uecp_manager, self.config_manager.config["rdsps_settings"], self.automation_connection)
        dyn_ps_engine.start_thread()
        uecp_loop_thread = threading.Thread(target=self.uecp_loop)
        uecp_loop_thread.daemon = True
        uecp_loop_thread.start()
        rtp_odaflag_thread = threading.Thread(target=self.rtp_odaflag_loop)
        rtp_odaflag_thread.daemon = True
        rtp_odaflag_thread.start()