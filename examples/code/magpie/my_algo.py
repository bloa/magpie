import magpie
from magpie.algos import FirstImprovement


class MyAlgo(FirstImprovement):
    def mutate(self, patch):
        for _ in range(3):
            super().mutate(patch)

magpie.algos.known_algos += [MyAlgo]
