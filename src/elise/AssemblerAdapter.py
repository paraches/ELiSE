import os
import shutil
import subprocess


class AssemblyResult:
    def __init__(self, command, output_file, list_file, stdout, stderr, returncode):
        self.command = command
        self.output_file = output_file
        self.list_file = list_file
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    @property
    def success(self):
        return self.returncode == 0


class AssemblerAdapter:
    def assemble(self, asm_file, output_dir=None, output_name=None):
        raise NotImplementedError


class ZasmAssembler(AssemblerAdapter):
    """Assemble an ELiSE-generated Z80 source file with zasm."""

    def __init__(self, executable='zasm'):
        self.executable = executable

    def assemble(self, asm_file, output_dir=None, output_name=None):
        asm_file = os.path.abspath(asm_file)
        if not os.path.isfile(asm_file):
            raise FileNotFoundError('Assembly source not found: %s' % asm_file)

        executable = shutil.which(self.executable)
        if executable is None:
            raise FileNotFoundError(
                'Assembler executable not found: %s' % self.executable
            )

        if output_dir is None:
            output_dir = os.path.dirname(asm_file)
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        if output_name is None:
            output_name = os.path.splitext(os.path.basename(asm_file))[0] + '.rom'
        output_file = os.path.join(output_dir, output_name)
        list_file = os.path.splitext(output_file)[0] + '.lst'

        command = [executable, '-uwy', '-v1', asm_file, output_file]
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
        return AssemblyResult(
            command=command,
            output_file=output_file,
            list_file=list_file,
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
        )
