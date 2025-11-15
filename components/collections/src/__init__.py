"""Collections component - Map, Set, WeakMap, WeakSet."""

from .same_value_zero import same_value_zero
from .hash_table import HashTable
from .map import Map
from .set import Set
from .weak_map import WeakMap
from .weak_set import WeakSet

__all__ = ['same_value_zero', 'HashTable', 'Map', 'Set', 'WeakMap', 'WeakSet']
