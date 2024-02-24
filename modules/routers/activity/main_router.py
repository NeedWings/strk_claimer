from asyncio import Event, sleep
from random import choice

from modules.utils.account import Account
from modules.other.strk_claimer import Claimer
from modules.utils.logger import logger
from modules.utils.utils import get_pair_for_address_from_file
from modules.config import SETTINGS

class MainRouter():
    def __init__(self, private_key: str, delay: int, task_number: int, proxy=None) -> None:
        self.task_number = task_number

        self.account = Account(private_key, proxy=proxy)

        self.delay = delay

    
    async def start(self, gas_lock: Event = None, one_thread_lock: Event = None):
        await self.account.setup_account()
        if self.task_number == 1:
            claimer = Claimer()
            await claimer.handle(self.account)
    