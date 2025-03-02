# Script Path Planning

This script is designed to keep track of the movements of the rover while manually driving. It allows users to store multiple waypoints by pressing the **W** key during navigation. Pressing **S** will save the collected waypoints into a JSON file.

### **How It Works:**
- **W Key**: Adds the current rover position as a waypoint.
- **S Key**: Saves the stored waypoints into a JSON file.
- Once a successful manual drive is completed, these stored waypoints can be used for path planning.
- The autonomous script will later use these saved waypoints to follow the planned path.

### **Future Development:**
- Implement autonomous movement based on stored waypoints.
- Fine-tune path following behavior using Unity's physics engine (PhysX).
