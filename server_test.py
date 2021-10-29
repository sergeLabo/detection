
import asyncio
import json

async def handle_skelet(reader, writer):
    data = await reader.read(4096)
    message = data.decode()
    print(message)

    skelets = json.loads(message)
    print("Skelets:", type(skelets))
    print(skelets)


async def main():
    server = await asyncio.start_server(
        handle_skelet, '127.0.0.1', 8888)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
