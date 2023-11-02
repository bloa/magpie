import pathlib


magpie_root = pathlib.Path(__file__).parent.parent

log_dir = '_magpie_logs'
work_dir = '_magpie_work'
local_original_copy = False
local_original_name = '__original__'
output_encoding = 'ascii'

edit_retries = 10
default_timeout = 30
default_lengthout = 1e4 # 1e6 bytes is 1Mb

diff_method = 'unified' # unified / context

trust_local_filesystem = True
