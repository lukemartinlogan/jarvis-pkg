import subprocess
import os
import shlex


class Exec:
    def __init__(self, cmd, sudo=False,
                 collect_output=True, cwd=None):
        self.cmd = cmd
        self.sudo = sudo
        if self.sudo:
            self.cmd = f"sudo {self.cmd}"
        self.collect_output = True
        if cwd is None:
            self.cwd = os.getcwd()
        else:
            self.cwd = cwd
        self.stdout = None
        self.stderr = None
        self._start_bash_processes()

    def _start_bash_processes(self):
        commands = self.cmd
        if not self.collect_output:
            self.proc = subprocess.Popen(commands, cwd=self.cwd, shell=True)
        else:
            self.proc = subprocess.Popen(commands,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         cwd=self.cwd,
                                         shell=True)
        self.stdout, self.stderr = self.proc.communicate()
        self.stdout = self.stdout.decode("utf-8")
        self.stderr = self.stderr.decode("utf-8")
        self.exit_code = self.proc.returncode
