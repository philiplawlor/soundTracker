import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8001/ws/test"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            await websocket.send("Hello, WebSocket!")
            response = await websocket.recv()
            print(f"Received: {response}")
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_websocket())
