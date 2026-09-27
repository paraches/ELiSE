import os
import shutil
import subprocess
import time
import json
import xml.etree.ElementTree as ElementTree
from xml.sax.saxutils import escape


class OpenMSXControlError(RuntimeError):
    pass


class ControlReply:
    def __init__(self, result, text):
        self.result = result
        self.text = text

    @property
    def success(self):
        return self.result == 'ok'


class PipeConnection:
    def __init__(self, process):
        self.process = process

    def sendall(self, data):
        self.process.stdin.write(data)
        self.process.stdin.flush()

    def recv(self, _size):
        return self.process.stdout.read(1)

    def close(self):
        if self.process.stdin:
            self.process.stdin.close()


class OpenMSXControlSession:
    def __init__(self, process, connection, log_file):
        self.process = process
        self.connection = connection
        self.log_file = log_file
        self.buffer = ''

    @classmethod
    def launch(
        cls,
        media_file,
        executable='openmsx',
        machine=None,
        script_file=None,
        output_dir=None,
        timeout=10,
    ):
        media_file = os.path.abspath(media_file)
        if not os.path.isfile(media_file):
            raise FileNotFoundError('MSX media file not found: %s' % media_file)

        executable_path = shutil.which(executable)
        if executable_path is None:
            raise FileNotFoundError('openMSX executable not found: %s' % executable)

        if output_dir is None:
            output_dir = os.path.dirname(media_file)
        log_dir = os.path.join(os.path.abspath(output_dir), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'control.log')

        command = [executable_path]
        if machine:
            command.extend(['-machine', machine])
        if script_file:
            command.extend(['-script', os.path.abspath(script_file)])
        command.extend(['-cart', media_file])

        log_stream = open(log_file, 'w')
        try:
            process = subprocess.Popen(
                command + ['-control', 'stdio'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=log_stream,
                bufsize=0,
            )
        except Exception:
            log_stream.close()
            raise
        log_stream.close()

        session = cls(process, PipeConnection(process), log_file)
        session._read_until('<openmsx-output>')
        session._send_raw('<openmsx-control>')
        return session

    def command(self, command):
        self._send_raw('<command>%s</command>' % escape(command))
        reply_xml = self._read_until('</reply>', include=True)
        start = reply_xml.find('<reply')
        if start < 0:
            raise OpenMSXControlError('Invalid openMSX reply: %s' % reply_xml)
        reply = ElementTree.fromstring(reply_xml[start:])
        return ControlReply(reply.attrib.get('result'), reply.text or '')

    def debug_list(self):
        return self.command('debug list')

    def debug_breaked(self):
        return self.command('debug breaked')

    def debug_break(self):
        return self.command('debug break')

    def debug_continue(self):
        return self.command('debug cont')

    def debug_step(self):
        return self.command('debug step')

    def debug_read(self, name, address):
        if ' ' in name and not name.startswith('{'):
            name = '{%s}' % name
        return self.command('debug read %s 0x%04X' % (name, address))

    def debug_read_memory(self, address, size):
        return [
            int(self.debug_read('memory', (address + offset) & 0xFFFF).text.strip())
            for offset in range(size)
        ]

    def debug_read_word(self, address):
        values = self.debug_read_memory(address, 2)
        return values[0] | (values[1] << 8)

    def debug_registers(self):
        names = [
            'A', 'F', 'B', 'C', 'D', 'E', 'H', 'L',
            "A'", "F'", "B'", "C'", "D'", "E'", "H'", "L'",
            'IXH', 'IXL', 'IYH', 'IYL',
            'PCH', 'PCL', 'SPH', 'SPL', 'I', 'R', 'IM', 'IFF1/2',
        ]
        values = {}
        for address, name in enumerate(names):
            reply = self.debug_read('CPU regs', address)
            if not reply.success:
                raise OpenMSXControlError(reply.text)
            values[name] = int(reply.text.strip())
        return values

    def runtime_snapshot(self, symbols_file=None, stack_bytes=32, heap_bytes=32):
        registers = self.debug_registers()
        stack_address = (registers['SPH'] << 8) | registers['SPL']
        snapshot = {
            'registers': registers,
            'stack': {
                'address': '0x%04X' % stack_address,
                'bytes': self.debug_read_memory(stack_address, stack_bytes),
            },
        }
        if symbols_file:
            with open(symbols_file) as file:
                labels = json.load(file).get('labels', {})
            heap_address = self._label_address(labels, 'heap')
            if heap_address is not None:
                snapshot['heap'] = {
                    'address': '0x%04X' % heap_address,
                    'bytes': self.debug_read_memory(heap_address, heap_bytes),
                    'free_list': '0x%04X' % self.debug_read_word(heap_address),
                    'block_size': self.debug_read_word(heap_address + 2),
                }
        return snapshot

    @staticmethod
    def _label_address(labels, label):
        address = labels.get(label, {}).get('address')
        return int(address, 16) if address else None

    def close(self):
        try:
            if self.process.poll() is None:
                self.command('exit')
        except (OSError, OpenMSXControlError):
            pass
        finally:
            self.connection.close()
            if self.process.poll() is None:
                self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

    def _send_raw(self, message):
        self.connection.sendall((message + '\n').encode('utf-8'))

    def _read_until(self, marker, include=False):
        deadline = time.time() + 10
        while marker not in self.buffer:
            if time.time() > deadline:
                raise OpenMSXControlError(
                    'Timed out waiting for openMSX response: %s' % marker
                )
            chunk = self.connection.recv(4096)
            if not chunk:
                raise OpenMSXControlError('openMSX control connection closed')
            self.buffer += chunk.decode('utf-8', errors='replace')

        end = self.buffer.find(marker) + len(marker)
        result = self.buffer[:end]
        self.buffer = self.buffer[end:]
        if not include:
            result = result[:-len(marker)]
        return result
