import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8001/ws/audio"
    try:
        async with websockets.connect(uri) as websocket:
            # Test get_devices
            await websocket.send(json.dumps({"type": "get_devices"}))
            response = await websocket.recv()
            print(f"Received: {response}")
            
            # Test start capture (use default device)
            await websocket.send(json.dumps({"type": "start"}))
            print("Sent start command")
            
            # Listen for audio levels for 5 seconds
            print("Listening for audio levels (5 seconds)...")
            for _ in range(5):
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"Audio level: {response}")
                except asyncio.TimeoutError:
                    print("No audio level received in 1 second")
            
            # Stop capture
            await websocket.send(json.dumps({"type": "stop"}))
            print("Sent stop command")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_websocket())
