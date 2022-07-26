import types

class ExecResult(types.SimpleNamespace):
    def __init__(self, status, return_code, stdout, stderr, runtime):
        self.status = status
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        self.runtime = runtime
