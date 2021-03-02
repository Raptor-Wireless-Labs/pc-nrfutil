
from nordicsemi.dfu.dfu_transport   import DfuTransport, DfuEvent, TRANSPORT_LOGGING_LEVEL
from nordicsemi.dfu.dfu_transport_serial import DfuTransportSerial, Slip

from pc_ble_driver_py.exceptions    import NordicSemiException
import logging
import struct
import binascii

code_page_size = 4096

logger = logging.getLogger(__name__)

class FileDFUAdapter:

    def __init__(self, opened_file):
        self.opened_File = opened_file

    def send_message(self, data):
        packet = Slip.encode(data)
        self.opened_File.write(bytearray(packet))
        self.last_op = data[0]

    def get_message(self):
        result = [DfuTransportSerial.OP_CODE['Response'], self.last_op , DfuTransport.RES_CODE['Success']]
        #pad = bytearray(4)
        if self.last_op == DfuTransportSerial.OP_CODE['ReadObject']:
            result.extend((code_page_size).to_bytes(4, 'little')) #size
            result.extend((0).to_bytes(4, 'little')) #offset
            result.extend((0).to_bytes(4, 'little')) #crc
        elif self.last_op == DfuTransportSerial.OP_CODE['CalcChecSum']:
            result.extend((0).to_bytes(4, 'little')) #offset
            result.extend((0).to_bytes(4, 'little')) #crc
        return result


class DfuTransportFile(DfuTransportSerial):
    def __init__(self, output_file):
        super().__init__(0)
        self.output_file = output_file
        self.mtu = 131
        self.already_opened = False

    def open(self):
        try:
            file_mode = 'wb'
            if self.already_opened:
                file_mode = 'ab'

            self.out_f = open(self.output_file, mode=file_mode)
            self.dfu_adapter = FileDFUAdapter(self.out_f)
            self.already_opened = True


        except OSError as e:
            raise NordicSemiException("Output file could not be opened "
              ". Reason: {1}".format(self.com_port, e.strerror))

    def close(self):
        try:

            self.out_f.close()
        except OSError as e:
            raise NordicSemiException("Output file could not be opened "
                                      ". Reason: {1}".format(self.com_port, e.strerror))

    def __calculate_checksum(self):
        return {'offset': 0, 'crc': 0}

    #this mimics the behavior of the base class, except to get rid of the crc checks, since we're just saving to a file.
    def _DfuTransportSerial__stream_data(self, data, crc=0, offset=0):
        logger.debug("Serial: Streaming Data: " +
            "len:{0} offset:{1} crc:0x{2:08X}".format(len(data), offset, crc))
        current_pnr     = 0

        for i in range(0, len(data), (self.mtu-1)//2 - 1):
            # append the write data opcode to the front
            # here the maximum data size is self.mtu/2,
            # due to the slip encoding which at maximum doubles the size
            to_transmit = data[i:i + (self.mtu-1)//2 - 1 ]
            to_transmit = struct.pack('B',DfuTransportSerial.OP_CODE['WriteObject']) + to_transmit

            self.dfu_adapter.send_message(list(to_transmit))
            crc     = binascii.crc32(to_transmit[1:], crc) & 0xFFFFFFFF
            offset += len(to_transmit) - 1
            current_pnr    += 1
            if self.prn == current_pnr:
                current_pnr = 0
                response    = self.__get_checksum_response()
                #validate_crc()
        response = self.__calculate_checksum()
        #validate_crc()
        return crc