import abc
import itertools
from typing import Collection

def flatten(ll: Collection) -> list:
    """Flatten an iterable of iterable to a single list.
    """
    return list(itertools.chain(*ll))


def new_name(prefix: str, names: Collection[str], count_from = 1):
    """Generate a new name that is not in `names` starting with `prefix`.
    Includes NO modification to `names`
    """
    while True:
        name = f"{prefix}{count_from}"
        if name not in names:
            return name
        count_from += 1

class Convertor(metaclass = abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def convert(self, from_: object) -> object:
        """Abstract method to convert an object
        from `from_` to the return object
        """
        return NotImplemented
    