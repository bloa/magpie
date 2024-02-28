from abc import ABC, abstractmethod
import random

class Realm(ABC):
    @classmethod
    def random_value_from_realm(cls, realm):
        if isinstance(realm, Realm):
            realm = realm.random_value()
        if isinstance(realm, list):
            return cls.random_value_from_realm(random.choice(realm))
        if isinstance(realm, tuple):
            if len(realm) == 2:
                if isinstance(realm[0], int):
                    return random.randint(*realm)
                if isinstance(realm[0], float):
                    return random.uniform(*realm)
                if callable(realm[0]):
                    x = cls.random_value_from_realm(realm[1])
                    return realm[0](x)
            raise RuntimeError(f'Invalid param realm "{repr(realm)}"')
        return realm # single value?

    @abstractmethod
    def random_value(self):
        pass

    @classmethod
    def categorical(cls, *args, **kwargs):
        return CategoricalRealm(*args, **kwargs)

    @classmethod
    def uniform(cls, *args, **kwargs):
        return UniformRealm(*args, **kwargs)

    @classmethod
    def uniform_int(cls, *args, **kwargs):
        return UniformIntRealm(*args, **kwargs)

    @classmethod
    def exponential(cls, *args, **kwargs):
        return ExponentialRealm(*args, **kwargs)

    @classmethod
    def geometric(cls, *args, **kwargs):
        return GeometricRealm(*args, **kwargs)

    @classmethod
    def lambd(cls, *args, **kwargs):
        return LambdaRealm(*args, **kwargs)

    c = categorical
    u = uniform
    ui = uniform_int
    e = exponential
    g = geometric
    l = lambd


class CategoricalRealm(Realm):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return f'CategoricalRealm({self.data})'

    def random_value(self):
        return random.choice(self.data)

class UniformRealm(Realm):
    def __init__(self, start, stop, step=None):
        self.start = start
        self.stop = stop
        self.step = step

    def __str__(self):
        if self.step is None:
            return f'UniformRealm({self.start}, {self.stop})'
        return f'UniformRealm({self.start}, {self.stop}, {self.step})'

    def random_value(self):
        if self.step is None:
            return random.uniform(self.start, self.stop)
        return round(self.start + self.step*random.randrange((self.stop-self.start)/self.step), 10)

class UniformIntRealm(Realm):
    def __init__(self, start, stop, step=None):
        self.start = start
        self.stop = stop
        self.step = step

    def __str__(self):
        if self.step is None:
            return f'UniformIntRealm({self.start}, {self.stop})'
        return f'UniformIntRealm({self.start}, {self.stop}, {self.step})'

    def random_value(self):
        if self.step is None:
            return random.randint(self.start, self.stop)
        return random.randrange(self.start, self.stop, self.step)

class ExponentialRealm(Realm):
    def __init__(self, start, stop, lambd=None):
        self.start = start
        self.stop = stop
        self.lambd = lambd

    def __str__(self):
        if self.lambd is None:
            return f'ExponentialRealm({self.start}, {self.stop})'
        return f'ExponentialRealm({self.start}, {self.stop}, {self.lambd})'

    def random_value(self):
        if self.start >= 0:
            return self.random_positive_value(self.start, self.stop, self.lambd)
        if self.stop <= 0:
            return self.random_negative_value(self.start, self.stop, self.lambd)
        if random.randrange(2) == 0:
            return self.random_positive_value(0, self.stop, self.lambd)
        return self.random_negative_value(self.start, 0, self.lambd)

    def random_positive_value(self, start, stop, lambd):
        if lambd is None:
            lambd = 10.0/(stop - start)
        for _ in range(1000):
            x = random.expovariate(lambd)
            if x <= stop - start:
                return start + x
        # give up?! and return some uniform value instead
        return random.uniform(start, stop)

    def random_negative_value(self, start, stop, lambd):
        return -self.random_positive_value(-stop, -start, None if lambd is None else -lambd)

class GeometricRealm(Realm):
    def __init__(self, start, stop, lambd=None):
        self.start = start
        self.stop = stop
        self.lambd = lambd

    def __str__(self):
        if self.lambd is None:
            return f'GeometricRealm({self.start}, {self.stop})'
        return f'GeometricRealm({self.start}, {self.stop}, {self.lambd})'

    def random_value(self):
        if self.start >= 0:
            return self.random_positive_value(self.start, self.stop, self.lambd)
        if self.stop <= 0:
            return self.random_negative_value(self.start, self.stop, self.lambd)
        if random.randrange(2) == 0:
            return self.random_positive_value(0, self.stop, self.lambd)
        return self.random_negative_value(self.start, 0, self.lambd)

    def random_positive_value(self, start, stop, lambd):
        if lambd is None:
            lambd = 10.0/(stop - start)
        for _ in range(1000):
            x = int(random.expovariate(lambd))
            if x <= stop - start:
                return start + x
        # give up?! and return some uniform value instead
        return random.uniform(start, stop)

    def random_negative_value(self, start, stop, lambd):
        return -self.random_positive_value(-stop, -start, None if lambd is None else -lambd)


class LambdaRealm(Realm):
    def __init__(self, lambd, realm):
        self.lambd = lambd
        self.realm = realm

    def __str__(self):
        return f'LambdaRealm(<unsupported>, {self.realm})'

    def random_value(self):
        x = Realm.random_value(self.realm)
        return self.lambd(x)
