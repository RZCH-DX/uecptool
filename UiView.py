import logging
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from zoneinfo import available_timezones
from RtObject import RtObject

class UiView:

    ptyDict = {
        0 : "No PTY",
        1 : "News",
        2 : "Current Affairs",
        3 : "Information",
        4 : "Sport",
        5 : "Education",
        6 : "Drama",
        7 : "Culture",
        8 : "Science",
        9 : "Varied",
        10 : "Pop Music",
        11 : "Rock Music",
        12 : "Easy Listening",
        13 : "Light Classical",
        14 : "Serious Classical",
        15 : "Other Music",
        16 : "Weather",
        17 : "Finance",
        18 : "Children's Programme",
        19 : "Social Affairs",
        20 : "Religion",
        21 : "Phone-in",
        22 : "Travel",
        23 : "Leisure",
        24 : "Jazz Music",
        25 : "Country Music",
        26 : "National Music",
        27 : "Oldies Music",
        28 : "Folk Music",
        29 : "Documentary",
        30 : "Alarm Test",
        31 : "Alarm",
    }

    rtpDict = {
        0: "Tag disabled",
        1: "Item.Title",
        2: "Item.Album",
        3: "Item.Tracknumber",
        4: "Item.Artist",
        5: "Item.Composition",
        6: "Item.Movement",
        7: "Item.Conductor",
        8: "Item.Composer",
        9: "Item.Band",
        10: "Item.Comment",
        11: "Item.Genre",
        12: "Info.News",
        13: "Info.News.Local",
        14: "Info.Stockmarket",
        15: "Info.Sport",
        16: "Info.Lottery",
        17: "Info.Horoscope",
        18: "Info.Daily_Diversion",
        19: "Info.Health",
        20: "Info.Event",
        21: "Info.Scene",
        22: "Info.Cinema",
        23: "Info.TV",
        24: "Info.Date_Time",
        25: "Info.Weather",
        26: "Info.Traffic",
        27: "Info.Alarm",
        28: "Info.Advertisement",
        29: "Info.URL",
        30: "Info.Other",
        31: "Stationname.Short",
        32: "Stationname.Long",
        33: "Programme.Now",
        34: "Programme.Next",
        35: "Programme.Part",
        36: "Programme.Host",
        37: "Programme.Editorial_Staff",
        38: "Programme.Frequency",
        39: "Programme.Homepage",
        40: "Programme.Subchannel",
        41: "Phone.Hotline",
        42: "Phone.Studio",
        43: "Phone.Other",
        44: "SMS.Studio",
        45: "SMS.Other",
        46: "Email.Hotline",
        47: "Email.Studio",
        48: "Email.Other",
        49: "MMS.Other",
        50: "Chat",
        51: "Chat.Center",
        52: "Vote.Question",
        53: "Vote.Center",
        54: "(Reserved 54)",
        55: "(Reserved 55)",
        56: "(Private 56)",
        57: "(Private 57)",
        58: "(Private 58)",
        59: "Place",
        60: "Appointment",
        61: "Identifier",
        62: "Purchase",
        63: "Get_Data"
    }

    group_dict = {
        10: "5A",
        12: "6A",
        14: "7A",
        16: "8A",
        18: "9A",
        22: "11A",
        24: "12A",
        26: "13A"
    }

    rtp_method_dict = {
        "MEC24": "MEC24 (better compatibility)",
        "MEC40+46": "MEC40+46 (cleaner + modern)"
    }

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.master = root
        self.tk = tk
        self.translator = self.safe_i18n_translator
        _ = self.translator  # i18n string marker.
        self.image_loader = self.safe_image_loader
        self.on_first_object_cb = self.safe_fo_callback
        self.vcmdduration = (self.root.register(self.controller.validate_duration), "%P")
        self.vcmdnwport = (self.root.register(self.controller.validate_network_port), "%P")
        self.vcmddsnpsn = (self.root.register(self.controller.validate_dsnpsn), "%P")
        self.vcmdrtrepeat = (self.root.register(self.controller.validate_rt_repeat), "%P")
        self.vcmdrdjtrigger = (self.root.register(self.controller.validate_rdj_trigger_value), "%P")
        self.vcmdptyn = (self.root.register(self.controller.validate_ptyn_field), "%P")
        self.vcmdpi = (self.root.register(self.controller.validate_pi_code), "%P")
        self.vcmdecclic = (self.root.register(self.controller.validate_ecc_lic), "%P")
        self.vcmddns = (self.root.register(self.controller.validate_dns), "%P")
        self.vcmdgs = (self.root.register(self.controller.validate_group_sequence), "%P")
        self.vcmdodaflagfreq = (self.root.register(self.controller.validate_odaflag_freq), "%P")
        self.vcmdpsduration = (self.root.register(self.controller.validate_rdsps_duration), "%P")
        self.vcmdpsrepeat = (self.root.register(self.controller.validate_rdsps_repeat), "%P")
        self.vcmdlps = (self.root.register(self.controller.validate_lps), "%P")
        self.schedule_rt_temp = []
        self.logger = logging.getLogger(__name__)
        self.main_window()

    def safe_i18n_translator(self, value):
        """i18n - Setup translator in derived class file"""
        return value


    def safe_fo_callback(self, widget):
        """on first objec callback - Setup callback in derived class file."""
        pass


    def safe_image_loader(self, master, image_name: str):
        """Image loader - Setup image_loader in derived class file."""
        return tk.PhotoImage(file=image_name, master=master)


    def find_callback(self, callbacks_bag, callback_uid):
        cb = None

        if isinstance(callbacks_bag, dict):
            if callback_uid in callbacks_bag:
                cb = callbacks_bag[callback_uid]
        elif hasattr(callbacks_bag, callback_uid):
            cb = getattr(callbacks_bag, callback_uid)
        if cb is None:

            def cb_undef(*args):
                self.logger.warning(f"No function defined for {callback_uid}")

            cb = cb_undef
        return cb
    
    def show_error(self, title, message, parent=None):
        messagebox.showerror(title, message, parent=parent)

    def rtpEditor(self, mode, index, list_name, show_index):
        def validate_64(text):
            return len(text) <= 64
        def validate_32(text):
            return len(text) <= 32
        def save_new_RT():
            radiotext = txtRadiotext.get()
            tag1_content = txtTag1Content.get()
            tag1_item = cmbTag1Item.current()
            if radiotext == "":
                self.show_error("RT+ error", "Radiotext field cannot be empty!", parent=rtpEditor)
                return
            if tag1_item != 0:
                tag1_start = radiotext.find(tag1_content)
                if tag1_start < 0:
                    self.show_error("RT+ error", "Couldn't find specified RT+ tag 1 content!", parent=rtpEditor)
                    return
                tag1_length = len(tag1_content) - 1
            else:
                tag1_start = 0
                tag1_length = 0
            tag2_content = txtTag2Content.get()
            tag2_item = cmbTag2Item.current()
            if tag2_item != 0:
                tag2_start = radiotext.find(tag2_content)
                if tag2_start < 0:
                    self.show_error("RT+ error", "Couldn't find specified RT+ tag 2 content!", parent=rtpEditor)
                    return
                tag2_length = len(tag2_content) - 1
            else:
                tag2_start = 0
                tag2_length = 0
            running_bit = tag1_item != 0 or tag2_item != 0
            self.controller.save_radiotext_entry(
                mode,
                index,
                list_name,
                show_index,
                radiotext,
                [False, running_bit, tag1_item, tag1_start, tag1_length, tag2_item, tag2_start, tag2_length],
                self.schedule_rt_temp,
            )
            rtpEditor.destroy()
        translator = self.safe_i18n_translator
        _ = translator  # i18n string marker.
        image_loader = self.safe_image_loader
        on_first_object_cb = self.safe_fo_callback
        if translator is None:
            translator = self.safe_i18n_translator
        _ = translator  # i18n
        if image_loader is None:
            image_loader = self.safe_image_loader
        if on_first_object_cb is None:
            on_first_object_cb = self.safe_fo_callback
        rtpEditor = tk.Toplevel(self.master)
        vcmd64 = rtpEditor.register(validate_64)
        vcmd32 = rtpEditor.register(validate_32)
        rtpEditor.transient(self.root)
        rtpEditor.grab_set()
        rtpEditor.title(mode + " RT string... - UECP tool - " + self.controller.get_instance_name())
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        s_width = self.root.winfo_width()
        s_height = self.root.winfo_height()
        width = 600
        height = 200
        pos_x = x + (s_width // 2) - (width // 2)
        pos_y = y + (s_height // 2) - (height // 2)
        rtpEditor.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        rtpEditor.resizable(False, False)
        rtpEditor.grid_rowconfigure(0, weight=1)
        rtpEditor.grid_columnconfigure(0, weight=1)
        frame30 = ttk.Frame(rtpEditor)
        frame30.grid(row=0, column=0, sticky="nsew")
        frame30.grid_columnconfigure(0, weight=0)
        frame30.grid_columnconfigure(1, weight=1)
        for r in (2,):
            frame30.grid_rowconfigure(r, weight=1)
        on_first_object_cb(rtpEditor)
        lblRadiotext = ttk.Label(frame30, name="lblradiotext", text="Radiotext string:")
        lblRadiotext.grid(row=0, column=0, sticky="w")
        txtRadiotext = ttk.Entry(frame30, name="txtradiotext", validate="key", validatecommand=(vcmd64, "%P"))
        txtRadiotext.grid(row=0, column=1, sticky="ew")
        labelframe6 = ttk.Labelframe(frame30, text="Radiotext+")
        labelframe6.grid(row=2, column=0, columnspan=2, sticky="nsew")
        labelframe6.grid_columnconfigure(0, weight=1)
        labelframe6.grid_rowconfigure(0, weight=1)
        labelframe6.grid_rowconfigure(1, weight=1)
        labelframe7 = ttk.Labelframe(labelframe6, text="Tag 1 (max. 64 characters)")
        labelframe7.grid(row=0, column=0, sticky="nsew")
        labelframe7.grid_columnconfigure(0, weight=0)
        labelframe7.grid_columnconfigure(1, weight=1)
        lblTag1Item = ttk.Label(labelframe7, name="lbltag1item", text="RT+ tag:")
        lblTag1Item.grid(row=0, column=0, sticky="w")
        lblTag1Content = ttk.Label(labelframe7, name="lbltag1content", text="RT+ content:")
        lblTag1Content.grid(row=0, column=1, sticky="w")
        cmbTag1Item = ttk.Combobox(labelframe7, name="cmbtag1item", width=24, state="readonly", values=list(self.rtpDict.values()))
        cmbTag1Item.current(0)
        cmbTag1Item.grid(row=1, column=0, sticky="ew")
        txtTag1Content = ttk.Entry(labelframe7, name="txttag1content", validate="key", validatecommand=(vcmd64, "%P"))
        txtTag1Content.grid(row=1, column=1, sticky="ew")
        labelframe9 = ttk.Labelframe(labelframe6, text="Tag 2 (max. 32 characters)")
        labelframe9.grid(row=1, column=0, sticky="nsew")
        labelframe9.grid_columnconfigure(0, weight=0)
        labelframe9.grid_columnconfigure(1, weight=1)
        lblTag2Item = ttk.Label(labelframe9, name="lbltag2item", text="RT+ tag:")
        lblTag2Item.grid(row=0, column=0, sticky="w")
        lblTag2Content = ttk.Label(labelframe9, name="lbltag2content", text="RT+ content:")
        lblTag2Content.grid(row=0, column=1, sticky="w")
        cmbTag2Item = ttk.Combobox(labelframe9, name="cmbtag2item", width=24, state="readonly", values=list(self.rtpDict.values()))
        cmbTag2Item.current(0)
        cmbTag2Item.grid(row=1, column=0, sticky="ew")
        txtTag2Content = ttk.Entry(labelframe9, name="txttag2content", validate="key", validatecommand=(vcmd32, "%P"))
        txtTag2Content.grid(row=1, column=1, sticky="ew")
        buttonbar = ttk.Frame(frame30)
        buttonbar.grid(row=3, column=0, columnspan=2, sticky="e", padx=5, pady=5)
        buttonbar.grid_columnconfigure(0, weight=0)
        buttonbar.grid_columnconfigure(1, weight=0)
        btnSaveRtpEditor = ttk.Button(buttonbar, name="btnsavertpeditor", text="Save", command=save_new_RT)
        btnSaveRtpEditor.grid(row=0, column=0)
        btnCancelRtpEditor = ttk.Button(buttonbar, name="btncancelrtpeditor", text="Cancel", command=rtpEditor.destroy)
        btnCancelRtpEditor.grid(row=0, column=1)
        if mode == "Edit":
            source = self.controller.get_radiotext_source(list_name, show_index)
            if list_name == "specialshow" and show_index is None:
                source = self.schedule_rt_temp
            txtRadiotext.insert(0, source[index]["text"])
            cmbTag1Item.current(source[index]["rtplus"][2])
            if not source[index]["rtplus"][2] == 0:
                txtTag1Content.insert(0, source[index]["text"][source[index]["rtplus"][3]:source[index]["rtplus"][3]+source[index]["rtplus"][4]+1])
            cmbTag2Item.current(source[index]["rtplus"][5])
            if not source[index]["rtplus"][5] == 0:
                txtTag2Content.insert(0, source[index]["text"][source[index]["rtplus"][6]:source[index]["rtplus"][6]+source[index]["rtplus"][7]+1])
        return rtpEditor

    def scheduleEditor(self, mode, index):
        self.schedule_rt_temp = []
        def validate_hour(new_hour):
            if new_hour == "":
                return True

            try:
                value = int(new_hour)
                return 0 <= value <= 24
            except ValueError:
                return False
        def load_data_into_tvScheduleRt():
            tvScheduleRt.delete(*tvScheduleRt.get_children())
            if mode == "Add":
                scheduleRTStrings = [
                    RtObject(
                        entry["rtplus"],
                        entry["text"]
                    )
                    for entry in self.schedule_rt_temp
                ]
            if mode == "Edit":
                scheduleRTStrings = [
                    RtObject(
                        entry["rtplus"],
                        entry["text"]
                    )
                    for entry in self.controller.get_schedule_entry(index)["radiotexts"]
                ]
            for rt_string in scheduleRTStrings:
                tvScheduleRt.insert("", tk.END, values=(rt_string.radio_text,))
        def add_scheduleRt_tv():
            self.root.wait_window(self.rtpEditor("Add", None, "specialshow", index))
            load_data_into_tvScheduleRt()
        def edit_scheduleRt_Tv(indexRt):
            self.root.wait_window(self.rtpEditor("Edit", indexRt, "specialshow", index))
            load_data_into_tvScheduleRt()
        def delete_scheduleRt_tv(indexRt):
            if messagebox.askyesno("Delete RT string - UECP tool - " + self.controller.get_instance_name(), "Are you sure you want to delete this RT string?", parent=scheduleEditor):
                if mode == "Add":
                    self.schedule_rt_temp.pop(indexRt)
                if mode == "Edit":
                    self.controller.delete_schedule_radiotext(indexRt, index)
                self.controller.reload_config()
                load_data_into_tvScheduleRt()
        def on_select_scheduleRt(event):
            selected = event.widget.selection()
            if selected:
                indexRt = tvScheduleRt.index(selected[0])
                btnEditScheduleRt.configure(state="enabled", command=lambda:edit_scheduleRt_Tv(indexRt))
                btnRemoveScheduleRt.configure(state="enabled", command=lambda:delete_scheduleRt_tv(indexRt))
            else:
                btnEditScheduleRt.configure(state="disabled", command=lambda:edit_scheduleRt_Tv(None))
                btnRemoveScheduleRt.configure(state="disabled", command=lambda:delete_scheduleRt_tv(None))
        def save_new_show():
            try:
                start_hour = int(sbScheduleStarthour.get())
                stop_hour = int(sbScheduleStophour.get())
            except Exception as e:
                self.show_error("Schedule error", "Start/Stop hour fields cannot be empty!", parent=scheduleEditor)
                return
            schedule_pty = cmbSchedulePty.current()
            schedule_ptyn = txtSchedulePtyn.get()
            schedule_name = txtScheduleShowname.get()
            if schedule_name == "":
                self.show_error("Schedule error", "Schedule name cannot be empty!", parent=scheduleEditor)
                return

            updated_weekdays = [scheduleEditor.day_vars[i].get() for i in range(7)]
            self.controller.save_schedule_entry(
                mode,
                index,
                schedule_name,
                start_hour,
                stop_hour,
                updated_weekdays,
                schedule_pty,
                schedule_ptyn,
                scheduleEditor.update_pin_check_var.get(),
                self.schedule_rt_temp,
            )
            self.schedule_rt_temp = []
            scheduleEditor.destroy()
        vcmdvh = (self.root.register(validate_hour), "%P")
        translator = self.safe_i18n_translator
        _ = translator  # i18n string marker.
        image_loader = self.safe_image_loader
        on_first_object_cb = self.safe_fo_callback
        if translator is None:
            translator = self.safe_i18n_translator
        _ = translator  # i18n
        if image_loader is None:
            image_loader = self.safe_image_loader
        if on_first_object_cb is None:
            on_first_object_cb = self.safe_fo_callback
        scheduleEditor = tk.Toplevel(self.master)
        scheduleEditor.transient(self.root)
        scheduleEditor.grab_set()
        scheduleEditor.title(mode + " schedule entry... - UECP tool - " + self.controller.get_instance_name())
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        s_width = self.root.winfo_width()
        s_height = self.root.winfo_height()
        width = 300
        height = 420
        pos_x = x + (s_width // 2) - (width // 2)
        pos_y = y + (s_height // 2) - (height // 2)
        scheduleEditor.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        scheduleEditor.resizable(False, False)
        on_first_object_cb(scheduleEditor)
        scheduleEditor.grid_rowconfigure(0, weight=1)
        scheduleEditor.grid_columnconfigure(0, weight=1)
        frame44 = ttk.Frame(scheduleEditor)
        frame44.grid(row=0, column=0, sticky="nsew")
        frame44.grid_columnconfigure(0, weight=0)
        frame44.grid_columnconfigure(1, weight=1)
        frame44.grid_rowconfigure(2, weight=1)
        leftPane = ttk.Frame(frame44)
        leftPane.grid(row=0, column=0, sticky="nsew")
        leftPane.grid_columnconfigure(0, weight=1)
        lblScheduleStarthour = ttk.Label(leftPane, name="lblschedulestarthour", text="Start hour:")
        lblScheduleStarthour.grid(row=0, column=0, sticky="w")
        sbScheduleStarthour = ttk.Spinbox(leftPane, name="sbschedulestarthour", from_=0, to=24, validate="key", validatecommand=vcmdvh)
        sbScheduleStarthour.grid(row=1, column=0, sticky="w")
        lblSchedulePty = ttk.Label(leftPane, name="lblschedulepty", text="PTY:")
        lblSchedulePty.grid(row=2, column=0, sticky="w")
        cmbSchedulePty = ttk.Combobox(leftPane, name="cmbschedulepty", width=21, state="readonly", values=list(self.ptyDict.values()))
        cmbSchedulePty.current(0)
        cmbSchedulePty.grid(row=3, column=0, sticky="ew")
        lblScheduleShowname = ttk.Label(leftPane, name="lblscheduleshowname", text="Show name:")
        lblScheduleShowname.grid(row=4, column=0, sticky="w")
        txtScheduleShowname = ttk.Entry(leftPane, name="txtscheduleshowname")
        txtScheduleShowname.grid(row=5, column=0, sticky="ew")
        days_container = ttk.Frame(leftPane)
        days_container.grid(row=6, column=0, sticky="w", pady=(10, 5))
        days = ["M", "T", "W", "T", "F", "S", "S"]
        scheduleEditor.day_vars = {} 
        for i, day in enumerate(days):
            day_col = ttk.Frame(days_container)
            day_col.grid(row=0, column=i, padx=1) 

            lblDay = ttk.Label(day_col, text=day, font=("Helvetica", 7))
            lblDay.pack(side="top")

            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(day_col, variable=var)
            cb.pack(side="top")
            scheduleEditor.day_vars[i] = var
        rightPane = ttk.Frame(frame44)
        rightPane.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        rightPane.grid_columnconfigure(0, weight=1)
        lblScheduleStophour = ttk.Label(rightPane, name="lblschedulestophour", text="Stop hour:")
        lblScheduleStophour.grid(row=0, column=0, sticky="w")
        sbScheduleStophour = ttk.Spinbox(rightPane, name="sbschedulestophour", from_=0, to=24, validate="key",validatecommand=vcmdvh)
        sbScheduleStophour.grid(row=1, column=0, sticky="w")
        lblSchedulePtyn = ttk.Label(rightPane, name="lblscheduleptyn", text="PTYN:")
        lblSchedulePtyn.grid(row=2, column=0, sticky="w")
        txtSchedulePtyn = ttk.Entry(rightPane, name="txtscheduleptyn", validate="key", validatecommand=(self.vcmdptyn))
        txtSchedulePtyn.grid(row=3, column=0, sticky="ew")
        scheduleEditor.update_pin_check_var = tk.BooleanVar(value=True) 
        cbUpdatePin = ttk.Checkbutton(rightPane, text="Update PIN", variable=scheduleEditor.update_pin_check_var)
        cbUpdatePin.grid(row=5, column=0, sticky="w", pady=(15, 0))
        lblScheduleRt = ttk.Label(frame44, name="lblschedulert", text="Radiotext strings:")
        lblScheduleRt.grid(row=1, column=0, columnspan=2, sticky="w")
        tvScheduleRt = ttk.Treeview(frame44, name="tvschedulert", selectmode="extended", height=7, columns=("radiotext"), show="headings")
        tvScheduleRt.heading("radiotext", text="Radiotext")
        tvScheduleRt.bind("<<TreeviewSelect>>", on_select_scheduleRt)
        tvScheduleRt.grid(row=2, column=0, columnspan=2, sticky="nsew")
        buttonBar = ttk.Frame(frame44)
        buttonBar.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))
        btnAddScheduleRt = ttk.Button(buttonBar, name="btnaddschedulert", text="Add", command=lambda:add_scheduleRt_tv())
        btnAddScheduleRt.grid(row=0, column=0)
        btnEditScheduleRt = ttk.Button(buttonBar, name="btneditschedulert", text="Edit", state="disabled")
        btnEditScheduleRt.grid(row=0, column=1)
        btnRemoveScheduleRt = ttk.Button(buttonBar, name="btnremoveschedulert", text="Remove", state="disabled")
        btnRemoveScheduleRt.grid(row=0, column=2)
        actionBar = ttk.Frame(frame44)
        actionBar.grid(row=4, column=0, columnspan=2, sticky="e", padx=5, pady=5)
        actionBar.grid_columnconfigure(0, weight=0)
        actionBar.grid_columnconfigure(1, weight=0)
        btnSaveScheduleEntry = ttk.Button(actionBar, name="btnsavescheduleentry", text="Save", command=save_new_show)
        btnSaveScheduleEntry.grid(row=0, column=0)
        btnCancelScheduleEntry = ttk.Button(actionBar, name="btncancelscheduleentry", text="Cancel", command=scheduleEditor.destroy)
        btnCancelScheduleEntry.grid(row=0, column=1)
        if mode == "Edit":
            show_data = self.controller.get_schedule_entry(index)
            sbScheduleStarthour.set(show_data["from_hour"])
            sbScheduleStophour.set(show_data["to_hour"])
            cmbSchedulePty.current(show_data["pty"])
            txtSchedulePtyn.insert(0, show_data["ptyn"])
            txtScheduleShowname.insert(0, show_data["name"])
            scheduleEditor.update_pin_check_var.set(show_data["update_pin"])
            for i, active in enumerate(show_data["weekdays"]):
                scheduleEditor.day_vars[i].set(active)
            load_data_into_tvScheduleRt()
        return scheduleEditor
    def main_window(self):
        # Begin UI code
        nbApp = ttk.Notebook(self.master, name="nbapp")
        nbApp.configure(height=300, width=500)
        # First object created
        self.on_first_object_cb(nbApp)
        frmMonitor = ttk.Frame(nbApp, name="frmmonitor")
        frmMonitor.configure(height=200, width=200)
        lblRdsPsMon = ttk.Label(frmMonitor, name="lblrdspsmon")
        self.lblRdsPsMon = lblRdsPsMon
        lblRdsPsMon.configure(
            anchor="center",
            background="#000000",
            font="{Arial} 24 {}",
            foreground="#ffffff",
            text='RDS PS',
            width=100)
        lblRdsPsMon.pack(side="top")
        lblRtMon = ttk.Label(frmMonitor, name="lblrtmon")
        self.lblRtMon = lblRtMon
        lblRtMon.configure(
            anchor="center",
            background="#000000",
            font="{Arial} 10 {}",
            foreground="#ffffff",
            text='Radio text',
            width=100)
        lblRtMon.pack(side="top")
        pwMon2 = ttk.Frame(frmMonitor, name="pwmon2")
        pwMon2.configure(height=200, width=450)
        frmTextMon = ttk.Frame(pwMon2, name="frmtextmon")
        frmTextMon.configure(height=80, width=200)
        paneTextMon = ttk.Panedwindow(
            frmTextMon,
            orient="horizontal",
            name="panetextmon")
        paneTextMon.configure(height=80, width=450)
        frmTextLabels = ttk.Frame(paneTextMon, name="frmtextlabels")
        frmTextLabels.configure(height=200, width=10)
        lblPtyMon = ttk.Label(frmTextLabels, name="lblptymon")
        lblPtyMon.configure(text='PTY:')
        lblPtyMon.pack(anchor="w", side="top")
        lblPtynMon = ttk.Label(frmTextLabels, name="lblptynmon")
        lblPtynMon.configure(text='PTYN:')
        lblPtynMon.pack(anchor="w", side="top")
        lblPiMon = ttk.Label(frmTextLabels, name="lblpimon")
        lblPiMon.configure(text='PI:')
        lblPiMon.pack(anchor="w", side="top")
        lblPinMon = ttk.Label(frmTextLabels, name="lblpinmon")
        lblPinMon.configure(text='PIN:')
        lblPinMon.pack(anchor="w", side="top")
        frmTextLabels.pack(side="top")
        frmTextLabels.pack_propagate(0)
        paneTextMon.add(frmTextLabels, weight="1")
        frmTextValues = ttk.Frame(paneTextMon, name="frmtextvalues")
        frmTextValues.configure(height=200, width=100)
        lblPtyMonC = ttk.Label(frmTextValues, name="lblptymonc")
        self.lblPtyMonC = lblPtyMonC
        lblPtyMonC.configure(text='0 | None')
        lblPtyMonC.pack(anchor="w", side="top")
        lblPtynMonC = ttk.Label(frmTextValues, name="lblptynmonc")
        self.lblPtynMonC = lblPtynMonC
        lblPtynMonC.configure(text='No PTYN')
        lblPtynMonC.pack(anchor="w", side="top")
        lblPiMonC = ttk.Label(frmTextValues, name="lblpimonc")
        self.lblPiMonC = lblPiMonC
        lblPiMonC.configure(text='FFFF')
        lblPiMonC.pack(anchor="w", side="top")
        lblPinMonC = ttk.Label(frmTextValues, name="lblpinmonc")
        self.lblPinMonC = lblPinMonC
        lblPinMonC.configure(text='0. 00:00')
        lblPinMonC.pack(anchor="w", side="top")
        frmTextValues.pack(side="top")
        frmTextValues.pack_propagate(0)
        paneTextMon.add(frmTextValues, weight="1")
        frame43 = ttk.Frame(paneTextMon)
        frame43.configure(height=200, width=10)
        lblWsStatus = ttk.Label(frame43, name="lblwsstatus")
        lblWsStatus.configure(text='WS status:')
        lblWsStatus.pack(anchor="w", side="top")
        lblTcpStatus = ttk.Label(frame43, name="lbltcpstatus")
        lblTcpStatus.configure(text='TCP status:')
        lblTcpStatus.pack(anchor="w", side="top")
        frame43.pack(side="top")
        frame43.pack_propagate(0)
        paneTextMon.add(frame43, weight="1")
        frame45 = ttk.Frame(paneTextMon)
        frame45.configure(height=200, width=200)
        lblWsStatusC = ttk.Label(frame45, name="lblwsstatusc")
        self.lblWsStatusC = lblWsStatusC
        lblWsStatusC.configure(foreground="#ff0000", text='Not connected')
        lblWsStatusC.pack(anchor="w", side="top")
        lblTcpStatusC = ttk.Label(frame45, name="lbltcpstatusc")
        self.lblTcpStatusC = lblTcpStatusC
        lblTcpStatusC.configure(foreground="#ff0000", text='Not connected')
        lblTcpStatusC.pack(anchor="w", side="top")
        frame45.pack(side="top")
        paneTextMon.add(frame45, weight="1")
        paneTextMon.pack(anchor="w", side="top")
        frmTextMon.grid(row=0, column=0, sticky="nsew")
        frmCheckboxes = ttk.Frame(pwMon2, name="frmcheckboxes")
        frmCheckboxes.configure(height=200, width=200)
        chkTPMon = ttk.Checkbutton(frmCheckboxes, name="chktpmon")
        tp_check_var = tk.BooleanVar()
        self.tp_check_var = tp_check_var
        chkTPMon.configure(state="disabled", text='TP (Traffic Program flag)', variable=tp_check_var)
        chkTPMon.pack(anchor="w", side="top")
        ta_check_var = tk.BooleanVar()
        self.ta_check_var = ta_check_var
        chkTAMon = ttk.Checkbutton(frmCheckboxes, name="chktamon")
        chkTAMon.configure(state="disabled", text='TA (Traffic Announcement flag)', variable=ta_check_var)
        chkTAMon.pack(anchor="w", side="top")
        ms_check_var = tk.BooleanVar()
        self.ms_check_var = ms_check_var
        chkMSMon = ttk.Checkbutton(frmCheckboxes, name="chkmsmon")
        chkMSMon.configure(state="disabled", text='Music/Speech flag (off = Speech, on = Music)', variable=ms_check_var)
        chkMSMon.pack(anchor="w", side="top")
        rtp_check_var = tk.BooleanVar()
        self.rtp_check_var = rtp_check_var
        chkRTPMon = ttk.Checkbutton(frmCheckboxes, name="chkrtpmon")
        chkRTPMon.configure(state="disabled", text='Radiotext+', variable=rtp_check_var)
        chkRTPMon.pack(anchor="w", side="top")
        frmCheckboxes.grid(row=1, column=0, sticky="nsew")
        pwMon2.rowconfigure(0, weight=1)
        pwMon2.rowconfigure(1, weight=1)
        pwMon2.columnconfigure(0, weight=1)
        pwMon2.pack(pady=20, side="top")
        nbApp.add(frmMonitor, text='Monitor')
        panedwindow5 = ttk.Frame(nbApp)
        panedwindow5.configure(height=200, width=200)
        frame13 = ttk.Frame(panedwindow5)
        frame13.configure(height=200, width=200)
        lblPi = ttk.Label(frame13, name="lblpi")
        lblPi.configure(text='PI code:')
        lblPi.pack(anchor="w", side="top")
        txtPi = ttk.Entry(frame13, name="txtpi", validate="key", validatecommand=self.vcmdpi)
        self.txtPi = txtPi
        txtPi.pack(anchor="w", side="top")
        lblAf = ttk.Label(frame13, name="lblaf")
        lblAf.configure(text='AF list:')
        lblAf.pack(anchor="w", side="top")
        txtAf = tk.Text(frame13, name="txtaf")
        self.txtAf = txtAf
        txtAf.configure(height=9, width=15)
        txtAf.pack(anchor="w", side="top")
        lblDefPtyn = ttk.Label(frame13, name="lbldefptyn")
        lblDefPtyn.configure(text='Default PTYN:')
        lblDefPtyn.pack(anchor="w", side="top")
        txtDefPtyn = ttk.Entry(frame13, name="txtdefptyn", validate="key", validatecommand=self.vcmdptyn)
        self.txtDefPtyn = txtDefPtyn
        txtDefPtyn.pack(anchor="w", side="top")
        frame13.grid(row=0, column=0, sticky="nsew")
        frame16 = ttk.Frame(panedwindow5)
        frame16.configure(height=200, width=200)
        labelframe1 = ttk.Labelframe(frame16)
        labelframe1.configure(height=200, text='RDS-DI', width=200)
        di_stereo_var = tk.BooleanVar()
        self.di_stereo_var = di_stereo_var
        chkDiStereo = ttk.Checkbutton(labelframe1, name="chkdistereo")
        chkDiStereo.configure(text='Stereo', variable=di_stereo_var)
        chkDiStereo.pack(anchor="w", side="top")
        di_ah_var = tk.BooleanVar()
        self.di_ah_var = di_ah_var
        chkDiAh = ttk.Checkbutton(labelframe1, name="chkdiah")
        chkDiAh.configure(text='Artificial Head', variable=di_ah_var)
        chkDiAh.pack(anchor="w", side="top")
        di_comp_var = tk.BooleanVar()
        self.di_comp_var = di_comp_var
        chkDiComp = ttk.Checkbutton(labelframe1, name="chkdicomp")
        chkDiComp.configure(text='Compressed', variable=di_comp_var)
        chkDiComp.pack(anchor="w", side="top")
        di_dynpty_var = tk.BooleanVar()
        self.di_dynpty_var = di_dynpty_var
        chkDiDynpty = ttk.Checkbutton(labelframe1, name="chkdidynpty")
        chkDiDynpty.configure(text='Dynamic PTY', variable=di_dynpty_var)
        chkDiDynpty.pack(anchor="w", side="top")
        labelframe1.pack(anchor="w", side="top")
        tp_conf_var = tk.BooleanVar()
        self.tp_conf_var = tp_conf_var
        chkTp = ttk.Checkbutton(frame16, name="chktp")
        chkTp.configure(text='TP', variable=tp_conf_var)
        chkTp.pack(anchor="w", side="top")
        ta_conf_var = tk.BooleanVar()
        self.ta_conf_var = ta_conf_var
        chkTa = ttk.Checkbutton(frame16, name="chkta")
        chkTa.configure(text='TA', variable=ta_conf_var)
        chkTa.pack(anchor="w", side="top")
        ms_conf_var = tk.BooleanVar()
        self.ms_conf_var = ms_conf_var
        chkMs = ttk.Checkbutton(frame16, name="chkms")
        chkMs.configure(text='M/S', variable=ms_conf_var)
        chkMs.pack(anchor="w", side="top")
        panedwindow12 = ttk.Frame(frame16)
        panedwindow12.configure(height=40, width=150)
        frame28 = ttk.Frame(panedwindow12)
        frame28.configure(height=40, width=200)
        lblEcc = ttk.Label(frame28, name="lblecc")
        lblEcc.configure(text='ECC:')
        lblEcc.pack(anchor="w", side="top")
        txtEcc = ttk.Entry(frame28, name="txtecc", validate="key", validatecommand=self.vcmdecclic)
        self.txtEcc = txtEcc
        txtEcc.configure(width=10)
        txtEcc.pack(anchor="w", side="top")
        frame28.grid(row=0, column=0, sticky="nsew")
        frame29 = ttk.Frame(panedwindow12)
        frame29.configure(height=40, width=200)
        lblLic = ttk.Label(frame29, name="lbllic")
        lblLic.configure(text='LIC:')
        lblLic.pack(anchor="w", side="top")
        txtLic = ttk.Entry(frame29, name="txtlic", validate="key", validatecommand=self.vcmdecclic)
        self.txtLic = txtLic
        txtLic.configure(width=10)
        txtLic.pack(anchor="w", side="top")
        frame29.grid(row=0, column=1, sticky="nsew")
        panedwindow12.rowconfigure(0, weight=1)
        panedwindow12.columnconfigure(0, weight=1)
        panedwindow12.columnconfigure(1, weight=1)
        panedwindow12.pack(anchor="w", side="top")
        lblDefPty = ttk.Label(frame16, name="lbldefpty")
        lblDefPty.configure(text='Default PTY:')
        lblDefPty.pack(anchor="w", side="top")
        cmbDefPty = ttk.Combobox(frame16, name="cmbdefpty", state="readonly", values=list(self.ptyDict.values()))
        self.cmbDefPty = cmbDefPty
        cmbDefPty.pack(anchor="w", side="top")
        frame16.grid(row=0, column=1, sticky="nsew")
        frame18 = ttk.Frame(panedwindow5)
        frame18.configure(height=200, width=200)
        lblDefaultRt = ttk.Label(frame18, name="lbldefaultrt")
        lblDefaultRt.configure(text='Default RT strings:')
        lblDefaultRt.pack(anchor="w", side="top")
        tvDefaultRt = ttk.Treeview(frame18, name="tvdefaultrt", columns=("radiotext"), show="headings")
        self.tvDefaultRt = tvDefaultRt
        tvDefaultRt.heading("radiotext", text="Radiotext")
        tvDefaultRt.configure(height=9, selectmode="extended")
        tvDefaultRt.bind("<<TreeviewSelect>>", self.controller.on_select_defaultRt)
        tvDefaultRt.pack(anchor="w", side="top")
        panedwindow8 = ttk.Frame(frame18)
        panedwindow8.configure(height=0, width=200)
        frame24 = ttk.Frame(panedwindow8)
        frame24.configure(height=0, width=200)
        btnAddDefaultRt = ttk.Button(frame24, name="btnadddefaultrt", command=lambda: self.rtpEditor("Add", None, "defaultRt", None))
        btnAddDefaultRt.configure(text='Add', width=9)
        btnAddDefaultRt.pack(side="top")
        frame24.grid(row=0, column=0, sticky="nsew")
        frame25 = ttk.Frame(panedwindow8)
        frame25.configure(height=0, width=200)
        btnEditDefaultRt = ttk.Button(frame25, name="btneditdefaultrt", state="disabled")
        self.btnEditDefaultRt = btnEditDefaultRt
        btnEditDefaultRt.configure(text='Edit', width=10)
        btnEditDefaultRt.pack(side="top")
        frame25.grid(row=0, column=1, sticky="nsew")
        frame26 = ttk.Frame(panedwindow8)
        frame26.configure(height=0, width=200)
        btnRemoveDefaultRt = ttk.Button(frame26, name="btnremovedefaultrt", state="disabled")
        self.btnRemoveDefaultRt = btnRemoveDefaultRt
        btnRemoveDefaultRt.configure(text='Remove', width=10)
        btnRemoveDefaultRt.pack(side="top")
        frame26.grid(row=0, column=2, sticky="nsew")
        panedwindow8.rowconfigure(0, weight=1)
        panedwindow8.columnconfigure(0, weight=1)
        panedwindow8.columnconfigure(1, weight=1)
        panedwindow8.columnconfigure(2, weight=1)
        panedwindow8.pack(anchor="w", side="top")
        btnSaveRdsConf = ttk.Button(frame18, name="btnsaverdsconf", command=self.controller.save_rds_conf)
        btnSaveRdsConf.configure(text='Save')
        btnSaveRdsConf.pack(anchor="se", padx=5, pady=5, side="bottom")
        frame18.grid(row=0, column=2, sticky="nsew")
        panedwindow5.rowconfigure(0, weight=1)
        panedwindow5.columnconfigure(0, weight=1)
        panedwindow5.columnconfigure(1, weight=1)
        panedwindow5.columnconfigure(2, weight=1)
        nbApp.add(panedwindow5, text='RDS Config')
        frame35 = ttk.Frame(nbApp)
        frame35.grid_rowconfigure(0, weight=1)
        frame35.grid_columnconfigure(0, weight=1)
        frame36 = ttk.Frame(frame35)
        frame36.grid(row=0, column=0, sticky="nsew")
        frame36.grid_columnconfigure(0, weight=1)
        frame36.grid_columnconfigure(1, weight=1)
        enable_schedule_var = tk.BooleanVar()
        self.enable_schedule_var = enable_schedule_var
        chkEnableSchedule = ttk.Checkbutton(frame36, text="Enable schedule", name="chkenableschedule", variable=enable_schedule_var)
        chkEnableSchedule.grid(row=0, column=0, sticky="w", padx=(0, 15))
        lblScheduleRtDuration = ttk.Label(frame36, text="Schedule RT duration (sec.):")
        lblScheduleRtDuration.grid(row=0, column=1, sticky="w")
        sbScheduleRtDuration = ttk.Spinbox(frame36, from_=1, to=60, validate="key", validatecommand=self.vcmdduration)
        self.sbScheduleRtDuration = sbScheduleRtDuration
        sbScheduleRtDuration.grid(row=1, column=1, sticky="ew")
        lblDailyTimetable = ttk.Label(frame36, name="lbldailytimetable", text="Weekly Timetable:")
        lblDailyTimetable.grid(row=2, column=0, columnspan=2, sticky="w")
        tvDailyTimetable = ttk.Treeview(frame36, name="tvdailytimetable", columns=("name", "days", "from_hour", "to_hour", "pty", "ptyn"), show="headings", selectmode="extended")
        self.tvDailyTimetable = tvDailyTimetable
        tvDailyTimetable.heading("name", text="Show name")
        tvDailyTimetable.heading("days", text="Show days")
        tvDailyTimetable.heading("from_hour", text="Start hour")
        tvDailyTimetable.heading("to_hour", text="End hour")
        tvDailyTimetable.heading("pty", text="PTY")
        tvDailyTimetable.heading("ptyn", text="PTYN")
        tvDailyTimetable.column("name", width=150)
        tvDailyTimetable.column("days", width=120)
        tvDailyTimetable.column("from_hour", width=50)
        tvDailyTimetable.column("to_hour", width=50)
        tvDailyTimetable.column("pty", width=50)
        tvDailyTimetable.column("ptyn", width=70)
        tvDailyTimetable.bind("<<TreeviewSelect>>", self.controller.on_select_timetable)
        tvDailyTimetable.grid(row=3, column=0, columnspan=2, sticky="nsew")
        panedwindow15 = ttk.Frame(frame36)
        panedwindow15.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        panedwindow15.grid_columnconfigure(0, weight=0)
        panedwindow15.grid_columnconfigure(1, weight=0)
        panedwindow15.grid_columnconfigure(2, weight=1)
        frame38 = ttk.Frame(panedwindow15)
        frame38.grid(row=0, column=0, sticky="w")
        btnAddTimetableEntry = ttk.Button(frame38, name="btnaddtimetableentry", text="Add", command=lambda:self.scheduleEditor("Add", None))
        btnAddTimetableEntry.pack()
        frame39 = ttk.Frame(panedwindow15)
        frame39.grid(row=0, column=1, sticky="w", padx=(10, 0))
        btnEditTimetableEntry = ttk.Button(frame39, name="btnedittimetableentry", text="Edit", state="disabled")
        self.btnEditTimetableEntry = btnEditTimetableEntry
        btnEditTimetableEntry.pack()
        frame40 = ttk.Frame(panedwindow15)
        frame40.grid(row=0, column=2, sticky="w", padx=(10, 0))
        btnRemoveTimetableEntry = ttk.Button(frame40, name="btnremovetimetableentry", text="Remove", state="disabled")
        self.btnRemoveTimetableEntry = btnRemoveTimetableEntry
        btnRemoveTimetableEntry.pack()
        frame36.rowconfigure(3, weight=1)
        frame36.columnconfigure(0, weight=1)
        frame36.columnconfigure(1, weight=1)
        btnSaveSchedule = ttk.Button(frame35, name="btnsaveschedule", text="Save", command=self.controller.save_schedule)
        btnSaveSchedule.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        nbApp.add(frame35, text='Schedule')
        frame19 = ttk.Frame(nbApp)
        frame19.grid_rowconfigure(0, weight=0)
        frame19.grid_rowconfigure(1, weight=1)
        frame19.grid_rowconfigure(2, weight=0)
        frame19.grid_columnconfigure(0, weight=1)
        template_frame = ttk.Frame(frame19)
        template_frame.grid(row=0, column=0, sticky="ew")
        template_frame.grid_columnconfigure(0, weight=1)
        lblRadiotextFormatTemplate = ttk.Label(template_frame, text="Title info RT format template:")
        lblRadiotextFormatTemplate.grid(row=0, column=0, sticky="w", pady=0)
        txtRadiotextFormatTemplate = ttk.Entry(template_frame)
        self.txtRadiotextFormatTemplate = txtRadiotextFormatTemplate
        txtRadiotextFormatTemplate.grid(row=1, column=0, sticky="ew", pady=2)
        container = ttk.Frame(frame19)
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        lblDefaultRtDuration = ttk.Label(container, text="Default RT string duration (sec.):")
        lblDefaultRtDuration.grid(row=0, column=0, sticky="w", pady=0)
        sbDefaultRtDuration = ttk.Spinbox(container, width=33, from_=1, to=60, validate="key", validatecommand=self.vcmdduration)
        self.sbDefaultRtDuration = sbDefaultRtDuration
        sbDefaultRtDuration.grid(row=1, column=0, sticky="w", pady=0)
        lblTitleinfoMode = ttk.Label(container, text="Radiotext switch mode:")
        lblTitleinfoMode.grid(row=2, column=0, sticky="w", pady=0)
        cmbTitleinfoMode = ttk.Combobox(container, width=32, state="readonly", values=("0 (repeat title info after all predef. RT)", "1 (repeat title info after every predef. RT)", "2 (show default RT if title unavailable)"))
        self.cmbTitleinfoMode = cmbTitleinfoMode
        cmbTitleinfoMode.grid(row=3, column=0, sticky="w", pady=0)
        lblTitleinfoDuration = ttk.Label(container, text="Title info RT duration (sec.):")
        lblTitleinfoDuration.grid(row=0, column=1, sticky="w", padx=(40, 0), pady=0)
        sbTitleinfoDuration = ttk.Spinbox(container, width=33, from_=1, to=60, validate="key", validatecommand=self.vcmdduration)
        self.sbTitleinfoDuration = sbTitleinfoDuration
        sbTitleinfoDuration.grid(row=1, column=1, sticky="w", padx=(40, 0), pady=0)
        remove_accents_var = tk.BooleanVar()
        self.remove_accents_var = remove_accents_var
        chkTitleinfoRemoveAccents = ttk.Checkbutton(container, text="Remove accents", variable=remove_accents_var)
        chkTitleinfoRemoveAccents.grid(row=2, column=1, sticky="w", padx=(40, 0), pady=0)
        capitalize_artist_var = tk.BooleanVar()
        self.capitalize_artist_var = capitalize_artist_var
        chkTitleinfoCapitalizeArtist = ttk.Checkbutton(container, text="Capitalize artist name", variable=capitalize_artist_var)
        chkTitleinfoCapitalizeArtist.grid(row=3, column=1, sticky="w", padx=(40, 0), pady=0)
        capitalize_title_var = tk.BooleanVar()
        self.capitalize_title_var = capitalize_title_var
        chkTitleinfoCapitalizeTitle = ttk.Checkbutton(container, text="Capitalize title name", variable=capitalize_title_var)
        chkTitleinfoCapitalizeTitle.grid(row=4, column=1, sticky="w", padx=(40, 0), pady=0)
        trim_prefix_suffix_var = tk.BooleanVar()
        self.trim_prefix_suffix_var = trim_prefix_suffix_var
        chkTitleinfoTrimPrefixSuffix = ttk.Checkbutton(container, text="Trim prefix and suffix if space runs out", variable=trim_prefix_suffix_var)
        chkTitleinfoTrimPrefixSuffix.grid(row=5, column=1, sticky="w", padx=(40, 0), pady=0)
        btnSaveTitleinfoConfig = ttk.Button(frame19, text="Save", command=self.controller.save_titleinfo_conf)
        btnSaveTitleinfoConfig.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        nbApp.add(frame19, text='Title info')
        frame20 = ttk.Frame(nbApp)
        frame20.grid_columnconfigure(0, weight=1)
        frame20.grid_rowconfigure(2, weight=1)
        autoFrame = ttk.LabelFrame(frame20, text="Automation data source (e.g. RadioDJ; UDP)")
        autoFrame.grid(row=0, column=0, sticky="ew")
        ttk.Label(autoFrame, text="Listen on IP:").grid(row=0, column=0, sticky="w")
        txtRadioDjIp = ttk.Entry(autoFrame, width=55)
        self.txtRadioDjIp = txtRadioDjIp
        txtRadioDjIp.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))
        ttk.Label(autoFrame, text="Listen on port:").grid(row=0, column=1, sticky="w")
        sbRadioDjPort = ttk.Spinbox(autoFrame, width=22, from_=1, to=65535, validate="key", validatecommand=self.vcmdnwport)
        self.sbRadioDjPort = sbRadioDjPort
        sbRadioDjPort.grid(row=1, column=1, sticky="ew", pady=(0, 10))
        uecpFrame = ttk.LabelFrame(frame20, text="UECP websocket server connection")
        uecpFrame.grid(row=1, column=0, sticky="ew")
        for c in range(5):
            uecpFrame.grid_columnconfigure(c, weight=1)
        uecpFrame.grid_columnconfigure(0, weight=2)
        enable_ws_var = tk.BooleanVar()
        self.enable_ws_var = enable_ws_var
        chkEnableWs = ttk.Checkbutton(uecpFrame, text="Enable", variable=enable_ws_var)
        chkEnableWs.grid(row=0, column=0, sticky="w")
        ttk.Label(uecpFrame, text="Websocket address:").grid(row=2, column=0, sticky="w", pady=(0, 2))
        ttk.Label(uecpFrame, text="Password:").grid(row=2, column=4, sticky="w", pady=(0, 2))
        txtWsIp = ttk.Entry(uecpFrame)
        self.txtWsIp = txtWsIp
        txtWsIp.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 10), padx=(0, 8))
        txtWsPswd = ttk.Entry(uecpFrame, show="•")
        self.txtWsPswd = txtWsPswd
        txtWsPswd.grid(row=3, column=4, sticky="ew", pady=(0, 10))
        encFrame = ttk.LabelFrame(frame20, text="Local RDS encoder connection (TCP)")
        encFrame.grid(row=2, column=0, sticky="ew")
        for i in range(4):
            encFrame.grid_columnconfigure(i, weight=1)
        enable_local_var = tk.BooleanVar()
        self.enable_local_var = enable_local_var
        chkEnableLocal = ttk.Checkbutton(encFrame, text="Enable", variable=enable_local_var)
        chkEnableLocal.grid(row=0, column=0, sticky="w")
        ttk.Label(encFrame, text="IP/DNS:").grid(row=0, column=1, sticky="w")
        ttk.Label(encFrame, text="Port:").grid(row=0, column=2, sticky="w")
        txtLocalEncIp = ttk.Entry(encFrame, width=42, validate="key", validatecommand=self.vcmddns)
        self.txtLocalEncIp = txtLocalEncIp
        txtLocalEncIp.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))
        sbLocalEncPort = ttk.Spinbox(encFrame, width=22, from_=1, to=65535, validate="key", validatecommand=self.vcmdnwport)
        self.sbLocalEncPort = sbLocalEncPort
        sbLocalEncPort.grid(row=1, column=2, sticky="ew", pady=(0, 10))
        btnSaveNetworkSetup = ttk.Button(frame20, text="Save", command=self.controller.save_network_setup)
        btnSaveNetworkSetup.grid(row=3, column=0, sticky="e", padx=5, pady=5)
        nbApp.add(frame20, text='Network Setup')
        frame21 = ttk.Frame(nbApp)
        frame21.grid_columnconfigure(0, weight=1)
        frame21.grid_rowconfigure(0, weight=1)
        settingsContainer = ttk.Frame(frame21)
        settingsContainer.grid(row=0, column=0, sticky="nsew")
        settingsContainer.grid_columnconfigure(0, weight=1)
        settingsContainer.grid_columnconfigure(1, weight=1)
        lblTimezone = ttk.Label(settingsContainer, text='Time zone:')
        lblTimezone.grid(row=0, column=0, sticky='w')
        cmbTimezone = ttk.Combobox(settingsContainer, state="readonly", values=sorted(available_timezones()))
        self.cmbTimezone = cmbTimezone
        cmbTimezone.grid(row=1, column=0, sticky='ew', padx=(0,20))
        news_in_rt_var = tk.BooleanVar()
        self.news_in_rt_var = news_in_rt_var
        chkShowNewsInRt = ttk.Checkbutton(settingsContainer, text='Show news title data in RT', name="chkshownewsinrt", variable=news_in_rt_var)
        chkShowNewsInRt.grid(row=2, column=0, sticky='w', padx=(0,20))
        lblNewsPty = ttk.Label(settingsContainer, text='PTY during news:')
        lblNewsPty.grid(row=3, column=0, sticky='w')
        cmbNewsPty = ttk.Combobox(settingsContainer, state="readonly", name='cmbnewspty', values=list(self.ptyDict.values()))
        self.cmbNewsPty = cmbNewsPty
        cmbNewsPty.grid(row=4, column=0, sticky='ew', padx=(0,20))
        lblInstanceName = ttk.Label(settingsContainer, text='Instance/Station name:')
        lblInstanceName.grid(row=5, column=0, sticky='w')
        txtInstanceName = ttk.Entry(settingsContainer, name='txtInstanceName')
        self.txtInstanceName = txtInstanceName
        txtInstanceName.grid(row=6, column=0, sticky='ew', padx=(0,20))
        lblRdjNewsTriggerKey = ttk.Label(settingsContainer, text='RadioDJ news trigger key:')
        lblRdjNewsTriggerKey.grid(row=0, column=1, sticky='w')
        txtRdjNewsTriggerKey = ttk.Entry(settingsContainer, name='txtrdjnewstriggerkey')
        self.txtRdjNewsTriggerKey = txtRdjNewsTriggerKey
        txtRdjNewsTriggerKey.grid(row=1, column=1, sticky='ew')
        lblRdjNewsTriggerValue = ttk.Label(settingsContainer, text='RadioDJ news trigger value:')
        lblRdjNewsTriggerValue.grid(row=2, column=1, sticky='w')
        sbRdjNewsTriggerValue = ttk.Spinbox(settingsContainer, name='txtrdjnewstriggervalue', from_=0, to=100, validate="key", validatecommand=self.vcmdrdjtrigger)
        self.sbRdjNewsTriggerValue = sbRdjNewsTriggerValue
        sbRdjNewsTriggerValue.grid(row=3, column=1, sticky='ew')
        lblNewsPtyn = ttk.Label(settingsContainer, text='PTYN during news:')
        lblNewsPtyn.grid(row=4, column=1, sticky='w')
        txtNewsPtyn = ttk.Entry(settingsContainer, name='txtnewsptyn', validate="key", validatecommand=self.vcmdptyn)
        self.txtNewsPtyn = txtNewsPtyn
        txtNewsPtyn.grid(row=5, column=1, sticky='ew')
        btnSaveSettings = ttk.Button(frame21, text='Save', name='btnsavesettings', command=self.controller.save_settings)
        btnSaveSettings.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        nbApp.add(frame21, text='Settings')
        # UECP Tab
        frameUecp = ttk.Frame(nbApp, name="frameuecp")
        frameUecp.grid_columnconfigure(0, weight=1)
        frameUecp.grid_rowconfigure(0, weight=0)
        frameUecp.grid_rowconfigure(1, weight=0)
        frameUecp.grid_rowconfigure(2, weight=1)
        frameUecp.grid_rowconfigure(3, weight=0)
        uecpContainer = ttk.Frame(frameUecp)
        uecpContainer.grid(row=0, column=0, sticky="nsew")
        uecpContainer.grid_columnconfigure(0, weight=1, uniform="uecp_cols")
        uecpContainer.grid_columnconfigure(1, weight=1, uniform="uecp_cols")
        ttk.Label(uecpContainer, text="DSN:").grid(row=1, column=0, sticky="w", pady=5)
        sbWsDsn = ttk.Spinbox(uecpContainer, from_=0, to=255, validate="key", validatecommand=self.vcmddsnpsn)
        self.sbWsDsn = sbWsDsn
        sbWsDsn.grid(row=2, column=0, sticky="ew", pady=(0, 5),  padx=(0, 5))
        sbRadiotextRepeat = ttk.Spinbox(uecpContainer, from_=0, to=15, validate="key", validatecommand=self.vcmdrtrepeat)
        self.sbRadiotextRepeat = sbRadiotextRepeat
        sbRadiotextRepeat.grid(row=4, column=0, sticky="ew", pady=(0, 5), padx=(0, 5))
        lblOdaflagFreq = ttk.Label(uecpContainer, text='RT+ ODA flag frequency (millisec.):')
        lblOdaflagFreq.grid(row=5, column=0, sticky='w')
        sbOdaflagFreq = ttk.Spinbox(uecpContainer, from_=100, to=100000, validate="key", validatecommand=self.vcmdodaflagfreq)
        self.sbOdaflagFreq = sbOdaflagFreq
        sbOdaflagFreq.grid(row=6, column=0, sticky='ew', padx=(0, 5))
        lblGvcSeq = ttk.Label(uecpContainer, text='1A group variant sequence:')
        lblGvcSeq.grid(row=7, column=0, sticky='w')
        txtGvcSeq = ttk.Entry(uecpContainer, name='txtgvcseq', validate="key", validatecommand=self.vcmdgs)
        self.txtGvcSeq = txtGvcSeq
        txtGvcSeq.grid(row=8, column=0, sticky='ew', padx=(0, 5))
        ttk.Label(uecpContainer, text="PSN:").grid(row=1, column=1, sticky="w", pady=5, padx=(5, 0))
        sbWsPsn = ttk.Spinbox(uecpContainer, from_=0, to=255, validate="key", validatecommand=self.vcmddsnpsn)
        self.sbWsPsn = sbWsPsn
        sbWsPsn.grid(row=2, column=1, sticky="ew", pady=(0, 5), padx=(5, 0))
        ttk.Label(uecpContainer, text="Radiotext repeat (0 is recommended!):").grid(row=3, column=0, sticky="w")
        ab_toggle_var = tk.BooleanVar()
        self.ab_toggle_var = ab_toggle_var
        chkAbToggle = ttk.Checkbutton(uecpContainer, text="A/B toggle", variable=ab_toggle_var)
        chkAbToggle.grid(row=3, column=1, sticky="w", padx=(5, 0))
        rt_termination_var = tk.BooleanVar()
        self.rt_termination_var = rt_termination_var
        chkRtTermination = ttk.Checkbutton(uecpContainer, text="0x0D RT termination", variable=rt_termination_var)
        chkRtTermination.grid(row=4, column=1, sticky="w", pady=(0, 5), padx=(5, 0))
        lblRtpGroup = ttk.Label(uecpContainer, text='RT+ group:')
        lblRtpGroup.grid(row=5, column=1, sticky='w', padx=(5, 0))
        cmbRtpGroup = ttk.Combobox(uecpContainer, state="readonly", values=list(self.group_dict.values()))
        self.cmbRtpGroup = cmbRtpGroup
        cmbRtpGroup.grid(row=6, column=1, sticky="ew", pady=0, padx=(5, 0))
        lblRtpMethod = ttk.Label(uecpContainer, text='RT+ method:')
        lblRtpMethod.grid(row=7, column=1, sticky='w', padx=(5, 0))
        cmbRtpMethod = ttk.Combobox(uecpContainer, state="readonly", values=list(self.rtp_method_dict.values()))
        self.cmbRtpMethod = cmbRtpMethod
        cmbRtpMethod.grid(row=8, column=1, sticky="ew", pady=0, padx=(5, 0))
        gscontainer = ttk.Frame(frameUecp)
        gscontainer.grid(row=1, column=0, sticky="nsew")
        gscontainer.grid_columnconfigure(0, weight=1)
        gscontainer.grid_columnconfigure(1, weight=0)
        lblGroupSequence = ttk.Label(gscontainer, text='Manual Group Sequence override:')
        lblGroupSequence.grid(row=1, column=0, sticky='w')
        txtGroupSequence = ttk.Entry(gscontainer, name='txtgvcseq', validate="key", validatecommand=self.vcmdgs)
        self.txtGroupSequence = txtGroupSequence
        txtGroupSequence.grid(row=2, column=0, sticky='ew', padx=(0, 5))
        btnSendGroupSequence = ttk.Button(gscontainer, text='Send', name='btnsavegroupsequence', command=self.controller.send_group_sequence)
        btnSendGroupSequence.grid(row=2, column=1, sticky='w')
        btnSaveUecp = ttk.Button(frameUecp, text='Save', name='btnsaveuecp', command=self.controller.save_uecp)
        btnSaveUecp.grid(row=3, column=0, sticky='e', padx=5, pady=5)
        nbApp.add(frameUecp, text='UECP')
        # RDS PS Tab
        frameRdsPs = ttk.Frame(nbApp, name="framerdsps")
        frameRdsPs.grid_columnconfigure(0, weight=1)
        frameRdsPs.grid_rowconfigure(0, weight=1)
        rdsPsContainer = ttk.Frame(frameRdsPs)
        rdsPsContainer.grid(row=0, column=0, sticky="nsew")
        rdsPsContainer.grid_columnconfigure(0, weight=1)
        rdsPsContainer.grid_columnconfigure(1, weight=1)
        left_col = ttk.Frame(rdsPsContainer)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=(2, 0))
        left_col.grid_columnconfigure(0, weight=1)
        right_col = ttk.Frame(rdsPsContainer)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=(2, 0))
        right_col.grid_columnconfigure(0, weight=1)
        dyn_ps_var = tk.BooleanVar()
        self.rdsps_dyn_ps_var = dyn_ps_var
        chkDynPs = ttk.Checkbutton(left_col, text="Enable dynamic title info PS", variable=dyn_ps_var)
        chkDynPs.grid(row=0, column=0, sticky="w")
        lblDefaultPs = ttk.Label(left_col, name="lbldefaultps")
        lblDefaultPs.configure(text='Station Name:')
        lblDefaultPs.grid(row=1, column=0, sticky="w", pady=(2, 0))
        txtDefaultPs = ttk.Entry(left_col, name="txtdefaultps")
        self.txtDefaultPs = txtDefaultPs
        txtDefaultPs.grid(row=2, column=0, sticky="ew", pady=(0, 2))
        lblTitleInfoFormat = ttk.Label(left_col, text='Title info format:')
        lblTitleInfoFormat.grid(row=3, column=0, sticky="w")
        txtTitleInfoFormat = ttk.Entry(left_col, name="txttitleinfoformat")
        self.txtTitleInfoFormat = txtTitleInfoFormat
        txtTitleInfoFormat.grid(row=4, column=0, sticky="ew", pady=(0, 2))
        caps_artist_var = tk.BooleanVar()
        self.caps_artist_var = caps_artist_var
        chk_caps_artist = ttk.Checkbutton(left_col, text='Capitalize artist name', variable=caps_artist_var)
        chk_caps_artist.grid(row=5, column=0, sticky="w")
        caps_title_var = tk.BooleanVar()
        self.caps_title_var = caps_title_var
        chk_caps_title = ttk.Checkbutton(left_col, text='Capitalize title name', variable=caps_title_var)
        chk_caps_title.grid(row=6, column=0, sticky="w")
        lblLongPs = ttk.Label(left_col, text='Long PS:')
        lblLongPs.grid(row=7, column=0, sticky="w")
        txtLongPs = ttk.Entry(left_col, name="txtlongps", validate="key", validatecommand=self.vcmdlps)
        self.txtLongPs = txtLongPs
        txtLongPs.grid(row=8, column=0, sticky="ew", pady=(0, 2))
        center_title_info_var = tk.BooleanVar()
        self.center_title_info_var = center_title_info_var
        chkCenterTitleInfo = ttk.Checkbutton(right_col, text='Center title info', variable=center_title_info_var)
        chkCenterTitleInfo.grid(row=0, column=0, sticky="w")
        center_station_name_var = tk.BooleanVar()
        self.center_station_name_var = center_station_name_var
        chkCenterStationName = ttk.Checkbutton(right_col, text='Center station name', variable=center_station_name_var)
        chkCenterStationName.grid(row=1, column=0, sticky="w", pady=(1, 0))
        rdsps_remove_accents_var = tk.BooleanVar()
        self.rdsps_remove_accents_var = rdsps_remove_accents_var
        chkRdspsRemoveAccents = ttk.Checkbutton(right_col, text='Remove accents', variable=rdsps_remove_accents_var)
        chkRdspsRemoveAccents.grid(row=2, column=0, sticky="w", pady=(1, 0))
        lblMessageDuration = ttk.Label(right_col, text='Message duration (sec.):')
        lblMessageDuration.grid(row=3, column=0, sticky="w", pady=(2, 0))
        sbMessageDuration = ttk.Spinbox(right_col, from_=1, to=60, validate="key", validatecommand=self.vcmdpsduration)
        self.sbRdspsMessageDuration = sbMessageDuration
        sbMessageDuration.grid(row=4, column=0, sticky="ew", pady=(0, 2))
        lblTitleInfoRepeats = ttk.Label(right_col, text='Title info repeats (0 = infinite):')
        lblTitleInfoRepeats.grid(row=5, column=0, sticky="w")
        sbTitleInfoRepeats = ttk.Spinbox(right_col, from_=0, to=20, validate="key", validatecommand=self.vcmdpsrepeat)
        self.sbRdspsTitleInfoRepeats = sbTitleInfoRepeats
        sbTitleInfoRepeats.grid(row=6, column=0, sticky="ew", pady=(0, 2))
        lblStationNameRepeats = ttk.Label(right_col, text='Station name repeats:')
        lblStationNameRepeats.grid(row=7, column=0, sticky="w")
        sbStationNameRepeats = ttk.Spinbox(right_col, from_=0, to=20, validate="key", validatecommand=self.vcmdpsrepeat)
        self.sbRdspsStationNameRepeats = sbStationNameRepeats
        sbStationNameRepeats.grid(row=8, column=0, sticky="ew", pady=(0, 2))
        btnSaveRdsps = ttk.Button(frameRdsPs, text='Save', command=self.controller.save_rdsps)
        btnSaveRdsps.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        nbApp.add(frameRdsPs, text='RDS PS')
        nbApp.pack(side="top")