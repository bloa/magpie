import copy

import magpie


class StubSoftware(magpie.core.BasicSoftware):
    def __init__(self):
        super().__init__(copy.deepcopy(magpie.default_scenario))
        self.config['software'].update({
            'path': 'foo',
            'target_files': 'foo/bar',
            'possible_edits': 'LineDeletion',
            'fitness': 'output',
        })

class StubExecManager(magpie.core.BasicExecManager):
    def reset_timestamp(self):
        self.unix_timestamp = 0
        self.run_label = 'foo_0_0'

    def reset_workdir(self):
        pass

    def reset_contents(self):
        self.contents = {}
        self.locations = {}
