import pathlib

magpie_root = pathlib.Path(__file__).parent.parent

# WARNING: note that the following settings are overwritten in core/setup.py with default values from core/scenario.py

log_dir = '_magpie_logs'
work_dir = '_magpie_work'
local_original_copy = False
local_original_name = '__original__'
output_encoding = 'ascii'

edit_retries = 10
default_timeout = 30
default_lengthout = 1e4 # 1e6 bytes is 1Mb

color_output = True
log_format_info = '{counter:<7} {status:<20} {best}{fitness} ({ratio}) [{size}] {cached} {log}'
log_format_debug = 'patch({counter}) {patch}'
log_format_fitness = '{:.2f}'
log_format_ratio = '{:.2%}'

diff_method = 'unified' # unified / context

trust_local_filesystem = True
