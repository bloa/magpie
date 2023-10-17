import magpie

class MyAlgo(magpie.algo.FirstImprovement):
    def mutate(self, patch):
        for _ in range(3):
            super().mutate(patch)

magpie.algo.algos += [MyAlgo]
