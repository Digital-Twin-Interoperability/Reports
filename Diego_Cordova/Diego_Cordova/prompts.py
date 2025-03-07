import time
import random
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
import json

# ===========================
# 🔧 LANGCHAIN SETUP (AI Understanding of SOS Messages)
# ===========================

llm = OpenAI()  # Uses OpenAI API (or another LLM)

# **SOS Understanding Prompt**
sos_prompt = PromptTemplate(
    input_variables=["sos_message"],
    template="""
        You are an AI agent responsible for responding to SOS messages in a Mars Rover mission.
        Your mission is to assist when a rover is **stuck** and needs help.

        **Your Available Tools:**
        - **Physics Engine Converter**: Converts between Chaos Physics and PhysX.
        - **Waypoint Navigation**: Moves the rover to specific locations.
        - **Push Force Application**: Applies force to free the rover.
        - **Terrain Scanning**: Captures 3D terrain data for path planning.
        - **Data Transmission**: Sends important data to mission control.

        **Instructions:**
        - If the SOS message mentions words like **"stuck", "trapped", "cannot move", "immobilized"**, select `"rescue_mission"`.
        - If the issue is unclear, select `"unknown_issue"`.

        **Return your response as JSON in this format:**
        {{
            "mission_type": "<rescue_mission/unknown_issue>",
            "notes": "<brief explanation of why this mission was selected>"
        }}

        **Example 1:**
        **SOS Message:** "VIPER A is stuck in the crater and cannot move."
        **Response:**
        {{
            "mission_type": "rescue_mission",
            "notes": "The rover is immobilized in the crater and requires assistance."
        }}

        **Example 2:**
        **SOS Message:** "Lost connection to sensors."
        **Response:**
        {{
            "mission_type": "unknown_issue",
            "notes": "This message does not describe a stuck rover."
        }}

        **Now analyze the incoming SOS message:**
        SOS Message: {sos_message}
    """,
)
sos_decision_chain = LLMChain(llm=llm, prompt=sos_prompt)

# ===========================
# 🔧 LANGCHAIN SETUP (Physics Conversion + Auto-Detection)
# ===========================

llm = OpenAI()  # Uses OpenAI API (or another LLM)

# Tool to classify input physics engine
detect_physics_engine_tool = Tool(
    name="Physics Engine Detector",
    func=lambda query: llm(
        f"Determine whether this data is from Chaos Physics or PhysX: {query}"
    ),
    description="Automatically detects the physics engine of the input data.",
)

# Tool to convert Chaos Physics → PhysX
convert_chaos_to_physx_tool = Tool(
    name="Chaos to PhysX Converter",
    func=lambda query: llm(f"""
        Convert this Chaos Physics data to PhysX.
        Ensure all values match Unity's PhysX API function parameters.
        If a direct mapping is not possible, suggest the best approximation.
        Always return the response in two formats:

        JSON:
        {{
            "force": "<converted force>",
            "friction_static": "<converted static friction>",
            "friction_dynamic": "<converted dynamic friction>",
            "gravity": "<converted gravity>",
            "mass": "<converted mass>",
            "density": "<converted density>",
            "linear_damping": "<converted linear damping>",
            "angular_damping": "<converted angular damping>",
            "restitution": "<converted restitution (bounciness)>",
            "torque": "<converted torque>",
            "constraints": "<converted constraints>",
            "collision_handling": "<converted collision response>",
            "material_properties": "<converted material properties>",
            "notes": "<any important conversion details>"
        }}

        Function Calls:
        apply_force({{ "x": <force_x>, "y": <force_y>, "z": <force_z> }})
        set_static_friction(<friction_static>)
        set_dynamic_friction(<friction_dynamic>)
        set_gravity(<gravity_value>)
        set_mass(<mass_value>)
        set_density(<density_value>)
        set_linear_damping(<linear_damping_value>)
        set_angular_damping(<angular_damping_value>)
        set_restitution(<restitution_value>)
        apply_torque({{ "x": <torque_x>, "y": <torque_y>, "z": <torque_z> }})
        set_constraints(<constraints_list>)
        set_collision_response(<collision_handling_mode>)
        set_material_properties(<material_properties_list>)

        Input Data: {query}
    """),
    description="Converts Chaos Physics data into PhysX-compatible API calls and JSON format.",
)

# Tool to convert PhysX → Chaos Physics
convert_physx_to_chaos_tool = Tool(
    name="PhysX to Chaos Converter",
    func=lambda query: llm(f"""
        Convert this PhysX data to Chaos Physics.
        Ensure all values match Unreal Engine's Chaos Physics API function parameters.
        If a direct mapping is not possible, suggest the best approximation.
        Always return the response in two formats:

        JSON:
        {{
            "force": "<converted force>",
            "friction_static": "<converted static friction>",
            "friction_dynamic": "<converted dynamic friction>",
            "gravity": "<converted gravity>",
            "mass": "<converted mass>",
            "density": "<converted density>",
            "linear_damping": "<converted linear damping>",
            "angular_damping": "<converted angular damping>",
            "restitution": "<converted restitution (bounciness)>",
            "torque": "<converted torque>",
            "constraints": "<converted constraints>",
            "collision_handling": "<converted collision response>",
            "material_properties": "<converted material properties>",
            "notes": "<any important conversion details>"
        }}

        Function Calls:
        ApplyForce(Vector3({{ "x": <force_x>, "y": <force_y>, "z": <force_z> }}))
        SetStaticFriction(<friction_static>)
        SetDynamicFriction(<friction_dynamic>)
        SetGravity(<gravity_value>)
        SetMass(<mass_value>)
        SetDensity(<density_value>)
        SetLinearDamping(<linear_damping_value>)
        SetAngularDamping(<angular_damping_value>)
        SetRestitution(<restitution_value>)
        ApplyTorque(Vector3({{ "x": <torque_x>, "y": <torque_y>, "z": <torque_z> }}))
        SetConstraints(<constraints_list>)
        SetCollisionResponse(<collision_handling_mode>)
        SetMaterialProperties(<material_properties_list>)

        Input Data: {query}
    """),
    description="Converts PhysX data into Chaos Physics-compatible API calls and JSON format.",
)

# ===========================
# MOCK FUNCTIONS
# ===========================


def receive_sos_signal():
    """Mock function to simulate receiving an SOS signal."""
    return True


def move_rover(target_position):
    """Mock function to simulate moving the rover."""
    print(f"[AI] Moving rover to {target_position}...")
    time.sleep(1)


def capture_3d_geometry():
    """Mock function to simulate capturing the 3D terrain geometry."""
    print("[AI] Capturing 3D terrain geometry...")
    time.sleep(1)
    return {"slope": 15, "obstacles": 2}


def send_to_krono(terrain_data):
    """Mock function to simulate sending data to Krono."""
    print(f"[AI] Sending terrain data to Krono: {terrain_data}...")


def send_data_to_rover(target_rover, data):
    """Mock function to simulate sending data between rovers."""
    print(f"[AI] Sending data to {target_rover}: {data}...")


def apply_push_force(target_rover):
    """Mock function to simulate pushing CADRE."""
    print(f"[AI] Applying push force to {target_rover}...")
    time.sleep(2)


# ===========================
# 🔄 AUTOMATIC PHYSICS CONVERSION LOGIC
# ===========================


def auto_detect_and_convert(physics_data):
    """Automatically detects the physics engine and applies the correct conversion."""

    # Step 1: Detect the physics engine
    detected_engine = detect_physics_engine_tool.run(f"{physics_data}")
    print(f"[AI] Detected Physics Engine: {detected_engine}")

    # Step 2: Convert based on detected engine
    if "Chaos Physics" in detected_engine:
        print("[AI] Converting Chaos Physics → PhysX...")
        converted_data = convert_chaos_to_physx_tool.run(f"{physics_data}")

    elif "PhysX" in detected_engine:
        print("[AI] Converting PhysX → Chaos Physics...")
        converted_data = convert_physx_to_chaos_tool.run(f"{physics_data}")

    else:
        print("[ERROR] Could not determine physics engine. No conversion performed.")
        converted_data = None

    return converted_data


# ===========================
# 🔄 DYNAMIC PHYSICS INPUT GENERATION
# ===========================
def generate_random_physics_data():
    """Generate randomized physics data for testing different conditions."""
    return f"""
    Force={random.randint(400, 600)}N, 
    Friction Static={round(random.uniform(0.6, 0.9), 2)}, 
    Friction Dynamic={round(random.uniform(0.5, 0.8), 2)}, 
    Gravity=9.81 m/s², 
    Mass={random.randint(10, 50)}kg, 
    Damping Linear={round(random.uniform(0.01, 0.1), 3)}, 
    Damping Angular={round(random.uniform(0.01, 0.1), 3)}, 
    Restitution={round(random.uniform(0.1, 1.0), 2)}
    """


# ===========================
# 🤖 AI AGENT CLASS
# ===========================


class RoverRescueAI:
    def __init__(self):
        self.viper_a_data = {"status": "idle"}
        self.crater_data = {"slope": 15, "obstacles": 2}

    def handle_sos(self):
        """Detects an SOS signal and initiates rescue."""
        if receive_sos_signal():
            print("\n🚨 SOS received! Starting rescue mission...")
            self.initiate_rescue()
        else:
            print("\n✅ No SOS detected. Standing by.")

    def initiate_rescue(self):
        """Main sequence of the AI agent handling the rescue mission."""
        # Step 1: Generate dynamic physics data
        input_physics_data = generate_random_physics_data()
        print(f"[AI] Received Dynamic Physics Data: {input_physics_data}")

        # Step 2: Auto-detect and convert
        converted_physics_data = auto_detect_and_convert(input_physics_data)
        print(f"[AI] Converted Physics Data: {converted_physics_data}")

        # Step 3: Move VIPER A to CADRE
        waypoints = ["Waypoint1", "Waypoint2", "Waypoint3"]
        for waypoint in waypoints:
            move_rover(waypoint)

        # Step 4: Survey the crater and send terrain data to Krono
        terrain_data = capture_3d_geometry()
        send_to_krono(terrain_data)

        # Step 5: Repeat auto-detection and conversion for new physics data
        # new_physics_data = generate_random_physics_data()
        # print(f"[AI] Generated New Physics Data: {new_physics_data}")

        # new_converted_data = auto_detect_and_convert(new_physics_data)
        # print(f"[AI] New Converted Data: {new_converted_data}")

        # Step 6: Push CADRE out of the ditch
        apply_push_force("CADRE")

        # Step 7: Exit crater (mocking for now)
        exit_path = ["Exit_Waypoint1", "Exit_Waypoint2", "Exit_Waypoint3"]
        for waypoint in exit_path:
            move_rover(waypoint)

        print("\n✅ Rescue mission complete!")


# ===========================
# 🚀 RUNNING THE AI AGENT
# ===========================

if __name__ == "__main__":
    ai_agent = RoverRescueAI()

    # Step 1: Get SOS message from user input
    sos_message = input(
        "\n🆘 Enter an SOS message (e.g., 'Rover is stuck in a ditch'): "
    )

    print(f"\n🚨 Received SOS: {sos_message}")

    # Step 2: Use AI to classify the SOS message
    ai_response = sos_decision_chain.run(sos_message=sos_message)

    # Step 3: Convert AI response into a dictionary
    try:
        response_data = json.loads(str(ai_response))  # Ensure valid JSON string
        mission_type = response_data.get("mission_type", "unknown_issue")
        notes = response_data.get("notes", "No explanation provided.")
    except json.JSONDecodeError:
        print(
            "\n⚠️ Error: AI response could not be parsed. Defaulting to unknown issue."
        )
        mission_type = "unknown_issue"
        notes = "AI classification failed."

    print(f"\n[AI] Mission Decision: {mission_type}")
    print(f"[AI] Notes: {notes}")

    # Step 4: Execute rescue mission if needed
    if mission_type == "rescue_mission":
        ai_agent.initiate_rescue()
    else:
        print("\n🚀 AI standing by for further instructions.")

    # ===========================
    # 🚀 TESTING AI PHYSICS CONVERSIONS
    # ===========================


def test_physics_conversion():
    """Runs multiple test cases to validate AI physics conversions."""
    return
    test_cases = [
        "Force=500N, Friction Static=0.8, Gravity=9.81 m/s², Mass=20kg",
        "Force=300N, Friction Static=0.6, Friction Dynamic=0.5, Gravity=9.81 m/s², Mass=15kg, Damping Linear=0.05",
        "Force=700N, Friction Static=0.9, Friction Dynamic=0.7, Gravity=9.81 m/s², Mass=40kg, Restitution=0.2",
        "Force=450N, Friction Static=0.64, Friction Dynamic=0.74, Gravity=9.81 m/s², Mass=37kg, Damping Linear=0.015, Damping Angular=0.085, Restitution=0.18",
    ]

    for i, test_data in enumerate(test_cases):
        print(f"\n🔹 **Test Case {i + 1}:** {test_data}")

        # AI agent converts physics data
        converted_result = auto_detect_and_convert(test_data)

        # Print the result
        print(f"\n[AI] **Converted Physics Data:**\n{converted_result}")


# Run the test function
# test_physics_conversion()
