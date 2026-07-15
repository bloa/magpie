from .abstract_evalcache import AbstractEvalCache


class BasicEvalCache(AbstractEvalCache):
    def __init__(self):
        super().__init__()
        self.config['maxsize'] = 40
        self.config['keep'] = 0.2

    def reset(self):
        super().reset()
        self.cache = {}
        self.cache_hits = {}

    def setup(self, config):
        sec = config['search']
        self.config['maxsize'] = int(val) if (val := sec['cache_maxsize']) else 0
        self.config['keep'] = float(sec['cache_keep'])

    def get(self, diff):
        try:
            run = self.cache[diff]
        except KeyError:
            self.stats['misses'] += 1
            return None
        else:
            self.stats['hits'] += 1
            if self.config['maxsize'] > 0:
                self.cache_hits[diff] += 1
            run.cached = True
            run.updated = False
            return run

    def update(self, diff, run):
        msize = self.config['maxsize']
        if msize == 0:
            return
        if msize < len(self.cache_hits):
            keep = self.config['keep']
            hits = sorted(self.cache.keys(), key=lambda k: 999 if len(k) == 0 else self.cache_hits[k])
            for k in hits[:int(msize*(1-keep))]:
                del self.cache[k]
            self.cache_hits = dict.fromkeys(self.cache, 0)
        if diff not in self.cache:
            self.cache_hits[diff] = 0
        self.cache[diff] = run
