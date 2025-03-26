from algopy import (
    Global,
    Account,
    BigUInt,
    Bytes,
    Txn,
    arc4,
    subroutine,
)
from opensubmarine import ARC72Token, arc72_nft_data, arc72_Transfer
from opensubmarine.utils.algorand import require_payment
from opensubmarine.utils.types import Bytes256

mint_fee = 0
mint_cost = 336700


class HelloWorld(ARC72Token):
    """
    A simple Hello World smart contract that inherits from Ownable.
    """

    def __init__(self) -> None:
        super().__init__()  # call ARC72Token constructor

    @arc4.abimethod
    def mint(
        self,
        to: arc4.Address,
        tokenId: arc4.UInt256,
        metadata: Bytes256,
    ) -> arc4.UInt256:
        """
        Mint a new NFT
        """
        return arc4.UInt256(self._mint(to.native, tokenId.native, metadata.bytes))

    @subroutine
    def _mint(self, to: Account, tokenId: BigUInt, metadata: Bytes) -> BigUInt:
        # TODO require auth to mint
        nft_data = self._nft_data(tokenId)
        assert nft_data.index == 0, "token must not exist"
        payment_amount = require_payment(Txn.sender)
        assert payment_amount >= mint_cost + mint_fee, "payment amount accurate"
        # TODO transfer mint_fee to treasury
        index = arc4.UInt256(
            self._increment_counter()
        ).native  # BigUInt to BigUInt(UInt256)
        self._increment_totalSupply()
        self.nft_index[index] = tokenId
        self.nft_data[tokenId] = arc72_nft_data(
            owner=arc4.Address(to),
            approved=arc4.Address(Global.zero_address),
            index=arc4.UInt256(index),
            token_id=arc4.UInt256(tokenId),
            metadata=Bytes256.from_bytes(metadata),
        )
        self._holder_increment_balance(to)
        arc4.emit(
            arc72_Transfer(
                arc4.Address(Global.zero_address),
                arc4.Address(to),
                arc4.UInt256(tokenId),
            )
        )
        return index
