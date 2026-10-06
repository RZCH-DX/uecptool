import time
import threading
import unicodedata

class DynPsEngine:
    def __init__(self, uecp_manager, rdsps_settings, automation_connection):
        self.uecp_manager = uecp_manager
        self.rdsps_settings = rdsps_settings
        self.automation_connection = automation_connection
        self._previous_ps = ""
        self._previous_ps_counter = 0

    def _strip_accents(self, s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
                       if unicodedata.category(c) != 'Mn')

    def _split_string_into_blocks(self, text, block_size, center):
        prepared_words = []
        for word in text.split():
            while len(word) > block_size:
                prepared_words.append(word[:block_size])
                word = word[block_size:]
            if word:
                prepared_words.append(word)

        blocks = []
        current_block = ""

        for word in prepared_words:
            if not current_block:
                current_block = word
            elif len(current_block) + 1 + len(word) <= block_size:
                current_block += " " + word
            else:
                blocks.append(current_block)
                current_block = word

        if current_block:
            blocks.append(current_block)

        if center:
            centered_blocks = [block.center(block_size) for block in blocks]
            return centered_blocks
        else:
            return blocks

    def _send_rds_ps(self, message):
        if message != self._previous_ps:
            self.uecp_manager.send_uecp_command("ps", message)
            self._previous_ps = message
            self._previous_ps_counter = 0
        else:
            self._previous_ps_counter += 1
            if self._previous_ps_counter >= 12:
                self.uecp_manager.send_uecp_command("ps", message)
                self._previous_ps_counter = 0

    def dyn_ps_loop(self):
        while True:
            def show_station_once():
                for ps_block in self._split_string_into_blocks(self.rdsps_settings["station_name"], 8, self.rdsps_settings["center_station_name"]):
                    self._send_rds_ps(ps_block)
                    time.sleep(self.rdsps_settings["message_duration"])
                time.sleep(0.1)
                return True

            if not self.automation_connection.title_available or not self.rdsps_settings["dyn_ps"]:
                while not self.automation_connection.title_available or not self.rdsps_settings["dyn_ps"]:
                    show_station_once()
                continue

            current_data = self.automation_connection.current_data
            current_artist = current_data["artist"]
            current_title = current_data["title"]
            current_year = current_data["year"]
            if current_year:
                current_year = "({year})".format(year=current_year)
            else:
                current_year = ""

            if self.rdsps_settings["remove_accents"]:
                current_artist = self._strip_accents(current_artist)
                current_title = self._strip_accents(current_title)
            if self.rdsps_settings["caps_artist"]:
                current_artist = current_artist.upper()
            if self.rdsps_settings["caps_title"]:
                current_title = current_title.upper()
            dyn_ps_string = self.rdsps_settings["title_info_format"].format(artist=current_artist, title=current_title, year=current_year)

            def show_title_once():
                for block in self._split_string_into_blocks(dyn_ps_string, 8, self.rdsps_settings["center_title_info"]):
                    if self.automation_connection.current_data != current_data:
                        return False
                    self._send_rds_ps(block)
                    time.sleep(self.rdsps_settings["message_duration"])
                return True

            if self.rdsps_settings["title_info_repeats"] == 0:
                while (
                    self.automation_connection.title_available
                    and self.rdsps_settings["dyn_ps"]
                    and self.automation_connection.current_data == current_data
                ):
                    if not show_title_once():
                        break
                    for _ in range(max(1, self.rdsps_settings["station_name_repeats"])):
                        if (
                            not self.automation_connection.title_available
                            or not self.rdsps_settings["dyn_ps"]
                            or self.automation_connection.current_data != current_data
                        ):
                            break
                        if not show_station_once():
                            break
            else:
                for _ in range(self.rdsps_settings["title_info_repeats"]):
                    if (
                        not self.automation_connection.title_available
                        or not self.rdsps_settings["dyn_ps"]
                        or self.automation_connection.current_data != current_data
                    ):
                        break
                    if not show_title_once():
                        break
                    for _ in range(max(1, self.rdsps_settings["station_name_repeats"])):
                        if self.automation_connection.current_data != current_data:
                            break
                        if not show_station_once():
                            break

                if self.automation_connection.current_data == current_data:
                    while self.automation_connection.current_data == current_data:
                        if not show_station_once():
                            break

    def start_thread(self):
        dyn_ps_thread = threading.Thread(target=self.dyn_ps_loop)
        dyn_ps_thread.daemon = True
        dyn_ps_thread.start()