import asyncio
import struct
from multiprocessing import Lock
from typing import Dict, List, Optional

from viam.components.input import (Control, ControlFunction, Controller, Event,
                                   EventType)
from viam.rpc.server import Server


class MyController(Controller):

    CONTROL_MAP: Dict[int, Control] = {
        0:   Control.ABSOLUTE_X,
        1:   Control.ABSOLUTE_Y,
        2:   Control.ABSOLUTE_Z,
        3:   Control.ABSOLUTE_RX,
        4:   Control.ABSOLUTE_RY,
        5:   Control.ABSOLUTE_RZ,
        16:  Control.ABSOLUTE_HAT0_X,
        17:  Control.ABSOLUTE_HAT0_Y,
        304: Control.BUTTON_SOUTH,
        305: Control.BUTTON_EAST,
        307: Control.BUTTON_WEST,
        308: Control.BUTTON_NORTH,
        310: Control.BUTTON_LT,
        311: Control.BUTTON_RT,
        314: Control.BUTTON_SELECT,
        315: Control.BUTTON_START,
        317: Control.BUTTON_L_THUMB,
        318: Control.BUTTON_R_THUMB,
        316: Control.BUTTON_MENU,
    }

    def __init__(self, name: str):
        super().__init__(name)
        self.last_events: Dict[Control, Event] = {}
        self.callbacks: Dict[Control,
                             Dict[EventType, Optional[ControlFunction]]] = {}
        self.lock = Lock()

        self.f = open('/dev/input/event0', 'rb')
        asyncio.get_running_loop().add_reader(self.f, self._read_input)

    def _read_input(self):
        data = self.f.read(24)
        raw = struct.unpack('4IHHI', data)
        if raw[4:] == (0, 0, 0):
            return
        secs = raw[0]
        nanos = raw[2]
        control = MyController.CONTROL_MAP[raw[5]]
        value = raw[6]
        e_type: EventType
        if raw[5] < 20:
            e_type = EventType.POSITION_CHANGE_ABSOLUTE
        else:
            e_type = EventType.BUTTON_RELEASE
            if value == 1:
                e_type = EventType.BUTTON_PRESS
        if value == 4294967295:
            value = -1
        event = Event(
            time=float(((secs*1e9)+nanos)/1e9),
            control=control,
            event=e_type,
            value=value
        )
        with self.lock:
            self.last_events[control] = event

        self._execute_callback(event)

    def _execute_callback(self, event):
        with self.lock:
            callback = self.callbacks.get(
                event.control, {}).get(event.event, None)
            if callback:
                callback(event)

            callback = self.callbacks.get(event.control, {}).get(
                EventType.ALL_EVENTS, None)
            if callback:
                callback(event)

    async def get_controls(self) -> List[Control]:
        return [
            Control.ABSOLUTE_X,
            Control.ABSOLUTE_Y,
            Control.ABSOLUTE_Z,
            Control.ABSOLUTE_RX,
            Control.ABSOLUTE_RY,
            Control.ABSOLUTE_RZ,
            Control.ABSOLUTE_HAT0_X,
            Control.ABSOLUTE_HAT0_Y,
            Control.BUTTON_SOUTH,
            Control.BUTTON_EAST,
            Control.BUTTON_WEST,
            Control.BUTTON_NORTH,
            Control.BUTTON_LT,
            Control.BUTTON_RT,
            Control.BUTTON_L_THUMB,
            Control.BUTTON_R_THUMB,
            Control.BUTTON_SELECT,
            Control.BUTTON_START,
            Control.BUTTON_MENU,
        ]

    async def get_events(self) -> Dict[Control, Event]:
        with self.lock:
            return {key: value for (key, value) in self.last_events.items()}

    def register_control_callback(
        self,
        control: Control,
        triggers: List[EventType],
        function: Optional[ControlFunction]
    ):
        with self.lock:
            callbacks = self.callbacks.get(control, {})
            for trigger in triggers:
                if trigger == EventType.BUTTON_CHANGE:
                    callbacks[EventType.BUTTON_PRESS] = function
                    callbacks[EventType.BUTTON_RELEASE] = function
                else:
                    callbacks[trigger] = function
            self.callbacks[control] = callbacks


async def main():
    srv = Server(components=[MyController('controller')])
    await srv.serve()

if __name__ == '__main__':
    asyncio.run(main())
