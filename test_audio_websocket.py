import asyncio
import websockets
import json
import signal
import sys

# Flag to control the WebSocket loop
running = True

def signal_handler(sig, frame):
    global running
    print("\nStopping WebSocket client...")
    running = False

async def test_audio_websocket():
    uri = "ws://localhost:8001/ws/audio"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            
            # Send a test message
            test_message = {"type": "get_devices"}
            await websocket.send(json.dumps(test_message))
            print(f"Sent: {test_message}")
            
            # Listen for messages
            while running:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"Received: {response}")
                except asyncio.TimeoutError:
                    # No message received within timeout, just continue
                    pass
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"WebSocket connection closed: {e}")
                    break
                except Exception as e:
                    print(f"Error receiving message: {e}")
                    break
                    
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("WebSocket client stopped")

if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting WebSocket client. Press Ctrl+C to stop.")
    asyncio.get_event_loop().run_until_complete(test_audio_websocket())
