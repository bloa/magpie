import argparse
import configparser
import os
import pathlib

import magpie


# ================================================================================
# Experimental protocol
# ================================================================================

class ExpProtocol:
    def __init__(self):
        self.search = None
        self.program = None

    def run(self):
        if self.program is None:
            raise AssertionError('Program not specified')
        if self.search is None:
            raise AssertionError('Search not specified')

        self.search.config['warmup'] = 3
        self.search.program = self.program

        logger = self.program.logger
        result = {'stop': None, 'best_patch': []}
        self.search.run()
        result.update(self.search.report)
        result['diff'] = self.program.diff_patch(result['best_patch'])
        logger.info('')

        logger.info('==== REPORT ====')
        logger.info('Termination: {}'.format(result['stop']))
        if result['best_patch']:
            logger.info('Best fitness: {}'.format(result['best_fitness']))
            logger.info('Best patch: {}'.format(result['best_patch']))
            base_path = os.path.join(magpie.config.log_dir, self.program.run_label)
            with open('{}.patch'.format(base_path), 'w') as f:
                f.write(str(result['best_patch'])+"\n")
            logger.info('Diff:\n{}'.format(result['diff']))
            with open('{}.diff'.format(base_path), 'w') as f:
                f.write(result['diff'])
        self.program.clean_work_dir()


# ================================================================================
# Target software specifics
# ================================================================================

# class MyProgram(magpie.base.Program):
#     def __init__(self, config):
#         self.base_init(config['program']['path'])
#         self.possible_edits = [
#             magpie.line.LineReplacement,
#             magpie.line.LineInsertion,
#             magpie.line.LineDeletion,
#         ]
#         self.target_files = config['program']['target_files'].split()
#         self.compile_cmd = config['exec']['compile']
#         self.test_cmd = config['exec']['test']
#         self.run_cmd = config['exec']['run']
#         self.reset_timestamp()
#         self.reset_logger()
#         self.reset_contents()

#     def get_engine(self, target_file):
#         return magpie.line.LineEngine

#     def process_run_exec(self, run_result, exec_result):
#         run_result.fitness = round(exec_result.runtime, 4)


# ================================================================================

def apply_global_config(config):
    if 'magpie' not in config:
        return
    if 'compile_timeout' in config['magpie']:
        magpie.config.compile_timeout = float(config['magpie']['compile_timeout'])
    if 'compile_output' in config['magpie']:
        if config['magpie']['compile_output'] == '':
            magpie.config.compile_output = None
        else:
            magpie.config.compile_output = float(config['magpie']['compile_output'])
    if 'test_timeout' in config['magpie']:
        magpie.config.test_timeout = float(config['magpie']['test_timeout'])
    if 'test_output' in config['magpie']:
        if config['magpie']['test_output'] == '':
            magpie.config.test_output = None
        else:
            magpie.config.test_output = float(config['magpie']['test_output'])
    if 'run_timeout' in config['magpie']:
        magpie.config.run_timeout = float(config['magpie']['run_timeout'])
    if 'run_output' in config['magpie']:
        if config['magpie']['run_output'] == '':
            magpie.config.run_output = None
        else:
            magpie.config.run_output = float(config['magpie']['run_output'])


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE Runtime Example')
    parser.add_argument('--config', type=pathlib.Path, required=True)
    args = parser.parse_args()

    # read config file
    config = configparser.ConfigParser()
    config.read(args.config)
    apply_global_config(config)

    # setup protocol
    protocol = ExpProtocol()
    protocol.search = magpie.algo.FirstImprovement()
    if 'max_iter' in config['search']:
        protocol.search.stop['steps'] = int(config['search']['max_iter'])
    if 'max_time' in config['search']:
        protocol.search.stop['wall'] = int(config['search']['max_time'])
    protocol.program = MyProgram(config)

    # run experiments
    protocol.run()
