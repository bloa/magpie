from .basic_fitness import BasicFitness


class TemplatedFitness(BasicFitness):
    @classmethod
    def template(cls, template):
        args = [s.strip() for s in template[1:-1].split(',')]
        return type(f'{cls.__name__}{template}', (cls, ), {'TEMPLATE': args})
