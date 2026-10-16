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

def update_archive(archive, candidate):
    if any(sol['patch'] == candidate['patch'] for sol in archive):
        return False # already in
    if any(dominates(sol['fitness'], candidate['fitness']) for sol in archive):
        return False # dominated
    archive[:] = [sol for sol in archive if not dominates(candidate['fitness'], sol['fitness'])]
    archive.append(candidate)
    return True

def update_global_archive(archive, candidate):
    if same_diff := [sol for sol in archive if sol['diff'] == candidate['diff']]:
        if min(same_diff + [candidate], key=lambda sol: len(sol['patch'].edits)) is candidate:
            archive[:] = [sol for sol in archive if sol not in same_diff]
            archive.append(candidate)
            return True
        return False
    if same_fit := [sol for sol in archive if sol['fitness'] == candidate['fitness']]:
        if min(same_fit + [candidate], key=lambda sol: len(sol['patch'].edits)) is candidate:
            archive[:] = [sol for sol in archive if sol not in same_fit]
            archive.append(candidate)
            return True
        return False
    return update_archive(archive, candidate)

def update_global_best(best, candidate):
    # same patch?
    if candidate['patch'] == best['patch']:
        best.update(candidate)
        return True
    # simply better
    if dominates(candidate['fitness'], best['fitness']):
        best.update(candidate)
        return True
    # same phenotype, but simpler genotype
    if candidate['diff'] == best['diff']:
        if len(candidate['patch'].edits) < len(best['patch'].edits):
            best.update(candidate)
            return True
        return False
    # same fitness, but simpler genotype / phenotype
    if candidate['fitness'] == best['fitness']:
        if len(candidate['patch'].edits) < len(best['patch'].edits):
            best.update(candidate)
            return True
        if len(candidate['patch'].edits) == len(best['patch'].edits) and len(candidate['diff']) < len(best['diff']):
            best.update(candidate)
            return True
        return False
    return False
