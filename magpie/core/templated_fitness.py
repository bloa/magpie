from .basic_fitness import BasicFitness


class TemplatedFitness(BasicFitness):
    TEMPLATE = None
    @classmethod
    def template(cls, *args):
        cls.TEMPLATE = [s.strip() for s in args]
