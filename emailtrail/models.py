from dataclasses import dataclass
from typing import List


@dataclass
class Hop:
    from_host: str
    protocol: str
    received_by_host: str
    timestamp: int
    delay: int = 0  # in seconds


@dataclass
class Trail:
    to_address: str
    from_address: str
    cc: str
    bcc: str
    hops: List[Hop]

    @property
    def total_delay(self) -> int:
        """in seconds"""
        return sum([hop.delay for hop in self.hops]) if self.hops else 0
