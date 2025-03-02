using UnityEngine;
using System.Collections.Generic;
using System.IO;

public class RoverWaypointRecorder : MonoBehaviour
{
    // List to store waypoints
    private List<Waypoint> waypoints = new List<Waypoint>();

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.W)) // W to record waypoints
        {
            RecordWaypoint();
        }

        if (Input.GetKeyDown(KeyCode.S))  // S to save waypoints
        {
            SaveWaypointsToFile();
        }

        if (Input.GetKeyDown(KeyCode.L))  // L to load waypoints
        {
            LoadWaypointsFromFile();
        }
    }

    void RecordWaypoint()
    {
        Waypoint waypoint = new Waypoint
        {
            x = transform.position.x,
            y = transform.position.y,
            z = transform.position.z,
            status = "success",
            timestamp = System.DateTime.Now.ToString("yyyy-MM-ddTHH:mm:ss")
        };

        waypoints.Add(waypoint);
        Debug.Log("Waypoint recorded: " + transform.position);
        Debug.Log("Waypoint recorded: " + "X: " + waypoint.x + " Y: " + waypoint.y + " Z: " + waypoint.z + " Status: " + waypoint.status + " Timestamp: " + waypoint.timestamp);
    }

    void SaveWaypointsToFile()
    {
        WaypointData data = new WaypointData();
        data.waypoints = waypoints;

        string json = JsonUtility.ToJson(data, true);
        File.WriteAllText("waypoints.json", json);
        Debug.Log("Waypoints saved to file.");
    }

    void LoadWaypointsFromFile()
    {
        if (File.Exists("waypoints.json"))
        {
            string json = File.ReadAllText("waypoints.json");
            WaypointData data = JsonUtility.FromJson<WaypointData>(json);
            waypoints = data.waypoints;
            Debug.Log("Waypoints loaded from file.");
        }
        else
        {
            Debug.LogError("No waypoints file found!");
        }
    }

    private void OnDrawGizmos()
    {
        if (waypoints.Count == 0) return;

        Gizmos.color = Color.red;
        // Draw a line connecting the waypoints
        for (int i = 0; i < waypoints.Count - 1; i++)
        {
            Gizmos.DrawLine(new Vector3(waypoints[i].x, waypoints[i].y, waypoints[i].z),
                            new Vector3(waypoints[i + 1].x, waypoints[i + 1].y, waypoints[i + 1].z));
        }

        // Draw spheres at each waypoint position
        foreach (Waypoint wp in waypoints)
        {
            Gizmos.DrawSphere(new Vector3(wp.x, wp.y, wp.z), 0.1f);
        }
    }
}

// The Waypoint class is used as a data container for waypoint information
[System.Serializable]
public class Waypoint
{
    public float x, y, z;  // Position coordinates
    public string status;  // Status (e.g., success or failure)
    public string timestamp;  // Timestamp of when the waypoint was recorded
}

// The WaypointData class is used to hold a list of waypoints
[System.Serializable]
public class WaypointData
{
    public List<Waypoint> waypoints = new List<Waypoint>();
}
