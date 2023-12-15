from pyrogram import filters

from logger.create_logger import logger


class MainFSM:
    """Custom Finite State Machine"""
    chill = "chill"

    del_chat_1 = "del_chat_1"
    del_chat_2 = "del_chat_2"

    add_chat_1 = "add_chat_1"
    add_chat_2 = "add_chat_2"
    add_chat_3 = "add_chat_3"

    set_msg_1 = "set_msg_1"
    set_msg_2 = "set_msg_2"

    stop_msg_1 = "stop_msg_1"

    start_msg_1 = "start_msg_1"

    int_chat_1 = "int_chat_1"
    int_chat_2 = "int_chat_2"

    int_chats_1 = "int_chats_1"
    int_chats_2 = "int_chats_2"

    def __init__(self):
        self._data = {}
        self._state = "chill"
        self._states = [
            self.chill,
            self.del_chat_1,
            self.del_chat_2,
            self.add_chat_1,
            self.add_chat_2,
            self.add_chat_3,
            self.set_msg_1,
            self.set_msg_2,
            self.int_chat_1,
            self.int_chat_2,
            self.int_chats_1,
            self.int_chats_2,
            self.stop_msg_1,
            self.start_msg_1
        ]

    async def get_data(self) -> dict:
        """Retrieving data from machine state storage"""
        return self._data

    async def set_data(self, **kwargs) -> None:
        """Changing data in machine state storage"""
        self._data.update(kwargs)

    async def clear(self):
        """Resetting state and data in machine states"""
        self._state = "chill"
        self._data.clear()

        logger.info(f"[CUSTOM_FSM] FSM cleared, new_state: \"{self._state}\"")

    async def get_state(self) -> str:
        """Getting the current state from the machine state"""
        return self._state

    async def set_state(self, state: str) -> bool:
        """Changing the current state of a machine state"""
        if state not in self._states:
            return False

        else:
            logger.info(f"[CUSTOM_FSM] FSM state changed - old_state: \"{self._state}\" ; new_state: \"{state}\"")
            self._state = state

            return True

    async def get_states(self) -> list[str, ...]:
        """Getting the names of all machine state states"""
        return self._states

    async def next_state(self) -> str:
        """Replacing a machine state with the following"""
        logger.info(f"[CUSTOM_FSM] FSM state changed (next) - old_state: \"{self._state}\" ; new_state: \"{self._states[self._states.index(self._state) + 1]}\"")
        self._state = self._states[self._states.index(self._state) + 1]

        return self._state

    def check_state(self, state: str):
        """Custom Filter: check state FSM"""

        async def state_filter_check(_, __, ___):
            return self._state == state

        return filters.create(state_filter_check)


main_fsm = MainFSM()
