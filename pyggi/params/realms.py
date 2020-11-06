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
            if isinstance(realm[0], int):
                return random.randint(*realm)
            if isinstance(realm[0], float):
                return random.uniform(*realm)
            if callable(realm[0]):
                x = cls.random_value_from_realm(realm[1])
                return realm[0](x)
            raise Exception('invalid param realm')
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

    def random_value(self):
        return random.choice(self.data)

class UniformRealm(Realm):
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def random_value(self):
        return random.uniform(self.start, self.stop)

class UniformIntRealm(Realm):
    def __init__(self, start, stop, step=None):
        self.start = start
        self.stop = stop
        self.step = step

    def random_value(self):
        if step:
            return random.randint(self.start, self.stop)
        else:
            return random.randrange(self.start, self.stop, self.step)

class ExponentialRealm(Realm):
    def __init__(self, start, stop, lambd=1.0):
        self.start = start
        self.stop = stop
        self.lambd = lambd

    def random_value(self):
        while True:
            x = random.expovariate(self.lambd)
            if self.lambd > 0:
                if x <= self.stop - self.start:
                    return self.start + x
            else:
                if x >= self.start - self.stop:
                    return self.stop + x

class GeometricRealm(Realm):
    def __init__(self, start, stop, lambd=1.0):
        self.start = start
        self.stop = stop
        self.lambd = lambd

    def random_value(self):
        while True:
            x = int(random.expovariate(self.lambd))
            if self.lambd > 0:
                if x <= self.stop - self.start:
                    return self.start + x
            else:
                if x >= self.start - self.stop:
                    return self.stop + x

class LambdaRealm(Realm):
    def __init__(self, lambd, realm):
        self.lambd = lambd
        self.realm = realm

    def random_value(self):
        x = Realm.random_value(self.realm)
        return self.lambd(x)
