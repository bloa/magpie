import copy
import difflib
import os
import pathlib
import random

import magpie.settings
import magpie.utils


class Variant:
    def __init__(self, software, patch=None):
        self.models = {}
        if software.noop_variant:
            self.models = copy.deepcopy(software.noop_variant.models)
        else:
            if patch is not None:
                raise AssertionError
            cwd = pathlib.Path.cwd()
            try:
                os.chdir(software.path)
                for filename in software.target_files:
                    self.models[filename] = self._init_model(software, filename)
            finally:
                os.chdir(cwd)
        self.patch = patch
        if patch:
            for edit in patch.edits:
                edit.apply(software.noop_variant, self)
        self.diff = self._diff(software.noop_variant or self, magpie.settings.diff_method)

    def random_model(self, klass):
        tmp = [model for model in self.models.values() if isinstance(model, klass)]
        if tmp:
            return random.choice(tmp)
        msg = f'No compatible target file for model "{klass.__name__}"'
        raise RuntimeError(msg)

    def random_targets(self, klass, *args):
        klass = self.random_model(klass).__class__
        return [self.random_model(klass).random_target(tag) for tag in args]

    def _init_model(self, software, target_file):
        for (pattern, klass) in software.model_rules:
            if any([target_file == pattern,
                    pattern == '*',
                    pattern.startswith('*') and target_file.endswith(pattern[1:]),
            ]):
                model = magpie.utils.model_from_string(klass)(target_file)
                break
        else:
            msg = f'Unknown model for target file "{target_file}"'
            raise RuntimeError(msg)
        for (pattern, section_name) in software.model_config:
            if any([target_file == pattern,
                    pattern == '*',
                    pattern.startswith('*') and target_file.endswith(pattern[1:]),
            ]):
                model.setup(software.config, section_name)
                break
        model.init_contents()
        if model.indirect_locations:
            model.locations_names = {key: list(range(len(value))) for key, value in model.locations.items()}
        else:
            model.locations_names = model.locations
        model.cached_dump = model.dump()
        return model

    def _diff(self, other, method='unified'):
        if method == 'unified':
            diff_method = difflib.unified_diff
        elif method == 'context':
            diff_method = difflib.context_diff
        else:
            msg = f'Unknown diff method: "{method}"'
            raise ValueError(msg)
        diffs = []
        for filename in self.models:
            renamed = other.models[filename].renamed_filename
            fromfile = f'before: {renamed}'
            tofile = f'after: {renamed}'
            s1 = other.models[filename].dump().splitlines(keepends=True)
            s2 = self.models[filename].dump().splitlines(keepends=True)
            diffs += diff_method(s1, s2, fromfile=fromfile, tofile=tofile)
        return ''.join(diffs)
