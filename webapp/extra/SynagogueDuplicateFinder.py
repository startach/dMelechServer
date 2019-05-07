import mpu


def dist(loc1, loc2):
    lat1 = loc1["coordinates"][0]
    lon1 = loc1["coordinates"][1]

    lat2 = loc2["coordinates"][0]
    lon2 = loc2["coordinates"][1]

    return mpu.haversine_distance((lat1, lon1), (lat2, lon2)) * 1000


def is_different(syn1, syn2):
    if syn1["name"] != syn2["name"]:
        return True
    if dist(syn1["location"], syn2["location"]) > 10:
        return True

    return False


def is_uniq(syn, uniq):
    return all([is_different(syn, syn2) for syn2 in uniq])


def find_duplicates(synagogues):
    dup = []
    uniq = []
    [uniq.append(syn) if is_uniq(syn, uniq) else dup.append(syn) for syn in synagogues]

    return [uniq, dup]
