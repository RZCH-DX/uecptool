import time
import websocket
import socket
import base64
import json
import threading
import logging
import queue

class EncoderConnection:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.controller = None
        self.ws = websocket.WebSocket()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_recv_thread = threading.Thread(target=self._recv_tcp_connection)
        self.sender_thread = threading.Thread(target=self._uecp_sender)
        self.send_queue = queue.Queue()
        self.logger = logging.getLogger(__name__)
        self.sender_thread_running = False
        self.recv_thread_running = False

    def set_controller(self, controller):
        self.controller = controller

    def connect(self):
        self.logger.info("Connecting to encoders...")
        if self.ws != None:
            self.ws.close()
        if self.sock != None:
            self.sock.close()
        if self.config_manager.config["local_encoder"]["enabled"]:
            self.sock = self._connect_to_local_encoder()
            if not self.recv_thread_running:
                self.recv_thread_running = True
                self.tcp_recv_thread.daemon = True
                self.tcp_recv_thread.start()
        if self.config_manager.config["uecp_server"]["enabled"]:
            self.ws = self._connect_to_websocket()
        if not self.sender_thread_running:
            self.sender_thread_running = True
            self.sender_thread.daemon = True
            self.sender_thread.start()

    # Thread function to receive data from the TCP client
    def _recv_tcp_connection(self):
        while True:
            try:
                self.sock.recv(4096)
            except Exception as e:
                pass
            time.sleep(1)

    # Function to connect to the websocket UECP server
    def _connect_to_websocket(self):
        local_ws = websocket.WebSocket()
        self.logger.info("Trying to connect to UECP server: " + self.config_manager.UECP_SERVER_IP)
        try:
            local_ws.connect(self.config_manager.UECP_SERVER_IP)
            self.logger.info("WebSocket connection was successful")
            self.controller.ws_queue.append(True)
            return local_ws
        except Exception as e:
            self.logger.error(f"UECP WebSocket connection failed: {e}")
            self.controller.ws_queue.append(False)
            return None

    # Function to connect to local Encoder
    def _connect_to_local_encoder(self):
        local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.info("Trying to connect to local encoder over TCP: " + self.config_manager.LOCAL_ENCODER_IP + ":" + str(self.config_manager.LOCAL_ENCODER_PORT))
        try:
            local_sock.connect((self.config_manager.LOCAL_ENCODER_IP, self.config_manager.LOCAL_ENCODER_PORT))
            self.logger.info("Local encoder TCP connection was successful")
            self.controller.tcp_queue.append(True)
            return local_sock
        except Exception as e:
            self.logger.error(f"Local encoder TCP connection failed: {e}")
            self.controller.tcp_queue.append(False)
            return None

    def _stop_connection(self, socket):
        if socket:
            try:
                socket.close()
            except Exception:
                pass

    def submit(self, uecp):
        self.send_queue.put(uecp)
    
    def _send_uecp(self, uecp):
        if self.config_manager.config["local_encoder"]["enabled"]:
            try:
                self.sock.send(uecp)
            except Exception as e:
                self.logger.warning(f"TCP connection lost: {e}")
                self._stop_connection(self.sock)
                self.sock = self._connect_to_local_encoder()
        jsonData = {}
        jsonData['pswd'] = self.config_manager.UECP_SERVER_PSWD
        jsonData['uecp'] = base64.b64encode(uecp).decode('UTF-8')
        if self.config_manager.config["uecp_server"]["enabled"]:
            try:
                self.ws.send(json.dumps(jsonData))
            except Exception as e:
                self.logger.warning(f"UECP WebSocket connection lost: {e}")
                self._stop_connection(self.ws)
                self.ws = self._connect_to_websocket()

    def _uecp_sender(self):
        while True:
            self._send_uecp(self.send_queue.get())