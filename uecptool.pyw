from ConfigManager import ConfigManager
from EncoderConnection import EncoderConnection
from UiController import UiController
from UecpManager import UecpManager
from UiView import UiView
from AutomationConnection import AutomationConnection
from ScheduleEngine import ScheduleEngine
from App import App
from Logger import Logger
import tkinter as tk

if __name__ == "__main__":
        logger = Logger()
        logger.start_logging()
        config_manager = ConfigManager()
        config_manager.init_data()
        root = tk.Tk()
        root.resizable(False, False)
        root.title("UECP tool - " + config_manager.config["instance_name"])
        encoder_connection = EncoderConnection(config_manager)
        controller = UiController(config_manager, encoder_connection)
        encoder_connection.set_controller(controller)
        ui_view = UiView(root, controller)
        controller.set_view(ui_view)
        uecp_manager = UecpManager(config_manager, controller, encoder_connection)
        controller.set_uecp_manager(uecp_manager)
        automation_connection = AutomationConnection(config_manager, uecp_manager)
        schedule_engine = ScheduleEngine(config_manager, uecp_manager, automation_connection)
        automation_connection.set_schedule_engine(schedule_engine)
        automation_connection.connect()
        automation_connection.start_thread()
        schedule_engine.startTimeThread()
        controller.load_data_into_gui()
        app = App(config_manager, automation_connection, uecp_manager, schedule_engine)
        app.start_threads()
        controller.update_monitor()
        root.mainloop()