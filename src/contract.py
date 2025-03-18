from algopy import (
    Global,
    arc4,
    subroutine,
    UInt64,
    BigUInt,
    Txn,
    Application,
    BoxMap,
    Account,
    String,
)
from opensubmarine import ARC200TokenInterface, Ownable, Upgradeable

# TODO require payment if box is not found
# from opensubmarine.utils.algorand import require_payment


class DonationData(arc4.Struct):
    amount: arc4.UInt256


class DropData(arc4.Struct):
    drip_amount: arc4.UInt256
    drip_count: arc4.UInt256
    drip_last: arc4.UInt64


class HelloWorld(Ownable, Upgradeable):  
    """
    ARC200 Token Faucet
    """

    def __init__(self) -> None:
        # ownable state
        self.owner = Global.creator_address
        # upgradeable state
        self.contract_version = UInt64()
        self.deployment_version = UInt64()
        self.updatable = bool(1)
        self.upgrader = Global.creator_address
        # this state
        self.name = String.from_bytes(b"ARC200 Token Faucet")
        self.drip_amount = BigUInt(1)
        self.drip_interval = UInt64(28800)  # ~ 1 day in blocks
        self.donations = BoxMap(Account, DonationData)
        self.drips = BoxMap(Account, DropData)

    @arc4.abimethod
    def donation_data(self, who: arc4.Address) -> DonationData:
        """
        Returns the donation amount for the given account.
        """
        return self._donation_data(who.native)

    @subroutine
    def _donation_data(self, sender: Account) -> DonationData:
        """
        Records a donation for the sender.
        """
        return self.donations.get(
            key=sender,
            default=DonationData(amount=arc4.UInt256(0)),
        )

    @arc4.abimethod
    def drip_data(self, who: arc4.Address) -> DropData:
        """
        Drips a token to the caller.
        """
        return self._drip_data(who.native)

    @subroutine
    def _drip_data(self, sender: Account) -> DropData:
        """
        Returns the drop data for the sender.
        """
        return self.drips.get(
            key=sender,
            default=DropData(
                drip_amount=arc4.UInt256(0),
                drip_count=arc4.UInt256(0),
                drip_last=arc4.UInt64(0),
            ),
        )

    @arc4.abimethod
    def donate(self, token_id: arc4.UInt64, amount: arc4.UInt256) -> None:
        """
        Donates a token to the faucet.
        """
        self._donate(Txn.sender, token_id.native, amount.native)

    @subroutine
    def _donate(self, sender: Account, token_id: UInt64, amount: BigUInt) -> None:
        """
        Donates a token to the faucet.
        """
        # TODO require payment if box is not found
        donation_data = self._donation_data(sender)
        arc4.abi_call(
            ARC200TokenInterface.arc200_transferFrom,  
            arc4.Address(sender),
            arc4.Address(Global.current_application_address),
            arc4.UInt256(amount),
            app_id=Application(token_id),
        )
        self.donations[sender] = DonationData(
            amount=arc4.UInt256(donation_data.amount.native + amount)
        )

    @arc4.abimethod
    def drip(self, token_id: arc4.UInt64) -> None:
        """
        Drips a token to the caller.
        """
        self._drip(Txn.sender, token_id.native)

    @subroutine
    def _drip(self, receiver: Account, token_id: UInt64) -> None:
        """
        Drips a token to the sender.
        """
        # TODO require payment if box is not found
        drip_data = self._drip_data(receiver)
        drip_last = drip_data.drip_last.native
        checkpoint = drip_last + self.drip_interval
        assert (
            checkpoint < Global.round
        ), "Not enough time has passed since the last drip"
        arc4.abi_call(
            ARC200TokenInterface.arc200_transfer,  
            arc4.Address(receiver),
            arc4.UInt256(self.drip_amount),
            app_id=Application(token_id),
        )
        self.drips[receiver] = DropData(
            drip_amount=arc4.UInt256(drip_data.drip_amount.native + self.drip_amount),
            drip_count=arc4.UInt256(drip_data.drip_count.native + 1),
            drip_last=arc4.UInt64(Global.round),
        )

    # TODO add box management
