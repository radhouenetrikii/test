import asyncio
from mavsdk import System
import math

def enu_to_latlon(x, y, z, ref_lat, ref_lon, ref_alt=0):
    R = 6378137.0  # Earth's radius in meters
    ref_lat_rad = math.radians(ref_lat)
    delta_lat = y / R
    lat = ref_lat + math.degrees(delta_lat)
    delta_lon = x / (R * math.cos(ref_lat_rad))
    lon = ref_lon + math.degrees(delta_lon)
    alt = z + ref_alt
    return lat, lon, alt

async def main():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break

    print("Waiting for GPS fix...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("GPS is ready")
            break

    # Takeoff to a safe altitude
    altitude = 5
    await drone.action.arm()
    print("Arming...")
    await drone.action.takeoff()
    print(f"Taking off to {altitude} meters...")
    await asyncio.sleep(10)

    # Reference point (Gazebo origin)
    ref_lat = 47.397971057728974
    ref_lon = 8.546163739800146

    # Cylinder 3 ENU coordinates
    x, y, z = 300.0, 30.0, 0.0

    # Convert ENU to geographic coordinates
    target_lat, target_lon, target_alt = enu_to_latlon(x, y, z, ref_lat, ref_lon, 0)

    # Fly to Cylinder 3
    print(f"Flying to target: Latitude={target_lat}, Longitude={target_lon}, Altitude={altitude}")
    await drone.action.goto_location(target_lat, target_lon, altitude, 0)
    await asyncio.sleep(20)

    # Loiter at the target
    print("Loitering at target for 50 seconds...")
    await asyncio.sleep(50)

    # Return to launch
    print("Mission complete. Returning to launch...")
    await drone.action.return_to_launch()
    print("Landing...")
    await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
