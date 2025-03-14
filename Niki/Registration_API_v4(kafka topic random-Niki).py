import json
import os
import subprocess
import mysql.connector
import random
import string
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer
from CLItool import extract_did_from_private_key


# Kafka Configuration
KAFKA_CONFIG = {
    "bootstrap.servers": "localhost:9092"
}
admin_client = AdminClient(KAFKA_CONFIG)
producer = Producer(KAFKA_CONFIG)

# MySQL Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "MoonwalkerJPL85!",
    "database": "did_registry"
}

# Connect to MySQL
def connect_db():
    return mysql.connector.connect(**db_config)

# Function to create a Kafka topic for Agents
def create_kafka_topic(topic_name, num_partitions=1, replication_factor=1):
    """Creates a Kafka topic using Confluent Kafka AdminClient"""
    topic_list = [NewTopic(topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
    fs = admin_client.create_topics(topic_list)
    
    for topic, f in fs.items():
        try:
            f.result()  # Block until topic creation is done
            print(f"Kafka topic '{topic}' created successfully.")
        except Exception as e:
            print(f"Failed to create topic '{topic}': {e}")

#Generate random string for Kafka Topic name
def generate_random_string(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Function to send a Kafka message
def send_kafka_message(topic, message):
    """Sends a message to a Kafka topic"""
    try:
        producer.produce(topic, json.dumps(message))
        producer.flush()
        print(f"Message sent to Kafka topic '{topic}': {message}")
    except Exception as e:
        print(f"Failed to send message to Kafka topic '{topic}': {e}")

# Function to generate DID:key using CLI tool (modified)
def generate_did_key():
    """Runs the CLI tool to generate a DID:key and extract the private key"""
    result = subprocess.run(["python", "CLItool.py", "--export-private"], capture_output=True, text=True)
    print(f"Subprocess output:\n{result.stdout}")  # Add this line for debugging
    output = result.stdout.split("\n")
    
    # Extract DID:key from the stdout (terminal output)
    did_key = None
    output = result.stdout.splitlines()
    
    for line in output:
        if line.startswith("Generated DID:key:"):
            did_key = line.split("Generated DID:key:")[1].strip()
    
    if not did_key:
        raise ValueError("Failed to generate DID:key from output")

    # Now, read the private key from the saved file "private_key.pem"
    private_key_path = "private_key.pem"
    try:
        with open(private_key_path, "rb") as key_file:
            private_key = key_file.read()  # Read the private key as bytes
    except FileNotFoundError:
        raise ValueError(f"Private key file '{private_key_path}' not found")
    
    # Return DID:key and private key as a PEM string
    return did_key, private_key.decode("utf-8")  # Decode private key bytes to string

# Function for login before registering
def login_or_register():
    choice = input("Must be registered in the Spatial Web to register a new Entity. Type 'new' to register or 'login' if already registered: ")
    db = connect_db()
    cursor = db.cursor()
    if choice.lower() == "new":
        print("Registering a new user. You can only register a Person or Organization.")
        return None
    elif choice.lower() == "login":
        private_key_path = input("Provide your private_key.pem path: ")
        user_did = extract_did_from_private_key(private_key_path)
        cursor.execute("SELECT metadata FROM did_keys WHERE did = %s", (user_did,))
        result = cursor.fetchone()
        if not result:
            print("DID not found in database. Please register first.")
            return None
        user_data = json.loads(result[0])
        if user_data.get("@type") not in ["Person", "Organization"]:
            print("Only registered Persons or Organizations can register new entities.")
            return None
        print(f"Welcome {user_data.get('name')}, you can now register your new Entity.")
        return user_did
    else:
        print("Invalid choice.")
        return None

# Function to validate JSON and register entity
def register_entity(json_file_path, output_directory, registered_by=None):
    """Validates, registers, and stores an HSML entity"""
    try:
        with open(json_file_path, "r") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON format"}
    
    # Check if JSON file is actually JSON
    if not isinstance(data, dict):
        return {"status": "error", "message": "Uploaded file is not a valid JSON object"}

    # Check @context for HSML
    if "@context" not in data or "https://digital-twin-interoperability.github.io/hsml-schema-context/hsml.jsonld" not in data["@context"]:
        return {"status": "error", "message": "Not a valid HSML JSON"}

    print("HSML JSON accepted.")

    # Check for required fields based on type
    entity_type = data.get("@type")
    required_fields = {
        "Entity": ["name", "description"],
        "Person": ["name", "birthDate", "email"],
        "Agent": ["name", "creator", "dateCreated", "dateModified", "description"],
        "Credential": ["name", "description", "issuedBy", "accessAuthorization", "authorizedForDomain"],
        "Organization": ["name", "description", "url","address", "logo", "foundingDate", "email"]
    }
    
    if entity_type not in required_fields:
        return {"status": "error", "message": "Unknown or missing entity type"}

    missing_fields = [field for field in required_fields[entity_type] if field not in data]
    if missing_fields:
        return {"status": "error", "message": f"Missing required fields: {missing_fields}"}

    # Check additional conditions per type
    if entity_type == "Person" and "affiliation" not in data:
        print("Warning: 'affiliation' field is missing.")
    
    if entity_type == "Credential" and ("validFrom" not in data or "validUntil" not in data):
        print("Warning: Credential has no expiration date.")

    if entity_type == "Entity" and "linkedTo" not in data:
        print("Warning: Object not linked to any other Entity. It will be registered under this user’s SWID.")

    # Check if SWID exists in DB
    swid = data.get("swid")
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM did_keys WHERE did = %s", (swid,))
    existing = cursor.fetchone()[0]
    
    if existing:
        print(f"Warning: SWID '{swid}' already exists and will be overwritten.")

    # Generate a new DID:key and private key
    did_key, private_key = generate_did_key()
    data["swid"] = did_key  # Attach new DID:key to swid
    public_key_part = did_key.replace("did:key:", "") # Only leaves the public key part

    # If what is being registered is a Person/Organization for the first time (when no existing user_did)
    if registered_by is None:
        registered_by = did_key

    topic_name = None
    flagUniqueName = False
    # Special case: If entity is an "Agent", create a Kafka topic
    if entity_type == "Agent":
        while flagUniqueName == False:
            random_suffix = generate_random_string()
            topic_name = f"{data["name"].replace(" ", "_").lower()}_{random_suffix}"
            cursor.execute("SELECT COUNT(*) FROM did.keys WHERE kafka_topic = %s", (topic_name,))
            existing = cursor.fetchone()

            if existing[0]==0:
                flagUniqueName = True
            else:
                flagUniqueName=False

            create_kafka_topic(topic_name)
            send_kafka_message(topic_name, {"message": f"New Agent registered: {data['name']}"})
            
     

    # Store in MySQL
    cursor.execute(
        "REPLACE INTO did_keys (did, public_key, metadata, registered_by, kafka_topic) VALUES (%s, %s, %s, %s, %s)",
        (did_key, public_key_part, json.dumps(data), registered_by, topic_name)
    )
    db.commit()
    db.close()

    # Ask user where to save files
    private_key_output = os.path.join(output_directory, "private_key.pem")
    json_output = os.path.join(output_directory, f"{data['name'].replace(' ', '_')}.json")

    # Save private key file (there was an error here, had to modify to this)
    with open(private_key_output, "w") as private_key_file:
        private_key_file.write(private_key)

    # Save JSON file
    with open(json_output, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Private key saved to: {private_key_output}")
    print(f"Updated JSON saved to: {json_output}")

    return {
        "status": "success",
        "message": "Entity registered successfully",
        "did_key": did_key,
        "private_key_path": private_key_output,
        "updated_json_path": json_output
    }

# Example usage
if __name__ == "__main__":
    user_did = login_or_register()
    #json_file_path = "C:/Users/abarrio/OneDrive - JPL/Desktop/Digital Twin Interoperability/Codes/HSML Examples/Examples 2025-02-03/entityExample/entityExample.json"  # Provide your JSON file
    if user_did is not None:
        json_file_path = input("Enter the directory to your HSML JSON to be registered: ")
        #output_directory = input("Enter the directory to save the private key and updated JSON: ")
        output_directory = "C:/Users/abarrio/OneDrive - JPL/Desktop/Digital Twin Interoperability/Codes/HSML Examples/registeredExamples"

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        result = register_entity(json_file_path, output_directory, registered_by=user_did)
        print(result)
    else:
        while True:
            json_file_path = input("Enter the directory to your Person/Organization HSML JSON to be registered: ")
            # Load JSON to check its @type is really Person or Organization
            try:
                with open(json_file_path, "r") as file:
                    data = json.load(file)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format.")
                #exit(1)
                continue 

            if data.get("@type") not in ["Person", "Organization"]:
                print("Error: You can only register a Person or Organization as a new user.")
                # exit(1)
                continue
            break

        output_directory = "C:/Users/abarrio/OneDrive - JPL/Desktop/Digital Twin Interoperability/Codes/HSML Examples/registeredExamples"

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        result = register_entity(json_file_path, output_directory, registered_by=None)
        print(result)

