try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    print("PySerial not found. Please install it using: pip install pyserial")
    print("Running in simulation mode without Arduino connection.")
    SERIAL_AVAILABLE = False

import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import time
import contextlib

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name="data")

arduino = None
if SERIAL_AVAILABLE:
    try:
        arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        print("Successfully connected to Arduino on /dev/ttyACM0")
    except serial.SerialException:
        try:
            arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            print("Successfully connected to Arduino on /dev/ttyUSB0")
        except serial.SerialException:
            print("Could not connect to Arduino. Running in simulation mode.")
            arduino = None

SIMULATION_MODE = arduino is None

active_connections = []

@app.get("/")
async def index():
    return HTMLResponse(open("index.html").read())

async def get_simulated_data():
    import random
    data_type = random.choice(["SENSOR", "SOUND", "TOUCH"])
    if data_type == "SENSOR":
        value = random.randint(5, 300)
        return f"[SENSOR]: {value}"
    elif data_type == "SOUND":
        value = random.randint(100, 800)
        return f"[SOUND]: {value}"
    else:
        value = random.randint(0, 1023)
        return f"[TOUCH]: {value}"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    active_connections.append(websocket)
    try:
        while True:
            try:
                if SIMULATION_MODE:
                    data = await get_simulated_data()
                else:
                    data = arduino.readline().decode("utf-8", errors="ignore").strip()
                if data.startswith("[SENSOR]:"):
                    value = data.replace("[SENSOR]:", "").strip()
                    await websocket.send_json({"type": "sensor", "value": value})
                elif data.startswith("[SOUND]:"):
                    value = data.replace("[SOUND]:", "").strip()
                    await websocket.send_json({"type": "sound", "value": value})
                elif data.startswith("[TOUCH]:"):
                    value = data.replace("[TOUCH]:", "").strip()
                    await websocket.send_json({"type": "touch", "value": value})
                await asyncio.sleep(0.1)
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Error sending data: {e}")
                await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected normally")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        with contextlib.suppress(ValueError):
            active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    print("Starting Smart Alarm server at http://localhost:8000")
    print("Press Ctrl+C to exit")
    uvicorn.run(app, host="0.0.0.0", port=8000)
