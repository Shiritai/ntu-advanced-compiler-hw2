import itertools
from typing import Collection

def flatten(ll: Collection) -> list:
    """Flatten an iterable of iterable to a single list.
    """
    return list(itertools.chain(*ll))


def new_name(seed: str, names: Collection[str]):
    """Generate a new name that is not in `names` starting with `seed`.
    """
    i = 1
    while True:
        name = f"{seed}{i}"
        if name not in names:
            return name
        i += 1


