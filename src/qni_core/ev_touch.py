import logging
import platform

# EvTouch: IPC for passing list of multitouch points.
# Notes:
#  The evdev based class seems to support 40 points max!
#  The UDP broadcast + numpy_array class works great and cross platform!

if platform.system() == 'NO_EVDEV_Linux':
    from evdev import UInput, InputDevice, ecodes, list_devices

    class EvTouch(object):
        _logger = logging.getLogger('ev_touch')
        _DEV_NAME = 'Qni Multitouch'

        def __init__(self, is_tx=False):
            mt_capabilities = {
                ecodes.EV_ABS: [
                    (ecodes.ABS_MT_POSITION_X, (0, 0)),
                    (ecodes.ABS_MT_POSITION_Y, (0, 0)),
                ]
            }

            if is_tx:
                self._mt_dev = UInput(mt_capabilities, self._DEV_NAME)
                self.update = self._send
                self._logger.info('Created %s device!', self._DEV_NAME)
            else:
                self._mt_dev = None
                self._mt_x = None
                self._mt_y = None
                self._mt_points = []
                self._reopen_mt_dev()
                self.update = self._recv

        def _reopen_mt_dev(self):
            if self._mt_dev is not None:
                self._mt_x = self._mt_y = None
                self._mt_points.clear()
                self._logger.warning('Reconnecting %s device..', self._DEV_NAME)
            for i in list_devices():
                self._mt_dev = InputDevice(i)
                if self._mt_dev.name == self._DEV_NAME:
                    self._logger.info('Connected to %s device!', self._DEV_NAME)
                    return True
                self._mt_dev.close()
            self._mt_dev = None
            return False

        def _send(self, mt_points):
            for i in mt_points:
                self._mt_dev.write(ecodes.EV_ABS, ecodes.ABS_MT_POSITION_X, i[0])
                self._mt_dev.write(ecodes.EV_ABS, ecodes.ABS_MT_POSITION_Y, i[1])
                self._mt_dev.write(ecodes.EV_SYN, ecodes.SYN_MT_REPORT, 0)
            if not mt_points:
                self._mt_dev.write(ecodes.EV_SYN, ecodes.SYN_MT_REPORT, 0)
            self._mt_dev.syn()

        def _recv(self):
            mt_points = None
            try:
                events = list(self._mt_dev.read())
            except BlockingIOError:
                pass
            except (OSError, AttributeError):
                self._reopen_mt_dev()
            else:
                for event in events:
                    if event.type == ecodes.EV_ABS:
                        if event.code == ecodes.ABS_MT_POSITION_X:
                            self._mt_x = event.value
                        elif event.code == ecodes.ABS_MT_POSITION_Y:
                            self._mt_y = event.value
                    elif event.type == ecodes.EV_SYN:
                        if event.code == ecodes.SYN_MT_REPORT:
                            if (self._mt_x or self._mt_y) is not None: 
                                self._mt_points.append((self._mt_x, self._mt_y))
                        elif event.code == ecodes.SYN_REPORT:
                            mt_points = self._mt_points.copy()
                            self._mt_x = self._mt_y = None
                            self._mt_points.clear()
            return mt_points

        def __exit__(self):
            self._mt_dev.close()

else:
    import numpy
    import socket

    class EvTouch(object):
        _logger = logging.getLogger('ev_touch')
        _SOCKET_HOST = ''
        _SOCKET_PORT = 16565
        _ARRAY_FMT = numpy.uint8 # point axis values 0-255

        def __init__(self, is_tx=False):
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            if is_tx:
                self.update = self._send
                self._logger.info('Started server, port: %s', self._SOCKET_PORT)
            else:
                self._socket.settimeout(0.01)
                self._socket.bind((self._SOCKET_HOST, self._SOCKET_PORT))
                self.update = self._recv
                self._logger.info('Started client, port: %s', self._SOCKET_PORT)

        def _send(self, mt_points):
            # TODO: wrap data with packet?
            data = numpy.array(mt_points, self._ARRAY_FMT).tobytes()
            self._socket.sendto(data, ('<broadcast>', self._SOCKET_PORT))

        def _recv(self):
            try:
                data, _ = self._socket.recvfrom(1024)
            except socket.timeout:
                return
            l = list(numpy.frombuffer(data, self._ARRAY_FMT))
            return list(zip(l[::2], l[1::2]))

        def __exit__(self):
            self._socket.close()
