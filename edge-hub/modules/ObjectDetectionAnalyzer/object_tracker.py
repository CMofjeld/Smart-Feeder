from dataclasses import dataclass
from typing import Any
import datetime

@dataclass
class TrackingInfo:
    """Necessary information associated with a tracking ID."""
    arrival_time: Any
    message_sent: bool

class ObjectTracker:
    def __init__(self, capacity: int = 10) -> None:
        """Set the ObjectTracker's capacity to the argument and initialize its cache to be empty."""
        self.capacity = capacity
        self.cache = {}
    
    def contains(self, id: int) -> bool:
        """Return true if id is already being tracked."""
        return id in self.cache
    
    def get_tracking_info(self, id: int) -> TrackingInfo:
        """Return the tracking info associated with id. Return None if id is not being tracked."""
        if id in self.cache:
            return self.cache[id]
        else:
            return None

    def start_tracking(self, id: int) -> bool:
        """Start tracking the given object ID.

        If the ID is not already being tracked, a new entry is created for it in the cache.
        The new entry's arrival time is set to the current time and its flag for a message
        being sent is set to false.

        If the cache's size is greater than the tracker's capacity after adding the new entry,
        the entry with the earliest arrival time is removed from the cache.

        If the ID is already being tracked, the cache is unchanged and the return value is False.

        Args:
            id (int): tracking ID of the object

        Returns:
            bool: False if the ID is already being tracked
        """
        # Check if id is already being tracked
        if id in self.cache:
            return False

        # Create new entry
        tracking_info = TrackingInfo(
            arrival_time=datetime.datetime.now(),
            message_sent=False
        )
        self.cache[id] = tracking_info

        # Remove oldest entry, if necessary
        if len(self.cache) > self.capacity:
            self.remove_oldest_object()

        # Signal success
        return True

    def remove_oldest_object(self) -> None:
        """Remove the entry with the earliest arrival time from the cache."""
        # Check for empty cache
        if len(self.cache) <= 0:
            return

        # Find the oldest entry
        items = iter(self.cache.items())
        oldest_id, oldest_info = next(items)
        for id, tracking_info in items:
            if tracking_info.arrival_time < oldest_info.arrival_time:
                oldest_id = id
                oldest_info = tracking_info

        # Remove oldest entry from the cache
        self.cache.pop(oldest_id)
