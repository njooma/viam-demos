import asyncio

from viam.components.input import Control, Controller, EventType
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions


async def client():
    creds = Credentials(
        type='robot-location-secret',
        payload='pem1epjv07fq2cz2z5723gq6ntuyhue5t30boohkiz3iqht4')
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    async with await RobotClient.at_address('naveed-pi-main.60758fe0f6.local.viam.cloud:8080', opts) as robot:
        print('Resources:')
        print(robot.resource_names)

        controller = Controller.from_robot(robot, 'controller')
        controller.register_control_callback(
            Control.BUTTON_START, [EventType.ALL_EVENTS], lambda ev: print(ev))

        while True:
            await asyncio.sleep(0.01)


if __name__ == '__main__':
    try:
        asyncio.run(client())
        while True:
            pass
    except KeyboardInterrupt:
        pass
