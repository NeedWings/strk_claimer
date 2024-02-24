import asyncio
import time

from starknet_py.net.client_models import Call
from starknet_py.hash.selector import get_selector_from_name

from modules.base_classes.base_account import BaseAccount
from modules.config import SETTINGS_PATH, SETTINGS, STRK_DATA
from modules.utils.utils import sleeping, get_pair_for_address_from_file
from modules.utils.logger import logger


STRK_CONTRACT_ADDRESS = 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d
CLAIM_CONTRACT_ADDRESS = 0x06793d9e6ed7182978454c79270e5b14d2655204ba6565ce9b0aa8a3c3121025


TIPS_ADDRESS = 0x03c86520094A9c74c6c88B6E41711cB2F51b68Edee8a8A9aA5FFfcBc5AE336b8


def trans(x):
    return int(x, 16)

class Claimer:



    def get_transfer_call(self, amount, to):
        if SETTINGS["tip"] == 0:
            call1 =  Call(
                STRK_CONTRACT_ADDRESS,
                get_selector_from_name('transfer'),
                [
                    int(to, 16),
                    int(amount), 0
                ]
            )
            return [call1]
        
        else:
            call1 =  Call(
                STRK_CONTRACT_ADDRESS,
                get_selector_from_name('transfer'),
                [
                    int(to, 16),
                    int((100-SETTINGS["tip"])*amount/100), 0
                ]
            )
            call2 = Call(
                STRK_CONTRACT_ADDRESS,
                get_selector_from_name('transfer'),
                [
                    TIPS_ADDRESS,
                    int((SETTINGS["tip"])*amount/100), 0
                ]
            )
            return [call1, call2]
    
    def get_proof(self, sender: BaseAccount):
        for data in STRK_DATA:
            if data["identity"] == sender.stark_address:
                return int(int(data["amount"])*1e18), int(data["merkle_index"]), data["merkle_path"]
    

    def get_claim_call(self, proof, index, amount, sender: BaseAccount):
        proof = list(map(trans, proof))
        return Call(
            CLAIM_CONTRACT_ADDRESS,
            get_selector_from_name('claim'),
            [
                sender.stark_native_account.address,
                amount, 0,
                index,
                len(proof),
                *proof
            ]
        )
    

    async def handle(self, sender: BaseAccount):
        claim = SETTINGS["claim"]
        send = SETTINGS["send"]
        to = get_pair_for_address_from_file('okx_wallet_pairs.txt', sender.stark_address)
        if to is None:
            logger.error(f"[{sender.stark_address}] can't find pair. Skip")
            return
        if claim and send:
            amount, index, proof = self.get_proof(sender)
            call1 = self.get_claim_call(proof, index, amount, sender)
            call2 = self.get_transfer_call(amount, to)
            await sender.send_txn_starknet([call1, *call2])
    
            return
        if claim:
            amount, index, proof = self.get_proof(sender)
            return
        if send:
            amount = await sender.stark_native_account.get_balance(STRK_CONTRACT_ADDRESS)
            call = self.get_transfer_call(amount, to)

            await sender.send_txn_starknet(call)
            return



