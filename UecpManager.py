import threading
import logging
import re

class UecpManager:
    ebu_chars = {'á': 128, 'à': 129, 'é': 130, 'è': 131, 'í': 132, 'ì': 133, 'ó': 134, 'ò': 135,
             'ú': 136, 'ù': 137, 'Ñ': 138, 'Ç': 139, 'Ş': 140, 'ß': 141, '¡': 142, 'Ĳ': 143,
             'â': 144, 'ä': 145, 'ê': 146, 'ë': 147, 'î': 148, 'ï': 149, 'ô': 150, 'ö': 151,
             'û': 152, 'ü': 153, 'ñ': 154, 'ç': 155, 'ş': 156, 'ğ': 157, 'ı': 158, 'ĳ': 159,
             'ª': 160, 'α': 161, '©': 162, '‰': 163, 'Ğ': 164, 'ě': 165, 'ň': 166, 'ő': 167,
             'π': 168, '€': 169, '£': 170, '$': 171, '←': 172, '↑': 173, '→': 174, '↓': 175,
             '⁰': 176, '¹': 177, '²': 178, '³': 179, '±': 180, 'İ': 181, 'ń': 182, 'ű': 183,
             'μ': 184, '¿': 185, '÷': 186, '°': 187, '¼': 188, '½': 189, '¾': 190, '§': 191,
             'Á': 192, 'À': 193, 'É': 194, 'È': 195, 'Í': 196, 'Ì': 197, 'Ó': 198, 'Ò': 199,
             'Ú': 200, 'Ù': 201, 'Ř': 202, 'Č': 203, 'Š': 204, 'Ž': 205, 'Đ': 206, 'L': 207,
             'Â': 208, 'Ä': 209, 'Ê': 210, 'Ë': 211, 'Î': 212, 'Ï': 213, 'Ô': 214, 'Ö': 215,
             'Û': 216, 'Ü': 217, 'ř': 218, 'č': 219, 'š': 220, 'ž': 221, 'đ': 222, 'l': 223,
             'Ã': 224, 'Å': 225, 'Æ': 226, 'Œ': 227, 'ŷ': 228, 'Ý': 229, 'Õ': 230, 'Ø': 231,
             'Þ': 232, 'Ŋ': 233, 'Ŕ': 234, 'Ć': 235, 'Ś': 236, 'Ź': 237, 'Ŧ': 238, 'ð': 239,
             'ã': 240, 'å': 241, 'æ': 242, 'œ': 243, 'ŵ': 244, 'ý': 245, 'õ': 246, 'ø': 247,
             'þ': 248, 'ŋ': 249, 'ŕ': 250, 'ć': 251, 'ś': 252, 'ź': 253, 'ŧ': 254, 'ÿ': 255}
    
    def __init__(self, config_manager, controller, encoder_connection):
        self._initial_connection_made = False
        self.config_manager = config_manager
        self.controller = controller
        self.encoder_connection = encoder_connection
        self.rt_plus_toggle_bit = False
        self.sqc = 0
        self.addr = bytes([0, 0])
        self.last_rtp = [False, False, 0, 0, 0, 0, 0, 0]
        self.last_rtp_group = self.config_manager.config["uecp_settings"]["rtp_group"]
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)

    def _connect(self):
        with self._lock:
            if not self._initial_connection_made:
                self.encoder_connection.connect()
                self._initial_connection_made = True


    # Function to create 16-bit UECP CRC
    def _crc16_ccitt(self, data: bytes, poly=0x1021, init_crc=0xFFFF) -> bytes:
        crc = init_crc
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ poly
                else:
                    crc <<= 1
                crc &= 0xFFFF  # Ensure it's a 16-bit value
        crc = 0xFFFF - crc # Invert CRC by subtracting from 0xFFFF
        return crc.to_bytes(2, byteorder='big')

    # Function to byte-stuff a UECP packet
    def _uecp_escape_bytes(self, data: bytearray) -> bytearray:
        ESCAPE = 0xFD
        replacements = {
            0xFD: bytearray([ESCAPE, 0x00]),
            0xFE: bytearray([ESCAPE, 0x01]),
            0xFF: bytearray([ESCAPE, 0x02])
        }

        escaped = bytearray()
        for byte in data:
            if byte in replacements:
                escaped.extend(replacements[byte])
            else:
                escaped.append(byte)
        return escaped

    # Function to convert a string to an EBU format byte array
    def _string_to_ebu_bytes(self, text):
        byte_array = bytearray()
        for char in text:
            if ord(char) < 0x80:
                byte_array.append(ord(char))
            elif char in self.ebu_chars:
                byte_array.append(self.ebu_chars[char])
            else:
                byte_array.append(0x20)  # Fallback space for unsupported chars
        return byte_array

    # Function to create and send UECP packets
    def send_uecp_command(self, type, payload):
        self._connect()
        dsn = self.config_manager.config["uecp_settings"]["dsn"]
        psn = self.config_manager.config["uecp_settings"]["psn"]
        msg = None
        match type:
            case "ps":
                psbytes = self._string_to_ebu_bytes(f'{payload: <8}')
                msg = bytes([0x02, dsn, psn]) + psbytes
                self.controller.rdsps_queue.append(payload)
            case "rt":
                if len(payload) > 64 :
                    payload = payload[:61] + '...'
                rtbytes = self._string_to_ebu_bytes(payload)
                if len(rtbytes) < 64 :
                    appendBytes = bytes([0x0D])
                    if not self.config_manager.config["uecp_settings"]["rt_termination"]:
                        appendBytes = bytes([0x20] * (64 - len(rtbytes)))
                    rtbytes = rtbytes + appendBytes
                flags = self.config_manager.config["uecp_settings"]["ab_toggle"] | (self.config_manager.config["uecp_settings"]["rt_repeat"] << 1)
                msg = bytes([0x0A, dsn, psn, len(rtbytes)+1, flags]) + rtbytes
                self.controller.rdsrt_queue.append(payload)
            case "pi":
                pibytes = payload.to_bytes(2, byteorder='big')
                msg = bytes([0x01, dsn, psn]) + pibytes
                self.controller.rdspi_queue.append(f"{payload:X}")
            case "pty":
                msg = bytes([0x07, dsn, psn, payload])
                self.controller.rdspty_queue.append(payload)
            case "af":
                if not payload:
                    return
                af = bytes([int(x * 10 - 875) for x in payload])
                af = bytes([224 + len(af)]) + af
                if len(af) % 2 :
                    af = af + bytes([0xcd])
                af = af + bytes([0x0])
                msg = bytes([0x13, dsn, psn, len(af)+2, 0x0, 0x0]) + af
            case "diptyi":
                flag = 0
                if payload['ms'] :
                    flag = flag | 0x1
                if payload['ah'] :
                    flag = flag | 0x2
                if payload['cmp'] :
                    flag = flag | 0x4
                if payload['dpty'] :
                    flag = flag | 0x8
                msg = bytes([0x04, dsn, psn, flag])
            case "ptyn":
                ptynbytes = self._string_to_ebu_bytes(f'{payload: <8}')
                msg = bytes([0x3e, dsn, psn]) + ptynbytes
                self.controller.rdsptyn_queue.append(payload)
            case "ms":
                msg = bytes([0x05, dsn, psn, (payload & 0x01)])
                self.controller.rdsms_queue.append(payload)
            case "odaflag":
                rtp_group = payload[0]
                odaflag = payload[1].to_bytes(2, byteorder='big')
                buffer_config = 0
                msg = bytes([0x24, 0x06, rtp_group | (buffer_config << 5), 0x00, 0x00]) + odaflag
            case "rtplus":
                rtp_group = self.config_manager.config["uecp_settings"]["rtp_group"]
                if payload[0] == True :
                    # This is a clear buffer message, set flags to 11 and data to zeros
                    msg = bytearray([0x24, self.last_rtp_group, 0x60, 0x0, 0x0, 0x0, 0x0])
                else:
                    self.last_rtp_group = rtp_group
                    # This is a new RT+ Config message, add it to the group in cyclic transmission mode
                    if self.last_rtp != payload:
                        self.rt_plus_toggle_bit = not self.rt_plus_toggle_bit
                    bitstream = 0
                    bitlen = 0
                    bitstream = (bitstream << 3) | 0x2
                    bitlen += 3
                    bitstream = (bitstream << 1) | (self.rt_plus_toggle_bit & 0x1)
                    bitlen += 1
                    bitstream = (bitstream << 1) | (payload[1] & 0x1)
                    bitlen += 1
                    for tag in payload[2:-1]:
                        bitstream = (bitstream << 6) | (tag & 0x3F)
                        bitlen += 6
                    bitstream = (bitstream << 5) | (payload[-1] & 0x1F)
                    bitlen += 5
                    pad = (-bitlen) % 8
                    if pad:
                        bitstream <<= pad
                        bitlen += pad
                    bytes_out = bitstream.to_bytes(bitlen // 8, byteorder="big")
                    msg = bytearray([0x24, rtp_group]) + bytes_out
                    self.last_rtp = payload
                    self.controller.rdsrtp_queue.append(payload[1])
            case "ta":
                flag = 0
                if payload['ta'] :
                    flag = flag | 1
                if payload['tp'] :
                    flag = flag | 2
                msg = bytes([0x03, dsn, psn, flag])
                self.controller.rdstp_queue.append(payload['tp'])
                self.controller.rdsta_queue.append(payload['ta'])
            case "ecc":
                msg = bytes([0x1a, dsn, 0x0, payload])
            case "lic":
                msg = bytes([0x1a, dsn, 0x30, payload])
            case "gvc_seq":
                msg = bytes([0x29, dsn, len(payload)+1, 0x2]) + bytes(payload)
            case "pin":
                if payload[0] > 31 or payload[0] < 0:
                    payload[0] = 0
                if payload[1] > 23 or payload[1] < 0:
                    payload[1] = 0
                if payload[2] > 59 or payload[2] < 0:
                    payload[2] = 0
                pin = ((payload[0] << 11) | (payload[1] << 6) | payload[2]).to_bytes(2, byteorder="big")
                msg = bytes([0x06, dsn, psn]) + bytes(pin)
                self.controller.rdspin_queue.append(f"{payload[0]}. {payload[1]:02}:{payload[2]:02}")
            case "lps":
                lps_bytes = payload.encode('utf-8') + bytes([0x0D])
                lps_bytes = lps_bytes[:32]
                msg = bytes([0x21, dsn, psn, len(lps_bytes)]) + lps_bytes
            case "gseq":
                split_groups = [t.strip().upper() for t in re.split(r'[, ]+', payload) if t.strip()]
                groups_bytes = bytearray()
                for group in split_groups[:252]:
                    number = int(group[:-1])
                    offset = 0 if group[-1] == 'A' else 1
                    groups_bytes.append((number * 2) + offset)
                msg = bytes([0x16, dsn, len(groups_bytes)]) + bytes(groups_bytes)

        with self._lock:
            uecp = self.addr + bytes([self.sqc, len(msg)]) + msg
            crc = self._crc16_ccitt(uecp)
            uecp = bytes([0xFE]) + self._uecp_escape_bytes(uecp + crc) + bytes([0xFF])
            self.logger.debug(f"Sent UECP command. SQC: {self.sqc}")
            if (self.sqc == 255):
                self.sqc = 0
            else:
                self.sqc = self.sqc + 1
            self.encoder_connection.submit(uecp)