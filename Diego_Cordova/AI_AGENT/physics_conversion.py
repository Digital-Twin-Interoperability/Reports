import json
from p import (
    detect_physics_engine_tool,
    convert_chaos_to_physx_tool,
    convert_physx_to_chaos_tool,
)


# ✅ Detect Physics Engine
def detect_physics_engine(physics_data):
    detected_engine = detect_physics_engine_tool.run(physics_data).strip()
    return detected_engine


# ✅ Convert Physics Data (Handles both Chaos → PhysX and PhysX → Chaos)
def convert_physics_data(physics_data):
    engine_detected = detect_physics_engine(physics_data)

    if "Chaos Physics" in engine_detected:
        converted = convert_chaos_to_physx_tool.run(physics_data)
        return json.dumps(
            {
                "original_engine": "Chaos Physics",
                "converted_to": "PhysX",
                "converted_data": converted,
            },
            indent=4,
        )

    elif "PhysX" in engine_detected:
        converted = convert_physx_to_chaos_tool.run(physics_data)
        return json.dumps(
            {
                "original_engine": "PhysX",
                "converted_to": "Chaos Physics",
                "converted_data": converted,
            },
            indent=4,
        )

    else:
        return json.dumps({"message": "Unknown physics engine."}, indent=4)
