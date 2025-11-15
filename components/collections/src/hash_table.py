"""
Hash table implementation with separate chaining.

Used internally by Map and Set.
- Separate chaining for collision resolution
- Insertion order preservation using linked list
- SameValueZero equality for keys
- Dynamic resizing for performance
"""

from .same_value_zero import same_value_zero


class HashNode:
    """
    Node in the hash table's linked list.

    Each bucket contains a linked list of nodes for collision handling.
    The nodes also form a doubly-linked list to preserve insertion order.
    """

    def __init__(self, key, value, hash_value):
        self.key = key
        self.value = value
        self.hash_value = hash_value

        # For separate chaining (collision resolution)
        self.next = None

        # For maintaining insertion order
        self.order_prev = None
        self.order_next = None


class HashTable:
    """
    Hash table with separate chaining and insertion order preservation.

    Features:
    - Separate chaining for collision resolution
    - Insertion order preservation (doubly-linked list)
    - SameValueZero equality for keys
    - Dynamic resizing when load factor exceeds threshold

    Attributes:
        size: Number of key-value pairs in the table
    """

    def __init__(self, initial_capacity=16, load_factor=0.75):
        """
        Initialize hash table.

        Args:
            initial_capacity: Initial number of buckets
            load_factor: Threshold for resizing (resize when size/capacity > load_factor)
        """
        self._capacity = initial_capacity
        self._load_factor = load_factor
        self._buckets = [None] * self._capacity
        self._size = 0

        # Maintain insertion order with doubly-linked list
        self._first = None  # First node in insertion order
        self._last = None   # Last node in insertion order

    @property
    def size(self):
        """Get number of entries in hash table."""
        return self._size

    def _hash(self, key):
        """
        Compute hash value for a key.

        Args:
            key: The key to hash

        Returns:
            int: Hash value
        """
        # Use Python's built-in hash function
        # For objects, this gives identity-based hash
        # For NaN, we need special handling
        if isinstance(key, float):
            import math
            if math.isnan(key):
                # All NaNs should hash to the same value
                return hash("__NaN__")

        try:
            return hash(key)
        except TypeError:
            # For unhashable types, use id()
            return id(key)

    def _bucket_index(self, hash_value):
        """
        Get bucket index for a hash value.

        Args:
            hash_value: The hash value

        Returns:
            int: Bucket index (0 to capacity-1)
        """
        return hash_value % self._capacity

    def _find_node(self, key, hash_value):
        """
        Find a node with the given key.

        Args:
            key: The key to find
            hash_value: Hash value of the key

        Returns:
            HashNode or None: The node if found, None otherwise
        """
        bucket_idx = self._bucket_index(hash_value)
        node = self._buckets[bucket_idx]

        while node is not None:
            if same_value_zero(node.key, key):
                return node
            node = node.next

        return None

    def set(self, key, value):
        """
        Add or update a key-value pair.

        Args:
            key: The key
            value: The value

        Returns:
            HashTable: self (for chaining)
        """
        hash_value = self._hash(key)
        existing_node = self._find_node(key, hash_value)

        if existing_node is not None:
            # Update existing entry
            existing_node.value = value
            return self

        # Add new entry
        new_node = HashNode(key, value, hash_value)

        # Add to bucket (separate chaining)
        bucket_idx = self._bucket_index(hash_value)
        new_node.next = self._buckets[bucket_idx]
        self._buckets[bucket_idx] = new_node

        # Add to insertion order list
        if self._last is None:
            # First entry
            self._first = new_node
            self._last = new_node
        else:
            # Append to end
            self._last.order_next = new_node
            new_node.order_prev = self._last
            self._last = new_node

        self._size += 1

        # Resize if load factor exceeded
        if self._size / self._capacity > self._load_factor:
            self._resize()

        return self

    def get(self, key):
        """
        Get value for a key.

        Args:
            key: The key

        Returns:
            The value if key exists, None otherwise
        """
        hash_value = self._hash(key)
        node = self._find_node(key, hash_value)
        return node.value if node is not None else None

    def has(self, key):
        """
        Check if a key exists.

        Args:
            key: The key

        Returns:
            bool: True if key exists
        """
        hash_value = self._hash(key)
        return self._find_node(key, hash_value) is not None

    def delete(self, key):
        """
        Delete a key-value pair.

        Args:
            key: The key to delete

        Returns:
            bool: True if key existed and was deleted, False otherwise
        """
        hash_value = self._hash(key)
        bucket_idx = self._bucket_index(hash_value)

        # Find and remove from bucket chain
        node = self._buckets[bucket_idx]
        prev_node = None

        while node is not None:
            if same_value_zero(node.key, key):
                # Found it - remove from bucket chain
                if prev_node is None:
                    self._buckets[bucket_idx] = node.next
                else:
                    prev_node.next = node.next

                # Remove from insertion order list
                if node.order_prev is not None:
                    node.order_prev.order_next = node.order_next
                else:
                    self._first = node.order_next

                if node.order_next is not None:
                    node.order_next.order_prev = node.order_prev
                else:
                    self._last = node.order_prev

                self._size -= 1
                return True

            prev_node = node
            node = node.next

        return False

    def clear(self):
        """Remove all entries from the hash table."""
        self._buckets = [None] * self._capacity
        self._size = 0
        self._first = None
        self._last = None

    def keys(self):
        """
        Iterate over keys in insertion order.

        Yields:
            Keys in insertion order
        """
        node = self._first
        while node is not None:
            yield node.key
            node = node.order_next

    def values(self):
        """
        Iterate over values in insertion order.

        Yields:
            Values in insertion order
        """
        node = self._first
        while node is not None:
            yield node.value
            node = node.order_next

    def entries(self):
        """
        Iterate over (key, value) pairs in insertion order.

        Yields:
            (key, value) tuples in insertion order
        """
        node = self._first
        while node is not None:
            yield (node.key, node.value)
            node = node.order_next

    def _resize(self):
        """
        Resize the hash table to maintain performance.

        Doubles the capacity and rehashes all entries.
        """
        old_capacity = self._capacity
        self._capacity = old_capacity * 2
        old_buckets = self._buckets
        self._buckets = [None] * self._capacity

        # Rehash all entries (maintains insertion order through order_* links)
        node = self._first
        while node is not None:
            # Re-add to new buckets
            bucket_idx = self._bucket_index(node.hash_value)
            node.next = self._buckets[bucket_idx]
            self._buckets[bucket_idx] = node
            node = node.order_next
