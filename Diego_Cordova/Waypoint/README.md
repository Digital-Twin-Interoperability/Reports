Waypoints and WaypointMover Setup Guide
This guide details how to configure and use the Waypoints and WaypointMover scripts to have an object follow a series of waypoints in your Unity scene.

1. Set Up the Waypoints
a. Create the Parent Waypoints Object
Create an Empty GameObject:

In the Unity Hierarchy window, right-click and select Create Empty.

Name this GameObject as you like (e.g., WaypointsParent). The name does not affect the functionality.

Attach the Waypoints Script:

With your new parent GameObject selected, go to the Inspector and click Add Component.

Search for and attach the Waypoints script.

Once attached, the script will visualize the waypoints with colored spheres and lines when you add child objects (the debug visuals are drawn in the Scene view via Gizmos).

b. Create Child Waypoint Objects
Create Child Objects:

Under your parent (e.g., WaypointsParent), create as many child GameObjects as there are waypoints you need.

Right-click on the WaypointsParent in the Hierarchy and choose Create Empty Child (or simply drag and drop a new empty GameObject into the parent).

Name each child appropriately (e.g., WP1, WP2, WP3, etc.) to keep your project organized.

Position the Waypoints:

Move each child object (waypoint) to the desired positions in your scene.

When the Waypoints script is active, you should see a blue wireframe sphere on each waypoint, and a red line will connect them in the order they appear as children of the parent.

Verify the Setup:

If you do not see the colored spheres or the connecting line:

Double-check that the child objects are correctly placed under the parent.

Ensure that you have attached the Waypoints script on the parent and that the scene is in Scene view (Gizmos must be enabled).

2. Set Up the Moving Object with WaypointMover
a. Prepare Your Moving Object
Select the Object to Move:

Choose the object in your scene that you want to follow the waypoints.

Ensure Correct Orientation:

The moving object should have the same rotation as Unity’s default orientation.

If the object is tilted:

Create another empty GameObject.

Reset its Transform (right-click the Transform component and select Reset).

Drag your moving object into this empty object as its child.

This new empty object will act as the parent, ensuring the object aligns correctly with Unity’s default axes.

If your object’s rotation is already aligned correctly, you can skip this step.

b. Attach the WaypointMover Script
Attach the Script:

With your moving object (or its correctly oriented parent) selected, add the WaypointMover script via the Inspector.

Configure the Script:

In the WaypointMover Inspector:

Waypoints: Drag your parent GameObject (i.e., the one with the Waypoints script) into the Waypoints field.

Move Speed: Set your desired movement speed.

Distance: Define how close the object must get to a waypoint before it starts moving toward the next one.

3. Running the Simulation
Play the Scene:

Click the Play button in the Unity Editor.

The moving object should follow the path defined by the child waypoints in the order they are arranged.

Observe the Movement:

Watch for any irregularities:

If the moving object tilts or behaves unexpectedly, revisit the orientation step and ensure your moving object is correctly parented and rotated.

Adjust if Necessary:

Tweak the waypoint positions, moveSpeed, or the proximity distance threshold in the Inspector to get the desired motion.
