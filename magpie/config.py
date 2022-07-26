import types

config = types.SimpleNamespace()

config.log_dir = '_magpie_logs'
config.work_dir = '_magpie_work'
config.local_original_copy = False
config.local_original_name = '__original__'

config.diff_method = 'unified' # unified / context

config.compile_timeout = 30
config.compile_output = None # no limit
config.test_timeout = 30
config.test_output = None # no limit
config.run_timeout = 15
config.run_output = 1e4 # 1e6 bytes is 1Mb

config.edit_retries = 10
