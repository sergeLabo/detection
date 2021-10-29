

from time import sleep
import asyncio
import json



class MyStream:

    async def tcp_echo_client(self, message):
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

        print(f'Send: {message!r}')
        data = json.dumps(message)
        writer.write(data.encode())


def main():
    skelets_3D = [[[-553, -646, 2930], [-534, -689, 2952], [-580, -677, 2921], [-490, -699, 2999], [-614, -669, 2927], [-358, -556, 3050], [-696, -544, 3087], [-301, -268, 3015], [-701, -243, 3116], None, None, [-398, -6, 3101], [-629, -59, 3079], None, [-627, 194, 3092], [-559, 648, 3200], [-650, 652, 3169]]]

    ms = MyStream()
    while 1:
        asyncio.run(ms.tcp_echo_client(skelets_3D))
        sleep(0.1)

main()
