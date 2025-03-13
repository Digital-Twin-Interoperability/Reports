import time
import random
import json
from langchain_openai import OpenAI
from langchain.schema.runnable import RunnableLambda
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

# ===========================
# 🔧 LANGCHAIN SETUP (AI Understanding of SOS Messages)
# ===========================

llm = OpenAI()  # Uses OpenAI API (or another LLM)

# **SOS Understanding Prompt**
sos_prompt = PromptTemplate(
    input_variables=["sos_message"],
    template="""
        You are an AI agent responsible for responding to SOS messages in a Rover mission.
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
sos_decision_chain = RunnableLambda(lambda x: llm.invoke(sos_prompt.format(**x)))

# ===========================
# 🔧 LANGCHAIN SETUP (Physics Conversion + Auto-Detection)
# ===========================

llm = OpenAI()  # Uses OpenAI API (or another LLM)

# Tool to classify input physics engine
detect_physics_engine_tool = Tool(
    name="Physics Engine Detector",
    func=lambda query: llm.invoke(
        f"Determine whether this data is from Chaos Physics or PhysX: {query}"
    ),
    description="Automatically detects the physics engine of the input data.",
)

# Tool to convert Chaos Physics → PhysX
convert_chaos_to_physx_tool = Tool(
    name="Chaos to PhysX Converter",
    func=lambda query: llm.invoke(f"""
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
            "constraints": "<converted constraints>" if "<converted constraints>" else "N/A",
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
    func=lambda query: llm.invoke(f"""
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
            "constraints": "<converted constraints>" if "<converted constraints>" else "N/A",
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


class RoverAI:
    def __init__(self):
        """
        Initialize the AI agent with necessary parameters.
        """
        self.viper_position = None
        self.cadre_position = None
        self.path_plan = []
        self.current_force = 0
        self.running = True  # Keeps the AI agent running continuously
        self.retry_attempts = 0  # ✅ Track number of retry attempts
        self.llm = OpenAI()

        # Setup LLM for SOS message understanding
        sos_prompt = PromptTemplate(
            input_variables=["sos_message"],
            template="""
                You are an AI agent responsible for responding to SOS messages in a Rover mission.
                Your mission is to assist when a rover is **stuck** and needs help.
                If the message mentions words like "stuck", "trapped", "immobilized", select "rescue_mission".
                Otherwise, select "unknown_issue".
                Return JSON format:
                {{
                    "mission_type": "<rescue_mission/unknown_issue>",
                    "notes": "<explanation>"
                }}
                SOS Message: {sos_message}
            """,
        )
        self.sos_decision_chain = RunnableLambda(
            lambda x: self.llm.invoke(sos_prompt.format(**x))
        )

    # ==================== 4️⃣ CHECK RESCUE STATUS ====================
    def check_rescue_statuss(self):
        return
        """Mock function: Checks if CADRE has exited the crater."""
        print("[MOCK] Checking if CADRE is out of the crater...")
        return True  # ✅ Assume success for now (modify for future logic)

    def check_rescue_status(self):
        """
        Mock function: Simulates CADRE's status.
        - First attempt fails.
        - AI retries, then succeeds.
        """
        if self.retry_attempts == 0:
            print("[WARNING] CADRE is still stuck. Adjusting approach and retrying...")
            self.retry_attempts += 1  # Increment retry counter
            return False  # ❌ First attempt fails

        print("[SUCCESS] CADRE has been successfully rescued on retry attempt!")
        return True  # ✅ Second attempt succeeds

    # ==================== 1️⃣ RECEIVE SOS MESSAGE ====================
    def receive_sos_signal(self):
        """Mock function: Receives SOS signal from CADRE."""
        print("[MOCK] VIPER A received SOS signal from CADRE.")
        return True

    # ==================== 2️⃣ GET CADRE'S ENVIRONMENT DATA ====================
    def get_cadre_status(self):
        """Mock function: Returns different CADRE environment data on each call to simulate changing conditions."""

        if self.retry_attempts == 0:
            print("[MOCK] Fetching CADRE environment data (First Attempt).")
            return {
                "position": (5, -3),
                "rotation": 45,
                "physics_engine": "Chaos",
                "force": "500N",
                "friction_coefficient": "0.9",  # High friction → harder to move
                "gravity": "9.81 m/s²",
                "mass": "30kg",  # Heavy → harder to push
                "density": "2.5kg/m³",
                "drag_coefficient": "0.08",
                "angular_damping": "0.03",
                "restitution": "0.2",
                "torque": "120Nm",
                "collision_response": "Physics Sub-Step",
            }

        else:  # ✅ Ensures the function always returns a valid dictionary
            print("[MOCK] Fetching CADRE environment data (Second Attempt).")
            return {
                "position": (5, -3),
                "rotation": 45,
                "physics_engine": "Chaos",
                "force": "700N",  # Increased force → better chance of freeing
                "friction_coefficient": "0.6",  # Lower friction → easier to move
                "gravity": "9.81 m/s²",
                "mass": "20kg",  # Reduced mass → easier to push
                "density": "2.0kg/m³",
                "drag_coefficient": "0.05",
                "angular_damping": "0.02",
                "restitution": "0.4",
                "torque": "140Nm",
                "collision_response": "Physics Sub-Step",
            }

    # ==================== 3️⃣ REQUEST PATH PLANNING ====================
    def request_path_plan(self):
        """Mock function: Requests a path plan from LLM."""
        print("[MOCK] Requesting LLM path plan.")
        return [(5, -3), (4, -2), (3, -1)]

    # ==================== 4️⃣ CONVERT PHYSICS USING LLM ====================
    def convert_physics_data(self, physics_data):
        """Detects physics engine type and converts physics data using LLM."""
        detected_engine = detect_physics_engine_tool.run(json.dumps(physics_data))
        print(f"[DEBUG] Detected Physics Engine: {detected_engine}")

        if "Chaos Physics" in detected_engine:
            print("[AI] Converting Chaos Physics → PhysX...")
            converted_data = convert_chaos_to_physx_tool.run(json.dumps(physics_data))
        elif "PhysX" in detected_engine:
            print("[AI] Converting PhysX → Chaos Physics...")
            converted_data = convert_physx_to_chaos_tool.run(json.dumps(physics_data))
        else:
            print(
                "[ERROR] Could not determine physics engine. No conversion performed."
            )
            converted_data = None

        return converted_data

    # ==================== MAIN AI AGENT WORKFLOW ====================
    def run(self):
        """
        Runs the AI agent's decision-making process in real-time.
        If an error occurs, it logs the error but continues running.
        """
        while self.running:
            try:
                if not self.receive_sos_signal():
                    print("[INFO] No SOS signal received, AI agent waiting...")
                    time.sleep(2)
                    continue

                cadre_data = self.get_cadre_status()
                self.cadre_position = cadre_data["position"]

                self.path_plan = self.request_path_plan()

                print("[INFO] Moving VIPER A to CADRE's location...")

                physics_conversion = self.convert_physics_data(cadre_data)
                print(f"[INFO] Converted Physics Data: {physics_conversion}")

                print("[INFO] Applying push force dynamically...")

                if self.check_rescue_status():
                    print("[SUCCESS] CADRE has been successfully rescued!")
                    self.running = False
                else:
                    print(
                        "[WARNING] CADRE is still stuck. Adjusting approach and retrying..."
                    )

            except Exception as e:
                print(f"[ERROR] An exception occurred: {e}")

            finally:
                print("[INFO] AI Agent is still running, ensuring no crash.")

        time.sleep(2)


# ==================== RUN AI AGENT ====================
if __name__ == "__main__":
    ai_agent = RoverAI()

    sos_message = input(
        "\n🆘 Enter an SOS message (e.g., 'Rover is stuck in a ditch'): "
    )
    print(f"\n🚨 Received SOS: {sos_message}")

    ai_response = ai_agent.sos_decision_chain.invoke({"sos_message": sos_message})

    try:
        response_text = str(ai_response).strip()
        if response_text.startswith("{") and response_text.endswith("}"):
            response_data = json.loads(response_text)
            mission_type = response_data.get("mission_type", "unknown_issue")
            notes = response_data.get("notes", "No explanation provided.")
        else:
            raise ValueError("AI response is not in JSON format.")
    except (json.JSONDecodeError, ValueError) as e:
        print(
            f"\n⚠️ Error: AI response could not be parsed - {e}. Defaulting to unknown issue."
        )
        mission_type = "unknown_issue"
        notes = "AI classification failed."

    print(f"\n[AI] Mission Decision: {mission_type}")
    print(f"[AI] Notes: {notes}")

    if mission_type == "rescue_mission":
        ai_agent.run()
    else:
        print("\n🚀 AI standing by for further instructions.")
