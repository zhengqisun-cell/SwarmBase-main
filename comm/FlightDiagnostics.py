"""Observability only: logging and optional passive robot USB input."""
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import os
import struct
import time
try:
    import fcntl
    import termios
except ImportError:  # Windows: no passive robot USB reader; everything else works
    fcntl = termios = None

MODES = {0: 'Off', 1: 'Manual', 2: 'Auto', 3: 'Balloon', 4: 'Goal', 5: 'Feedback toggle'}
# Balloon color sent in control param 7; 0 leaves the camera's own setting
COLORS = {0: 'Camera default', 1: 'Purple', 2: 'Green', 3: 'Purple+Green', 4: 'Red'}


def parse_robot_line(line):
    for tag in ('CMD', 'EXEC', 'CFG'):
        marker = '[' + tag + '] '
        if marker not in line:
            continue
        try:
            result = {'tag': tag}
            for word in line.split(marker, 1)[1].split():
                key, value = word.split('=', 1)
                values = [float(x) for x in value.split(',')]
                if not all(math.isfinite(x) for x in values):
                    return None
                result[key] = values if ',' in value else values[0]
            required = {'CMD': {'params': 13}, 'EXEC': {'beh': 5, 'out': 5, 'sensors': 11}, 'CFG': {}}
            if any(not isinstance(result.get(k), list) or len(result[k]) != n
                   for k, n in required[tag].items()):
                return None
            optional = {'requested': 5, 'integral': 3, 'ledc1': 5, 'ledc2': 5, 'ledc3': 5, 'ledc4': 5,
                        'motor_us_set': 2, 'servo_us_set': 2, 'servo_deg_cmd': 2, 'pwm_updates': 2, 'pwm_late': 2}
            if any(k in result and (not isinstance(result[k], list) or len(result[k]) != n) for k, n in optional.items()):
                return None
            if tag in ('CMD', 'EXEC') and 'seq' not in result:
                return None
            return result
        except (ValueError, TypeError):
            return None
    return None


class FlightDiagnostics:
    def __init__(self, log_root, robot_port=None, robot_mac=None, passive=True):
        self.started = time.monotonic()
        self.robot_port = robot_port
        self.robot_mac = (robot_mac or '').lower()
        self.passive = passive
        self.fd = None
        self.pending = bytearray()
        self.retry_at = 0
        self.robot_status = 'Waiting for robot USB; wireless control unaffected'
        if termios is None and robot_port:
            self.robot_status = 'Robot USB log not supported on this OS; wireless control unaffected'
        self.log_error = None
        self.selected = None
        self.base_open = False
        self.base_port = ''
        self.input = None
        self.tx = self.received = self.execution = self.config = self.telemetry = None
        self.extra, self.extra_at = {}, {}  # wireless health pages 2-4
        self.rx_at = self.exec_at = self.telemetry_at = None
        self.tx_count = self.rx_count = self.exec_count = self.telemetry_count = 0
        self.base_lines = 0
        self.tx_history = deque(maxlen=300)
        self.events = deque(maxlen=5)
        self.motor_history = deque(maxlen=120)
        self.closed = False
        self.file = None
        stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        self.session_dir = Path(log_root) / stamp
        try:
            self.session_dir.mkdir(parents=True)
            self.file = (self.session_dir / 'session.jsonl').open('x', buffering=1, encoding='utf-8')
        except OSError as exc:
            self.log_error = str(exc)
        self.event('session_start', robot_port=robot_port, robot_mac=self.robot_mac,
                   note='Passive USB reader; no robot writes/reset. TX does not prove radio delivery.')

    def event(self, kind, **data):
        record = {'time': datetime.now(timezone.utc).isoformat(),
                  'elapsed_s': round(time.monotonic() - self.started, 6),
                  'event': kind, **data}
        if self.file:
            try:
                self.file.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')
            except (OSError, ValueError) as exc:
                self.log_error = str(exc)
                try:
                    self.file.close()
                except OSError:
                    pass
                self.file = None
        return record

    def note(self, text):
        self.events.append(datetime.now().strftime('%H:%M:%S') + '  ' + text)

    def select(self, mac):
        self.selected = mac.lower() if mac else None
        self.event('selection', mac=self.selected)

    def joystick(self, axes, buttons):
        self.input = {'axes': list(map(float, axes)), 'buttons': list(map(int, buttons))}
        self.event('joystick', **self.input)

    def observe(self, kind, **data):
        now = time.monotonic()
        if kind == 'base_open':
            self.base_open = True
            self.base_port = data['port']
            self.note('Base serial port opened')
        elif kind == 'base_closed':
            self.base_open = False
        elif kind == 'tx_control':
            self.tx_count += 1
            self.tx = {**data, 'id': self.tx_count, 'at': now}
            self.tx_history.append(self.tx)
        elif kind == 'telemetry_extra':
            self.extra[data['page']] = data['values']
            self.extra_at[data['page']] = now
        elif kind == 'telemetry':
            self.telemetry_count += 1
            self.telemetry = data['values']
            self.telemetry_at = now
        elif kind == 'base_response':
            self.base_lines += 1
        elif kind == 'tx_preference':
            self.note('Uploaded preference: ' + data['key'])
        elif kind == 'base_error':
            self.note('Base serial error: ' + data['error'])
        self.event(kind, **data)

    def ingest(self, line):
        now = time.monotonic()
        parsed = parse_robot_line(line)
        self.event('robot_line', raw=line, parsed=parsed)
        if not parsed:
            if any(x in line.lower() for x in ('guru meditation', 'backtrace:', 'brownout', 'assert failed', 'corrupt heap')):
                self.note('Robot error: ' + line[:100])
            return
        tag = parsed['tag']
        if tag == 'CMD':
            self.received = parsed
            self.rx_at = now
            self.rx_count += 1
            if int(parsed['params'][0]) != int((self.execution or {}).get('beh', [-1])[0]):
                self.note('Robot received: ' + MODES.get(int(parsed['params'][0]), 'Unknown mode'))
        elif tag == 'EXEC':
            if self.execution and (parsed.get('t_us', 0) < self.execution.get('t_us', 0)
                                   or parsed['seq'] < self.execution['seq']):
                self.received = None
                self.rx_at = None
                self.motor_history.clear()
                self.note('Robot clock/sequence restarted; receive matching reset')
            self.execution = parsed
            self.exec_at = now
            self.exec_count += 1
            self.motor_history.append((now - self.started, *parsed['out'][:2]))
        else:
            self.config = parsed

    def poll(self):
        if self.closed or not self.passive or not self.robot_port or termios is None:
            return
        now = time.monotonic()
        if self.fd is None:
            if now < self.retry_at:
                return
            self.retry_at = now + 3
            fd = None
            try:
                fd = os.open(self.robot_port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                attrs = termios.tcgetattr(fd)
                attrs[0] = attrs[1] = attrs[3] = 0
                attrs[2] = termios.CS8 | termios.CLOCAL | termios.CREAD
                attrs[4] = attrs[5] = termios.B115200
                attrs[6][termios.VMIN] = attrs[6][termios.VTIME] = 0
                termios.tcsetattr(fd, termios.TCSANOW, attrs)
                self.fd = fd
                self.pending.clear()
                self.received = self.execution = self.config = None
                self.rx_at = self.exec_at = None
                self.motor_history.clear()
                self.robot_status = 'Robot USB log open (read-only, no reset)'
                self.note(self.robot_status)
                self.event('robot_usb_open', port=self.robot_port)
            except (OSError, termios.error) as exc:
                if fd is not None:
                    os.close(fd)
                self.robot_status = 'Robot USB not connected or busy'
                self.event('robot_usb_unavailable', error=str(exc))
                return
        try:
            for _ in range(4):
                try:
                    chunk = os.read(self.fd, 16384)
                except BlockingIOError:
                    break
                if not chunk:
                    break
                self.pending.extend(chunk)
                while b'\n' in self.pending:
                    line, _, tail = self.pending.partition(b'\n')
                    self.pending = bytearray(tail)
                    self.ingest(line.decode('utf-8', errors='replace').rstrip('\r'))
                if len(self.pending) > 65536:
                    self.pending.clear()
                    self.note('Dropped an overlong partial serial line')
        except OSError as exc:
            os.close(self.fd)
            self.fd = None
            self.robot_status = 'Robot USB disconnected; last outputs are stale'
            self.event('robot_usb_error', error=str(exc))
            self.note(self.robot_status)

    def same_robot(self):
        return bool(self.selected and self.selected == self.robot_mac)

    def command_match(self):
        if not self.same_robot():
            return 'The robot on this log port is not selected'
        if not self.received:
            return 'No receive record from the robot yet'
        if time.monotonic() - self.rx_at > 3:
            return 'Receive record is stale'
        wire = struct.pack('<13f', *self.received['params'])
        matches = [x for x in self.tx_history if x['mac'].lower() == self.robot_mac
                   and struct.pack('<13f', *x['params']) == wire and x['at'] <= self.rx_at]
        if matches:
            return 'Content matches TX#%d (duplicate packets are not a unique ack)' % matches[-1]['id']
        return 'No match with sent packets; check the raw log'

    def close(self):
        if self.closed:
            return
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        self.event('session_end')
        if self.file:
            try:
                self.file.close()
            except OSError as exc:
                self.log_error = str(exc)
            self.file = None
        self.closed = True
