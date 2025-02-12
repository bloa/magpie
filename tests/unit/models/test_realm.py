from magpie.models.paramconfig import Realm


def test_categorical():
    data = ['a', 'b', 'c', 'd']
    counts = {v : 0 for v in data}
    realm = Realm.categorical(data)
    for _ in range(100):
        v = realm.random_value()
        assert v in data
        counts[v] += 1
    for v in data:
        assert 10 <= counts[v] <= 40 # expected: 100/4=25

def test_uniform():
    counts1 = {v : 0 for v in range(10)} # integer part bins
    counts2 = {v : 0 for v in range(10)} # fractional part bins
    realm = Realm.uniform(0, 99)
    for _ in range(1000):
        v = realm.random_value()
        assert 0 <= v < 100
        counts1[v//10] += 1
        counts2[100*(v-int(v))//10] += 1
    for v in range(10):
        assert 50 <= counts1[v] <= 150 # expected: 100
        assert 50 <= counts2[v] <= 150 # expected: 100

def test_discrete():
    counts = {v : 0 for v in range(10)}
    realm = Realm.discrete(0, 99)
    for _ in range(1000):
        v = realm.random_value()
        assert(isinstance(v, int))
        assert 0 <= v < 100
        counts[v//10] += 1
    print(counts)
    for v in range(10):
        assert 50 <= counts[v] <= 150 # expected: 100

def test_exponential():
    counts1 = {v : 0 for v in range(10)} # integer part bins
    counts2 = {v : 0 for v in range(10)} # fractional part bins
    realm = Realm.exponential(0, 99)
    for _ in range(1000):
        v = realm.random_value()
        assert 0 <= v < 100
        counts1[v//10] += 1
        counts2[100*(v-int(v))//10] += 1
    # check bin inbalances
    tmp = [counts1[k] for k in range(10)]
    assert sum(tmp[:1]) >= sum(tmp[2:])
    assert sum(tmp[:2]) >= sum(tmp[3:])
    assert sum(tmp[:3]) >= sum(tmp[4:])
    for v in range(10):
        assert 50 <= counts2[v] <= 150 # expected: 100

def test_geometric():
    counts = {v : 0 for v in range(10)}
    realm = Realm.geometric(0, 99)
    for _ in range(1000):
        v = realm.random_value()
        assert(isinstance(v, int))
        assert 0 <= v < 100
        counts[v//10] += 1
    tmp = [counts[k] for k in range(10)]
    assert sum(tmp[:1]) >= sum(tmp[2:])
    assert sum(tmp[:2]) >= sum(tmp[3:])
    assert sum(tmp[:3]) >= sum(tmp[4:])
