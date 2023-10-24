import types


class ExecResult(types.SimpleNamespace):
    def __init__(self, cmd, status, return_code, stdout, stderr, runtime, output_length):
        self.cmd = cmd
        self.status = status
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        self.runtime = runtime
        self.output_length = output_length
