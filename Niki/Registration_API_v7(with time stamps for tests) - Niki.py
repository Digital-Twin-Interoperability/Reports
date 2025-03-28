import json
import os
import subprocess
import random
import string
import time
import mysql.connector
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
    "password": "NNbaking.105",
    "database": "did_registry"
}

# Connect to MySQL
def connect_db():
    return mysql.connector.connect(**db_config)

# Function to create a Kafka topic for Agents
def create_kafka_topic(topic_name, num_partitions=1, replication_factor=1):
    start_time_create_kafka = time.time()
    """Creates a Kafka topic using Confluent Kafka AdminClient"""
    topic_list = [NewTopic(topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
    fs = admin_client.create_topics(topic_list)
    
    for topic, f in fs.items():
        try:
            f.result()  # Block until topic creation is done
            print(f"Kafka topic '{topic}' created successfully.")
        except Exception as e:
            print(f"Failed to create topic '{topic}': {e}")
    end_time_create_kafka = time.time()
    total_time_create_kafka = end_time_create_kafka - start_time_create_kafka
    print()
    print(f"It took {total_time_create_kafka:.2f} seconds to create the Kafka topic name.")
    print()

#Generate random string for Kafka Topic name (NEW - Niki)
def generate_random_string(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Function to send a Kafka message
def send_kafka_message(topic, message):
    start_time_message = time.time()
    """Sends a message to a Kafka topic"""
    try:
        producer.produce(topic, json.dumps(message))
        producer.flush()
        print(f"Message sent to Kafka topic '{topic}': {message}")
    except Exception as e:
        print(f"Failed to send message to Kafka topic '{topic}': {e}")
    end_time_message = time.time()
    total_time_message = end_time_message - start_time_message
    print()
    print(f"It took {total_time_message:.2f} seconds to send the message.")
    print()

# Function to generate DID:key using CLI tool (modified)
def generate_did_key():
    start_time_gen_key = time.time()
    """Runs the CLI tool to generate a unique DID:key and extract the private key"""
    while True:
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
        
        # Check if the generated swid already exists in the database
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM did_keys WHERE did = %s", (did_key,))
        if cursor.fetchone()[0] == 0:  # SWID is unique
            # Return DID:key and private key as a PEM string
            return did_key, private_key.decode("utf-8")  # Decode private key bytes to string
        end_time_gen_key = time.time()
        total_time_gen_key = end_time_gen_key - start_time_gen_key
        print()
        print(f"It took {total_time_gen_key:.2f} seconds to generate a key.")
        print()

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
        start_time_auth = time.time()
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
        end_time_auth = time.time()
        total_time_auth = end_time_auth - start_time_auth
        print()
        print(f"It took {total_time_auth:.2f} seconds to authenticate.")
        print()
        print(f"Welcome {user_data.get('name')}, you can now register your new Entity.")
        return user_did
    else:
        print("Invalid choice.")
        return None

# Function to validate JSON and register entity
def register_entity(json_file_path, output_directory, registered_by=None):
    start_time_register = time.time()
    start_time_register1 = time.time()
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
    end_time_register1 = time.time()
    total_time_register1 = end_time_register1 - start_time_register1
    print()
    print(f"It took {total_time_register1:.2f} seconds to accept the HSML JSON file.")
    print()
    print("HSML JSON accepted.")
    
    # Check for required fields based on type
    entity_type = data.get("@type")
    required_fields = {
        "Entity": ["name", "description"],
        "Person": ["name", "birthDate", "email"],
        "Agent": ["name", "creator", "dateCreated", "dateModified", "description"],
        "Credential": ["name", "description", "issuedBy", "accessAuthorization", "authorizedForDomain"],
        "Organization": ["name", "description", "url","address", "foundingDate", "email"]
    }
    start_time_register2 = time.time()
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
    end_time_register2 = time.time()
    total_time_register2 = end_time_register2 - start_time_register2
    print()
    print(f"It took {total_time_register2:.2f} seconds to generate warning for registration/check required fields.")
    print() 

    # Check if SWID exists in the JSON
    swid = data.get("swid")
    
    if swid:
        start_time_register3 = time.time()
        # Check if this swid is already registered
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM did_keys WHERE did = %s", (swid,))
        existing = cursor.fetchone()[0]

        if existing:
            print(f"Warning: The provided 'swid' ({swid}) already exists in the database. You should not register an already existing object.")
            user_input = input("Do you want to continue and overwrite the existing 'swid' property? (yes/no): ").strip().lower()

            if user_input != "yes":
                print("Process aborted. No changes were made.")
                exit()
        end_time_register3 = time.time()
        total_time_register3 = end_time_register3 - start_time_register3
        print()
        print(f"It took {total_time_register3:.2f} seconds to check if swid already exists.")
        print()
        print(f"Warning: SWID '{swid}' in JSON file will be overwritten.")
        print()

    # No SWID in JSON, generate a unique one. Generate a new DID:key and private key
    did_key, private_key = generate_did_key()
    data["swid"] = did_key # Attach new DID:key to swid
    print(f"Generated unique SWID: {did_key}")
    public_key_part = did_key.replace("did:key:", "") # Only leaves the public key part
        
    # Connect to DB
    db = connect_db()
    cursor = db.cursor()

    # If what is being registered is a Person/Organization for the first time (when no existing user_did)
    if registered_by is None:
        registered_by = did_key

    topic_name = None

    # Special case: If entity is an "Agent", create a Kafka topic
    if entity_type == "Agent":
        flagUniqueName = False
        while flagUniqueName == False:
            random_suffix = generate_random_string() # new
            topic_name = f"{data["name"].replace(" ", "_").lower()}_{random_suffix}" # new
            #topic_name = data["name"].replace(" ", "_").lower()
            # Check the name generated does not already exist
            cursor.execute("SELECT COUNT(*) FROM did_keys WHERE kafka_topic = %s", (topic_name,))
            existing_topic = cursor.fetchone()
            if existing_topic[0]==0:
                flagUniqueName = True
                create_kafka_topic(topic_name)
                send_kafka_message(topic_name, {"message": f"New Agent registered: {data['name']}"})


    # Special case: If entity is a "Credential", more checks needed
    if entity_type == "Credential":
        issued_by_did = data.get("issuedBy", {}).get("swid") # SWID of user registering Credential
        authorized_for_domain_did = data.get("authorizedForDomain", {}).get("swid") # SWID of Domain that Credential is giving access to
        credential_domain_name = data.get("authorizedForDomain", {}).get("name") # Name of Domain that Credential is giving access to
        access_authorization_did = data.get("accessAuthorization",{}).get("swid") # SWID of new Domain/Person/Organization that Credential is granting access authorization
        #access_authorization_type = data.get("accessAuthorization",{}).get("@type") # Type of new Domain/Person/Organization that Credential is granting access authorization
        #access_authorization_name = data.get("accessAuthorization",{}).get("name") # Name of new Domain/Person/Organization that Credential is granting access authorization

        if not (issued_by_did and authorized_for_domain_did and access_authorization_did):
            raise ValueError("Missing required 'swid' in Credential fields")

        # Ensure issuedBy matches the logged in User's swid registering the Credential
        if issued_by_did != registered_by:
            raise ValueError("issuedBy field must match the User registering the Credential")

        # Verify authorizedForDomain ownership 
        private_key_path_credential_domain = input(f"Provide your private_key.pem path for '{credential_domain_name}' this Credential is giving access to: ")
        credential_domain_did = extract_did_from_private_key(private_key_path_credential_domain)
        
        if credential_domain_did != authorized_for_domain_did:
            print(f"Invalid private_key.pem for '{credential_domain_name}'")
            return None
        
        cursor.execute("SELECT metadata FROM did_keys WHERE did = %s", (authorized_for_domain_did,))
        domain_did_result = cursor.fetchone()
        if not domain_did_result:
            print(f"DID not found in database. Please register '{credential_domain_name}' first.")
            return None

        # Update authorizedForDomain's metadata to include the new accessAuthorization swid in "canAccess"
        domain_data = json.loads(domain_did_result[0])
        new_access_auth = data.get("accessAuthorization", {})
        if "canAccess" not in domain_data:
            # Write canAccess property
            domain_data["canAccess"] = [new_access_auth]
            
        else:
            # Attach to the existing canAccess property and existing allowed_did (fetch and merge)
            existing_can_access = domain_data.get("canAccess", [])
            
            # Ensure it's a list (sometimes it could be a single dict mistakenly)
            if not isinstance(existing_can_access, list):
                existing_can_access = [existing_can_access]
            
            # Extract existing swids to prevent duplicates
            existing_swids = {entry["swid"] for entry in existing_can_access if "swid" in entry}

            if new_access_auth.get("swid") and new_access_auth["swid"] not in existing_swids:
                existing_can_access.append(new_access_auth)
            else:
                print(f"{new_access_auth["swid"]} arlready has access to '{credential_domain_name}'")
            
            # Update the JSON structure with the merged list
            domain_data["canAccess"] = existing_can_access
        
        # Update Domain metadata JSON in DB and save in location
            cursor.execute("UPDATE did_keys SET metadata = %s WHERE did = %s", (json.dumps(domain_data), authorized_for_domain_did))
            domain_json_output = os.path.join(output_directory, f"{domain_data['name'].replace(' ', '_')}.json")
            with open(domain_json_output, "w") as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Updated {credential_domain_name} JSON saved to: {domain_json_output}")
            
        # Now to dump into allowed_did
        # Fetch the existing allowed_did list from the database
        cursor.execute("SELECT allowed_did FROM did_keys WHERE did = %s", (authorized_for_domain_did,))
        allowed_did_result = cursor.fetchone()

        # Convert the existing allowed_did value into a list (splitting by comma)
        if allowed_did_result and allowed_did_result[0]:
            allowed_did_list = allowed_did_result[0].split(",")  # Stored as comma-separated values
        else:
            allowed_did_list = []  # Initialize as empty list if nothing exists

        # Add the new DID if it's not already present
        new_did = new_access_auth.get("swid")
        if new_did and new_did not in allowed_did_list:
            allowed_did_list.append(new_did)

        # Convert the list back into a comma-separated string for database storage
        allowed_did_string = ",".join(allowed_did_list)

        # Update the database with the modified allowed_did list
        cursor.execute("UPDATE did_keys SET allowed_did = %s WHERE did = %s", 
                    (allowed_did_string, authorized_for_domain_did))

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

    end_time_register = time.time()
    total_time_register = end_time_register - start_time_register
    print()
    print(f"It took {total_time_register:.2f} seconds to register.")
    print()
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
    #json_file_path = "C:/Users/nnamian/OneDrive - JPL/Desktop/Digital Twin Interoperability/Codes/HSML Examples/Examples 2025-02-03/entityExample/entityExample.json"  # Provide your JSON file
    if user_did is not None:
        json_file_path = input("Enter the directory to your HSML JSON to be registered: ")
        #output_directory = input("Enter the directory to save the private key and updated JSON: ")
        output_directory = "C:/Users/nnamian/OneDrive - JPL/Desktop/Digital Twin Interoperability/Codes/HSML Examples/registeredExamples"

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

        output_directory = "C:/Users/nnamian/OneDrive - JPL/Desktop/Digital Twin Interoperability/Codes/HSML Examples/registeredExamples"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        result = register_entity(json_file_path, output_directory, registered_by=None)
        print(result)

