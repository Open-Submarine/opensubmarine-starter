from algopy import (
    subroutine,
    Bytes,
)
from opensubmarine import ARC73SupportsInterface

# See implementation of Ownable:
# https://github.com/Open-Submarine/opensubmarine-contracts/blob/main/src/opensubmarine/contracts/access/Ownable/contract.py
# Ownable class methods and subroutines are available to HelloWorld and by be overridden in HelloWorld

class HelloWorld(ARC73SupportsInterface):
    """
    A simple example of a contract that overrides the _supportsInterface method.
    """

    # arc73 override
    @subroutine
    def _supportsInterface(self, interface_id: Bytes) -> bool:
        if interface_id == Bytes.from_hex("10101010"):  # HelloWorld interface
            return True
        else:
            return super()._supportsInterface(interface_id)
