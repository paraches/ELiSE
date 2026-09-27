import os
import shutil
import subprocess


class EmulatorResult:
    def __init__(self, command, log_file, process):
        self.command = command
        self.log_file = log_file
        self.process = process

    @property
    def pid(self):
        return self.process.pid


class EmulatorAdapter:
    def run(self, media_file, output_dir=None, script_file=None):
        raise NotImplementedError


class OpenMSXEmulator(EmulatorAdapter):
    """Launch an MSX ROM in openMSX."""

    def __init__(self, executable='openmsx', machine=None):
        self.executable = executable
        self.machine = machine

    def run(self, media_file, output_dir=None, script_file=None):
        media_file = os.path.abspath(media_file)
        if not os.path.isfile(media_file):
            raise FileNotFoundError('MSX media file not found: %s' % media_file)

        executable = shutil.which(self.executable)
        if executable is None:
            raise FileNotFoundError(
                'openMSX executable not found: %s. '
                'Install openMSX or pass --openmsx with its path.'
                % self.executable
            )

        if output_dir is None:
            output_dir = os.path.dirname(media_file)
        output_dir = os.path.abspath(output_dir)
        log_dir = os.path.join(output_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'emulator.log')

        command = [executable]
        if self.machine:
            command.extend(['-machine', self.machine])
        if script_file:
            command.extend(['-script', os.path.abspath(script_file)])
        command.extend(['-cart', media_file])

        log_stream = open(log_file, 'w')
        try:
            process = subprocess.Popen(
                command,
                stdout=log_stream,
                stderr=subprocess.STDOUT,
            )
        except Exception:
            log_stream.close()
            raise

        # The child process owns the duplicated descriptor after Popen.
        log_stream.close()
        return EmulatorResult(command, log_file, process)
