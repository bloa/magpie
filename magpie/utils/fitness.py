def dominates(fit1, fit2):
    if fit1 is None:
        return False
    if fit2 is None:
        return True
    if isinstance(fit1, list):
        tmp = list(zip(fit1, fit2))
        return all(x <= y for (x, y) in tmp) and any(x < y for (x, y) in tmp)
    return fit1 < fit2

def dominates_or_equal(fit1, fit2):
    return dominates(fit1, fit2) or fit1 == fit2

def pareto(population):
    front = []
    for candidate in population:
        if any(dominates(incumbent['fitness'], candidate['fitness']) for incumbent in front):
            continue
        if any(incumbent['patch'] == candidate['patch'] for incumbent in front):
            continue
        front = [incumbent for incumbent in front if not dominates(candidate['fitness'], incumbent['fitness'])]
        front.append(candidate)
    return front
