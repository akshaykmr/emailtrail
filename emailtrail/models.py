from dataclasses import dataclass


@dataclass
class Hop:
    from_host: str
    protocol: str
    received_by_host: str
    timestamp: int | None
    delay: int = 0  # in seconds


@dataclass
class Trail:
    to_address: str
    from_address: str
    cc: str
    bcc: str
    hops: list[Hop]

    @property
    def total_delay(self) -> int:
        """in seconds"""
        return sum(hop.delay for hop in self.hops)
