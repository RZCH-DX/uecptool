from collections import deque
import re
from tkinter import messagebox
import ipaddress

class UiController:

    def __init__(self, config_manager, encoder_connection):
        self.config_manager = config_manager
        self.encoder_connection = encoder_connection
        self.rdsps_queue = deque()
        self.rdsrt_queue = deque()
        self.rdspty_queue = deque()
        self.rdsptyn_queue = deque()
        self.rdspi_queue = deque()
        self.rdspin_queue = deque()
        self.rdstp_queue = deque()
        self.rdsta_queue = deque()
        self.rdsms_queue = deque()
        self.rdsrtp_queue = deque()
        self.ws_queue = deque()
        self.tcp_queue = deque()

    def set_view(self, ui_view):
        self.ui_view = ui_view

    def set_uecp_manager(self, uecp_manager):
        self.uecp_manager = uecp_manager

    def get_config(self):
        return self.config_manager.config

    def get_instance_name(self):
        return self.config_manager.config["instance_name"]

    def get_radiotext_source(self, list_name, show_index=None):
        config = self.get_config()
        if list_name == "defaultRt":
            return config["radiotext"]["default"]
        if list_name == "specialshow" and show_index is not None:
            return config["shows"][show_index]["radiotexts"]
        return None

    def save_radiotext_entry(self, mode, index, list_name, show_index, radiotext, rtplus, schedule_rt_temp=None):
        dest = self.get_radiotext_source(list_name, show_index)
        if dest is None and list_name == "specialshow" and show_index is None:
            dest = schedule_rt_temp
        if dest is None:
            return None

        entry = {"rtplus": rtplus, "text": radiotext}
        if mode == "Add":
            dest.append(entry)
        elif mode == "Edit":
            dest[index] = entry

        self.reload_config()
        if list_name == "defaultRt":
            self.load_data_into_tvDefaultRt()
        return dest

    def delete_schedule_radiotext(self, index_rt, show_index):
        self.get_config()["shows"][show_index]["radiotexts"].pop(index_rt)
        self.reload_config()

    def get_schedule_entry(self, index):
        return self.get_config()["shows"][index]

    def save_schedule_entry(self, mode, index, schedule_name, start_hour, stop_hour, weekdays, schedule_pty, schedule_ptyn, update_pin, schedule_rt_temp):
        config = self.get_config()
        if mode == "Edit":
            config["shows"][index]["name"] = schedule_name
            config["shows"][index]["from_hour"] = start_hour
            config["shows"][index]["to_hour"] = stop_hour
            config["shows"][index]["weekdays"] = weekdays
            config["shows"][index]["pty"] = schedule_pty
            config["shows"][index]["ptyn"] = schedule_ptyn
            config["shows"][index]["update_pin"] = update_pin
        elif mode == "Add":
            config["shows"].append({
                "name": schedule_name,
                "from_hour": start_hour,
                "to_hour": stop_hour,
                "weekdays": weekdays,
                "pty": schedule_pty,
                "ptyn": schedule_ptyn,
                "update_pin": update_pin,
                "radiotexts": schedule_rt_temp,
            })

        self.reload_config()
        self.load_data_into_tvDailyTimetable()

    def load_data_into_tvDefaultRt(self):
        self.ui_view.tvDefaultRt.delete(*self.ui_view.tvDefaultRt.get_children())
        for rtString in self.config_manager.default_rt_strings:
                self.ui_view.tvDefaultRt.insert("", self.ui_view.tk.END, values=(rtString.radio_text,))

    def delete_defaultRt_tv(self, index):
        if messagebox.askyesno("Delete RT string - UECP tool - " + self.get_instance_name(), "Are you sure you want to delete this RT string?", parent=self.ui_view.root):
            self.config_manager.config["radiotext"]["default"].pop(index)
            self.reload_config()
            self.load_data_into_tvDefaultRt()

    def delete_timetable_tv(self, index):
        if messagebox.askyesno("Delete schedule - UECP tool - " + self.get_instance_name(), "Are you sure you want to delete this schedule entry?", parent=self.ui_view.root):
            self.config_manager.config["shows"].pop(index)
            self.ui_view.tvDailyTimetable.delete(*self.ui_view.tvDailyTimetable.get_children())
            self.reload_config()
            for show in self.config_manager.config["shows"]:
                weekdays = show["weekdays"]
                names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                if all(weekdays):
                    days_string = "Daily"
                else:
                    days_string = ", ".join([names[i] for i, active in enumerate(weekdays) if active])
                if not days_string:
                    days_string = "None"
                self.ui_view.tvDailyTimetable.insert("", self.ui_view.tk.END, values=(show["name"], days_string, show["from_hour"], show["to_hour"], f"{show["pty"]} | {self.ui_view.ptyDict[show["pty"]]}", show["ptyn"]))


    def on_select_defaultRt(self, event):
        selected = event.widget.selection()
        if selected:
            index = self.ui_view.tvDefaultRt.index(selected[0])
            self.ui_view.btnEditDefaultRt.configure(state="enabled", command=lambda:self.ui_view.rtpEditor("Edit", index, "defaultRt", None))
            self.ui_view.btnRemoveDefaultRt.configure(state="enabled", command=lambda:self.delete_defaultRt_tv(index))
        else:
            self.ui_view.btnEditDefaultRt.configure(state="disabled", command=lambda:self.ui_view.rtpEditor("Edit", None, "defaultRt", None))
            self.ui_view.btnRemoveDefaultRt.configure(state="disabled", command=lambda:self.delete_defaultRt_tv(None))

    def on_select_timetable(self, event):
        selected = event.widget.selection()
        if selected:
            show_name = str(self.ui_view.tvDailyTimetable.item(selected[0])["values"][0])
            index = next(
                (i for i, d in enumerate(self.config_manager.config["shows"]) if d.get("name") == show_name),
                None
            )
            self.ui_view.btnEditTimetableEntry.configure(state="enabled", command=lambda:self.ui_view.scheduleEditor("Edit", index))
            self.ui_view.btnRemoveTimetableEntry.configure(state="enabled", command=lambda:self.delete_timetable_tv(index))
        else:
            self.ui_view.btnEditTimetableEntry.configure(state="disabled", command=lambda:self.ui_view.scheduleEditor("Edit", None))
            self.ui_view.btnRemoveTimetableEntry.configure(state="disabled", command=lambda:self.delete_timetable_tv(None))

    def load_data_into_tvDailyTimetable(self):
        self.ui_view.tvDailyTimetable.delete(*self.ui_view.tvDailyTimetable.get_children())
        self.config_manager.config["shows"].sort(key=lambda p: p["from_hour"])
        for show in self.config_manager.config["shows"]:
            weekdays = show["weekdays"]
            names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            if all(weekdays):
                days_string = "Daily"
            else:
                days_string = ", ".join([names[i] for i, active in enumerate(weekdays) if active])
            if not days_string:
                days_string = "None"
            self.ui_view.tvDailyTimetable.insert("", self.ui_view.tk.END, values=(show["name"], days_string, show["from_hour"], show["to_hour"], f"{show["pty"]} | {self.ui_view.ptyDict[show["pty"]]}", show["ptyn"]))

    def save_rds_conf(self):
        if self.ui_view.txtPi.get() == "":
            self.ui_view.show_error("Save error", "PI code cannot be empty.")
            return
        af_split = self.ui_view.txtAf.get("1.0", "end-1c").strip().split("\n")
        if len(af_split) == 1 and af_split[0] == "":
            af_int = []
        else:
            try:
                af_int = [float(af) for af in af_split]
            except ValueError as e:
                self.ui_view.show_error("Save error", "AF list contains forbidden characters.\n" + str(e))
                return
        if self.ui_view.txtEcc.get() == "":
            self.ui_view.show_error("Save error", "ECC code cannot be empty. Use 00 instead & remove 0 from 1A group sequence.")
            return
        if self.ui_view.txtLic.get() == "":
            self.ui_view.show_error("Save error", "LIC code cannot be empty. Use 00 instead & remove 3 from 1A group sequence.")
            return
        self.config_manager.config["static_rds"]["pi"] = int(self.ui_view.txtPi.get(), 16)
        self.config_manager.config["static_rds"]["af"] = af_int
        self.config_manager.config["static_rds"]["default_ptyn"] = self.ui_view.txtDefPtyn.get()
        self.config_manager.config["static_rds"]["diptyi"] = {"ms": int(self.ui_view.di_stereo_var.get()), "ah": int(self.ui_view.di_ah_var.get()), "cmp": int(self.ui_view.di_comp_var.get()), "dpty": int(self.ui_view.di_dynpty_var.get())}
        self.config_manager.config["static_rds"]["ta"] = {"ta": int(self.ui_view.ta_conf_var.get()), "tp": int(self.ui_view.tp_conf_var.get())}
        self.config_manager.config["static_rds"]["ms"] = int(self.ui_view.ms_conf_var.get())
        self.config_manager.config["static_rds"]["ecc"] = int(self.ui_view.txtEcc.get(), 16)
        self.config_manager.config["static_rds"]["lic"] = int(self.ui_view.txtLic.get(), 16)
        self.config_manager.config["static_rds"]["default_pty"] = self.ui_view.cmbDefPty.current()
        self.reload_config()
        self.config_manager.save_json()

    def save_schedule(self):
        if self.ui_view.sbScheduleRtDuration.get() == "":
            self.ui_view.show_error("Save error", "Schedule RT duration cannot be empty.")
            return
        self.config_manager.config["enable_showschedule"] = self.ui_view.enable_schedule_var.get()
        self.config_manager.config["showstringrt_duration"] = int(self.ui_view.sbScheduleRtDuration.get())
        self.reload_config()
        self.config_manager.save_json()

    def save_titleinfo_conf(self):
        if self.ui_view.sbDefaultRtDuration.get() == "":
            self.ui_view.show_error("Save error", "Default RT duration cannot be empty.")
            return
        if self.ui_view.sbTitleinfoDuration.get() == "":
            self.ui_view.show_error("Save error", "Title info RT duration cannot be empty.")
            return
        self.config_manager.config["radiotext"]["titleinfo_format_template"] = self.ui_view.txtRadiotextFormatTemplate.get()
        self.config_manager.config["radiotext"]["defaultrt_duration"] = int(self.ui_view.sbDefaultRtDuration.get())
        self.config_manager.config["radiotext"]["titleinfo_duration"] = int(self.ui_view.sbTitleinfoDuration.get())
        self.config_manager.config["radiotext"]["titleinfo_mode"] = self.ui_view.cmbTitleinfoMode.current()
        self.config_manager.config["radiotext"]["titleinfo_remove_accents"] = self.ui_view.remove_accents_var.get()
        self.config_manager.config["radiotext"]["titleinfo_caps_artist"] = self.ui_view.capitalize_artist_var.get()
        self.config_manager.config["radiotext"]["titleinfo_caps_title"] = self.ui_view.capitalize_title_var.get()
        self.config_manager.config["radiotext"]["titleinfo_trim_prefix_suffix"] = self.ui_view.trim_prefix_suffix_var.get()
        self.reload_config()
        self.config_manager.save_json()

    def save_network_setup(self):
        try:
            ipaddress.ip_address(self.ui_view.txtRadioDjIp.get())
        except ValueError as e:
            self.ui_view.show_error("Save error", "RadioDJ IP address is in an invalid format.\n" + str(e))
            return
        if self.ui_view.txtRadioDjIp.get() == "":
            self.ui_view.show_error("Save error", "Automation data source listen IP cannot be empty.")
            return
        if self.ui_view.sbRadioDjPort.get() == "":
            self.ui_view.show_error("Save error", "Automation data source listen port cannot be empty.")
            return
        if self.ui_view.enable_ws_var.get() and self.ui_view.txtWsIp.get() == "":
            self.ui_view.show_error("Save error", "Websocket address cannot be empty if websocket output is enabled.")
            return
        if self.ui_view.enable_ws_var.get() and self.ui_view.txtWsPswd.get() == "":
            self.ui_view.show_error("Save error", "Websocket password cannot be empty if websocket output is enabled.")
            return
        if self.ui_view.enable_local_var.get() and self.ui_view.txtLocalEncIp.get() == "":
            self.ui_view.show_error("Save error", "Local RDS encoder address cannot be empty if its enabled.")
            return
        if self.ui_view.enable_local_var.get() and self.ui_view.sbLocalEncPort.get() == "":
            self.ui_view.show_error("Save error", "Local RDS encoder port cannot be empty if its enabled.")
            return
        self.config_manager.config["radiodj_listen"]["ip"] = self.ui_view.txtRadioDjIp.get()
        self.config_manager.config["radiodj_listen"]["port"] = int(self.ui_view.sbRadioDjPort.get())
        self.config_manager.config["uecp_server"]["enabled"] = self.ui_view.enable_ws_var.get()
        self.config_manager.config["uecp_server"]["ip"] = self.ui_view.txtWsIp.get()
        self.config_manager.config["uecp_server"]["password"] = self.ui_view.txtWsPswd.get()
        self.config_manager.config["local_encoder"]["enabled"] = self.ui_view.enable_local_var.get()
        self.config_manager.config["local_encoder"]["ip"] = self.ui_view.txtLocalEncIp.get()
        self.config_manager.config["local_encoder"]["port"] = int(self.ui_view.sbLocalEncPort.get())
        self.reload_config()
        self.config_manager.save_json()
        self.encoder_connection.connect()

    def save_settings(self):
        if self.ui_view.sbRdjNewsTriggerValue.get() == "":
            self.ui_view.show_error("Save error", "News trigger value cannot be empty.\nTo disable the news trigger, choose 0 here and set trigger key to empty.")
            return
        self.config_manager.config["timezone"] = self.ui_view.cmbTimezone.get()
        self.config_manager.config["rdj_news_trigger_key"] = self.ui_view.txtRdjNewsTriggerKey.get()
        self.config_manager.config["rdj_news_trigger_value"] = int(self.ui_view.sbRdjNewsTriggerValue.get())
        self.config_manager.config["static_rds"]["news_pty"] = int(self.ui_view.cmbNewsPty.current())
        self.config_manager.config["static_rds"]["news_ptyn"] = self.ui_view.txtNewsPtyn.get()
        self.config_manager.config["show_news_in_rt"] = self.ui_view.news_in_rt_var.get()
        self.config_manager.config["instance_name"] = self.ui_view.txtInstanceName.get()
        self.reload_config()
        self.ui_view.root.title("UECP tool - " + self.config_manager.config["instance_name"])
        self.config_manager.save_json()

    def save_uecp(self):
        if self.ui_view.sbWsDsn.get() == "":
            self.ui_view.show_error("Save error", "DSN cannot be empty.")
            return
        if self.ui_view.sbWsPsn.get() == "":
            self.ui_view.show_error("Save error", "PSN cannot be empty.")
            return
        if self.ui_view.sbRadiotextRepeat.get() == "":
            self.ui_view.show_error("Save error", "RT repeat value cannot be empty.")
            return
        if self.ui_view.sbOdaflagFreq.get() == "":
            self.ui_view.show_error("Save error", "RT+ ODA flag frequency cannot be .")
            return
        if not self.validate_group_sequence_format(self.ui_view.txtGroupSequence.get()):
            return
        self.config_manager.config["uecp_settings"]["dsn"] = int(self.ui_view.sbWsDsn.get())
        self.config_manager.config["uecp_settings"]["psn"] = int(self.ui_view.sbWsPsn.get())
        self.config_manager.config["uecp_settings"]["rt_repeat"] = int(self.ui_view.sbRadiotextRepeat.get())
        self.config_manager.config["uecp_settings"]["ab_toggle"] = self.ui_view.ab_toggle_var.get()
        self.config_manager.config["uecp_settings"]["rt_termination"] = self.ui_view.rt_termination_var.get()
        gvcseq_split = self.ui_view.txtGvcSeq.get().split(",")
        if self.ui_view.txtGvcSeq.get() == "":
            gvcseq_int = []
        else:
            gvcseq_int = [int(gvc.strip()) for gvc in gvcseq_split]
        self.config_manager.config["uecp_settings"]["rtp_group"] = list(self.ui_view.group_dict.keys())[self.ui_view.cmbRtpGroup.current()]
        self.config_manager.config["uecp_settings"]["rtp_method"] = list(self.ui_view.rtp_method_dict.keys())[self.ui_view.cmbRtpMethod.current()]
        self.config_manager.config["static_rds"]["gvc_seq"] = gvcseq_int
        self.config_manager.config["uecp_settings"]["odaflag_send_frequency"] = int(self.ui_view.sbOdaflagFreq.get())
        self.config_manager.config["uecp_settings"]["group_sequence"] = self.ui_view.txtGroupSequence.get()
        self.reload_config()
        self.config_manager.save_json()

    def save_rdsps(self):
        if self.ui_view.sbRdspsMessageDuration.get() == "":
            self.ui_view.show_error("Save error", "Message duration cannot be empty.")
            return
        if self.ui_view.sbRdspsTitleInfoRepeats.get() == "":
            self.ui_view.show_error("Save error", "Title info repeats cannot be empty.")
            return
        if self.ui_view.sbRdspsStationNameRepeats.get() == "":
            self.ui_view.show_error("Save error", "Station name repeats cannot be empty.")
            return
        self.config_manager.config["rdsps_settings"]["dyn_ps"] = self.ui_view.rdsps_dyn_ps_var.get()
        self.config_manager.config["rdsps_settings"]["station_name"] = self.ui_view.txtDefaultPs.get()
        self.config_manager.config["rdsps_settings"]["title_info_format"] = self.ui_view.txtTitleInfoFormat.get()
        self.config_manager.config["static_rds"]["lps"] = self.ui_view.txtLongPs.get()
        self.config_manager.config["rdsps_settings"]["center_title_info"] = self.ui_view.center_title_info_var.get()
        self.config_manager.config["rdsps_settings"]["center_station_name"] = self.ui_view.center_station_name_var.get()
        self.config_manager.config["rdsps_settings"]["remove_accents"] = self.ui_view.rdsps_remove_accents_var.get()
        self.config_manager.config["rdsps_settings"]["message_duration"] = int(self.ui_view.sbRdspsMessageDuration.get())
        self.config_manager.config["rdsps_settings"]["title_info_repeats"] = int(self.ui_view.sbRdspsTitleInfoRepeats.get())
        self.config_manager.config["rdsps_settings"]["station_name_repeats"] = int(self.ui_view.sbRdspsStationNameRepeats.get())
        self.config_manager.config["rdsps_settings"]["caps_artist"] = self.ui_view.caps_artist_var.get()
        self.config_manager.config["rdsps_settings"]["caps_title"] = self.ui_view.caps_title_var.get()
        self.reload_config()
        self.config_manager.save_json()

    def send_group_sequence(self):
        sequence = self.ui_view.txtGroupSequence.get()
        if self.validate_group_sequence_format(sequence):
            self.uecp_manager.send_uecp_command("gseq", sequence)

    def validate_group_sequence_format(self, new_sequence):
        split_groups = [t.strip().upper() for t in re.split(r'[, ]+', new_sequence) if t.strip()]
        if not split_groups:
            self.ui_view.show_error("Group sequence error", "Group sequence cannot be empty!")
            return False
        pattern = r"^(1[0-5]|[0-9])[AB]$"
        for group in split_groups:
            if not re.match(pattern, group):
                self.ui_view.show_error("Group sequence error", f"Found invalid RDS group in sequence: '{group}'.")
                return False
        return True

    def validate_duration(self, new_duration):
        if new_duration == "":
                return True
        try:
            value = int(new_duration)
            return 1 <= value <= 60
        except ValueError:
            return False

    def validate_network_port(self, new_port):
        if new_port == "":
                return True
        try:
            value = int(new_port)
            return 1 <= value <= 65535
        except ValueError:
            return False

    def validate_dsnpsn(self, new_dsnpsn):
        if new_dsnpsn == "":
                return True
        try:
            value = int(new_dsnpsn)
            return 0 <= value <= 255
        except ValueError:
            return False

    def validate_rt_repeat(self, new_rt_repeat):
        if new_rt_repeat == "":
                return True
        try:
            value = int(new_rt_repeat)
            return 0 <= value <= 15
        except ValueError:
            return False

    def validate_rdj_trigger_value(self, new_trigger_value):
        if new_trigger_value == "":
                return True
        try:
            value = int(new_trigger_value)
            return 0 <= value <= 100
        except ValueError:
            return False
        
    def validate_ptyn_field(self, new_ptyn_value):
        return len(new_ptyn_value) <= 8
    
    def validate_pi_code(self, new_pi_value):
        if new_pi_value == "":
            return True
        if len(new_pi_value) > 4:
            return False
        is_hex = re.match(r"^[0-9a-fA-F]+$", new_pi_value)
        return bool(is_hex)
    
    def validate_ecc_lic(self, new_ecc_lic_value):
        if new_ecc_lic_value == "":
            return True
        if len(new_ecc_lic_value) > 2:
            return False
        is_hex = re.match(r"^[0-9a-fA-F]+$", new_ecc_lic_value)
        return bool(is_hex)

    def validate_dns(self, new_dns_value):
        if new_dns_value == "":
            return True
        
        valid = re.match(r"^[a-zA-Z0-9\.\:\-]+$", new_dns_value)
        return bool(valid)
    
    def validate_group_sequence(self, new_gs_value):
        if new_gs_value == "":
            return True
        is_hex = re.match(r"^[0-9a-fA-F,\s]+$", new_gs_value)
        return bool(is_hex)

    def validate_odaflag_freq(self, new_freq):
        if new_freq == "":
                return True
        try:
            value = int(new_freq)
            return 1 <= value <= 100000
        except ValueError:
            return False

    def reload_config(self):
        self.config_manager.reload_data()

    def validate_rdsps_duration(self, new_rdsps_duration):
        if new_rdsps_duration == "":
                return True
        try:
            value = int(new_rdsps_duration)
            return 1 <= value <= 60
        except ValueError:
            return False
        
    def validate_rdsps_repeat(self, new_rdsps_repeat):
        if new_rdsps_repeat == "":
                return True
        try:
            value = int(new_rdsps_repeat)
            return 0 <= value <= 20
        except ValueError:
            return False

    def validate_lps(self, new_lps):
        return len(new_lps) <= 32

    def load_data_into_gui(self):
        self.ui_view.lblPtyMonC["text"] = f"{self.config_manager.current_pty} | {self.ui_view.ptyDict[self.config_manager.current_pty]}"
        self.ui_view.lblPtynMonC["text"] = self.config_manager.current_ptyn
        self.ui_view.lblPiMonC["text"] = f"{self.config_manager.static_rds["pi"]:X}"
        self.ui_view.tp_check_var.set(self.config_manager.static_rds["ta"]["tp"])
        self.ui_view.ta_check_var.set(self.config_manager.static_rds["ta"]["ta"])
        self.ui_view.ms_check_var.set(self.config_manager.static_rds["ms"])
        self.ui_view.txtPi.insert(0, f"{self.config_manager.static_rds["pi"]:X}")
        self.ui_view.txtAf.insert("1.0", "\n".join(map(str, self.config_manager.static_rds["af"])))
        self.ui_view.txtDefPtyn.insert(0, self.config_manager.static_rds["default_ptyn"])
        self.ui_view.di_stereo_var.set(self.config_manager.static_rds["diptyi"]["ms"])
        self.ui_view.di_ah_var.set(self.config_manager.static_rds["diptyi"]["ah"])
        self.ui_view.di_comp_var.set(self.config_manager.static_rds["diptyi"]["cmp"])
        self.ui_view.di_dynpty_var.set(self.config_manager.static_rds["diptyi"]["dpty"])
        self.ui_view.tp_conf_var.set(self.config_manager.static_rds["ta"]["tp"])
        self.ui_view.ta_conf_var.set(self.config_manager.static_rds["ta"]["ta"])
        self.ui_view.ms_conf_var.set(self.config_manager.static_rds["ms"])
        self.ui_view.txtEcc.insert(0, f"{self.config_manager.static_rds["ecc"]:02X}")
        self.ui_view.txtLic.insert(0, f"{self.config_manager.static_rds["lic"]:02X}")
        self.ui_view.cmbDefPty.current(self.config_manager.static_rds["default_pty"])
        self.load_data_into_tvDefaultRt()
        self.ui_view.enable_schedule_var.set(self.config_manager.config["enable_showschedule"])
        self.ui_view.sbScheduleRtDuration.set(self.config_manager.config["showstringrt_duration"])
        self.load_data_into_tvDailyTimetable()
        self.ui_view.txtRadiotextFormatTemplate.insert(0, self.config_manager.config["radiotext"]["titleinfo_format_template"])
        self.ui_view.sbDefaultRtDuration.set(self.config_manager.config["radiotext"]["defaultrt_duration"])
        self.ui_view.sbTitleinfoDuration.set(self.config_manager.config["radiotext"]["titleinfo_duration"])
        self.ui_view.cmbTitleinfoMode.current(self.config_manager.config["radiotext"]["titleinfo_mode"])
        self.ui_view.remove_accents_var.set(self.config_manager.config["radiotext"]["titleinfo_remove_accents"])
        self.ui_view.capitalize_artist_var.set(self.config_manager.config["radiotext"]["titleinfo_caps_artist"])
        self.ui_view.capitalize_title_var.set(self.config_manager.config["radiotext"]["titleinfo_caps_title"])
        self.ui_view.trim_prefix_suffix_var.set(self.config_manager.config["radiotext"]["titleinfo_trim_prefix_suffix"])
        self.ui_view.txtRadioDjIp.insert(0, self.config_manager.config["radiodj_listen"]["ip"])
        self.ui_view.sbRadioDjPort.set(self.config_manager.config["radiodj_listen"]["port"])
        self.ui_view.enable_ws_var.set(self.config_manager.config["uecp_server"]["enabled"])
        self.ui_view.sbWsDsn.set(self.config_manager.config["uecp_settings"]["dsn"])
        self.ui_view.sbWsPsn.set(self.config_manager.config["uecp_settings"]["psn"])
        self.ui_view.enable_local_var.set(self.config_manager.config["local_encoder"]["enabled"])
        self.ui_view.txtWsIp.insert(0, self.config_manager.config["uecp_server"]["ip"])
        self.ui_view.txtWsPswd.insert(0, self.config_manager.config["uecp_server"]["password"])
        self.ui_view.txtLocalEncIp.insert(0, self.config_manager.config["local_encoder"]["ip"])
        self.ui_view.sbLocalEncPort.set(self.config_manager.config["local_encoder"]["port"])
        self.ui_view.cmbTimezone.set(self.config_manager.config["timezone"])
        self.ui_view.txtRdjNewsTriggerKey.insert(0, self.config_manager.config["rdj_news_trigger_key"])
        self.ui_view.news_in_rt_var.set(self.config_manager.config["show_news_in_rt"])
        self.ui_view.sbRdjNewsTriggerValue.set(self.config_manager.config["rdj_news_trigger_value"])
        self.ui_view.txtGroupSequence.insert(0, self.config_manager.config["uecp_settings"]["group_sequence"])
        self.ui_view.cmbNewsPty.current(self.config_manager.config["static_rds"]["news_pty"])
        self.ui_view.txtNewsPtyn.insert(0, self.config_manager.config["static_rds"]["news_ptyn"])
        self.ui_view.txtInstanceName.insert(0, self.config_manager.config["instance_name"])
        self.ui_view.sbRadiotextRepeat.set(self.config_manager.config["uecp_settings"]["rt_repeat"])
        self.ui_view.cmbRtpGroup.set(self.ui_view.group_dict.get(self.config_manager.config["uecp_settings"]["rtp_group"]))
        self.ui_view.sbOdaflagFreq.insert(0, self.config_manager.config["uecp_settings"]["odaflag_send_frequency"])
        self.ui_view.cmbRtpMethod.set(self.ui_view.rtp_method_dict.get(self.config_manager.config["uecp_settings"]["rtp_method"]))
        self.ui_view.rt_termination_var.set(self.config_manager.config["uecp_settings"]["rt_termination"])
        self.ui_view.txtGvcSeq.insert(0, ", ".join(map(str, self.config_manager.config["static_rds"]["gvc_seq"])))
        self.ui_view.ab_toggle_var.set(self.config_manager.config["uecp_settings"]["ab_toggle"])
        self.ui_view.rdsps_dyn_ps_var.set(self.config_manager.config["rdsps_settings"]["dyn_ps"])
        self.ui_view.txtDefaultPs.insert(0, self.config_manager.config["rdsps_settings"]["station_name"])
        self.ui_view.txtTitleInfoFormat.insert(0, self.config_manager.config["rdsps_settings"]["title_info_format"])
        self.ui_view.txtLongPs.insert(0, self.config_manager.config["static_rds"]["lps"])
        self.ui_view.center_title_info_var.set(self.config_manager.config["rdsps_settings"]["center_title_info"])
        self.ui_view.center_station_name_var.set(self.config_manager.config["rdsps_settings"]["center_station_name"])
        self.ui_view.rdsps_remove_accents_var.set(self.config_manager.config["rdsps_settings"]["remove_accents"])
        self.ui_view.sbRdspsMessageDuration.set(self.config_manager.config["rdsps_settings"]["message_duration"])
        self.ui_view.sbRdspsTitleInfoRepeats.set(self.config_manager.config["rdsps_settings"]["title_info_repeats"])
        self.ui_view.sbRdspsStationNameRepeats.set(self.config_manager.config["rdsps_settings"]["station_name_repeats"])
        self.ui_view.caps_artist_var.set(self.config_manager.config["rdsps_settings"]["caps_artist"])
        self.ui_view.caps_title_var.set(self.config_manager.config["rdsps_settings"]["caps_title"])

    def update_monitor(self):
        try:
            self.ui_view.lblRdsPsMon["text"] = self.rdsps_queue.popleft()
        except IndexError:
            pass  # Ignore, if no text available.
        try:
            self.ui_view.lblRtMon["text"] = self.rdsrt_queue.popleft()
        except IndexError:
            pass  # Ignore, if no text available.
        try:
            rdspty = self.rdspty_queue.popleft()
            self.ui_view.lblPtyMonC["text"] = f"{rdspty} | {self.ui_view.ptyDict[rdspty]}"
        except IndexError:
            pass  # Ignore, if no text available.
        try:
            self.ui_view.lblPtynMonC["text"] = self.rdsptyn_queue.popleft()
        except IndexError:
            pass  # Ignore, if no text available.
        try:
            self.ui_view.lblPiMonC["text"] = self.rdspi_queue.popleft()
        except IndexError:
            pass  # Ignore, if no text available.
        try:
            self.ui_view.lblPinMonC["text"] = self.rdspin_queue.popleft()
        except IndexError:
            pass  # Ignore, if no text available.
        try:
            self.ui_view.tp_check_var.set(self.rdstp_queue.popleft())
        except IndexError:
            pass  # Ignore, if no text available.
        try:
            self.ui_view.ta_check_var.set(self.rdsta_queue.popleft())
        except IndexError:
            pass  # Ignore, if no text available.
        try:
            self.ui_view.ms_check_var.set(self.rdsms_queue.popleft())
        except IndexError:
            pass  # Ignore, if no text available.
        try:
            self.ui_view.rtp_check_var.set(self.rdsrtp_queue.popleft())
        except IndexError:
            pass  # Ignore, if no text available.
        try:
            if self.ws_queue.popleft():
                self.ui_view.lblWsStatusC["text"] = "Connected"
                self.ui_view.lblWsStatusC["foreground"] = "#009933"
            else:
                self.ui_view.lblWsStatusC["text"] = "Not connected"
                self.ui_view.lblWsStatusC["foreground"] = "#ff0000"
        except IndexError:
            pass  # Ignore, if no text available.
        try:
            if self.tcp_queue.popleft():
                self.ui_view.lblTcpStatusC["text"] = "Connected"
                self.ui_view.lblTcpStatusC["foreground"] = "#009933"
            else:
                self.ui_view.lblTcpStatusC["text"] = "Not connected"
                self.ui_view.lblTcpStatusC["foreground"] = "#ff0000"
        except IndexError:
            pass  # Ignore, if no text available.
        self.ui_view.root.after(ms=100, func=self.update_monitor)