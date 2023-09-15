import types

config = types.SimpleNamespace()

config.log_dir = '_magpie_logs'
config.work_dir = '_magpie_work'
config.local_original_copy = False
config.local_original_name = '__original__'
config.output_encoding = 'ascii'

config.edit_retries = 10
config.default_timeout = 30
config.default_lengthout = 1e4 # 1e6 bytes is 1Mb

config.diff_method = 'unified' # unified / context

config.trust_local_filesystem = True
