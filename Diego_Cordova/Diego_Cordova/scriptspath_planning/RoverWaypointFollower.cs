using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

public class RoverWaypointFollower : MonoBehaviour
{
    public float speed = 2f;  // Speed of the rover
    private List<Waypoint> waypoints = new List<Waypoint>();
    private int currentWaypointIndex = 0;
    private bool isMoving = false;

    void Start()
    {
        LoadWaypointsFromFile();
        if (waypoints.Count > 0)
        {
            StartCoroutine(FollowWaypoints());
        }
        else
        {
            Debug.LogError("No waypoints loaded!");
        }
    }

    void LoadWaypointsFromFile()
    {
        if (File.Exists("waypoints.json"))
        {
            string json = File.ReadAllText("waypoints.json");
            WaypointData data = JsonUtility.FromJson<WaypointData>(json);
            waypoints = data.waypoints;
            Debug.Log("Waypoints successfully loaded.");
        }
        else
        {
            Debug.LogError("No waypoints file found!");
        }
    }

    IEnumerator FollowWaypoints()
    {
        isMoving = true;
        while (currentWaypointIndex < waypoints.Count)
        {
            Vector3 targetPosition = new Vector3(waypoints[currentWaypointIndex].x, 
                                                 waypoints[currentWaypointIndex].y, 
                                                 waypoints[currentWaypointIndex].z);
            
            // Move the rover towards the target waypoint smoothly
            while (Vector3.Distance(transform.position, targetPosition) > 0.1f)
            {
                transform.position = Vector3.MoveTowards(transform.position, targetPosition, speed * Time.deltaTime);
                yield return null; // Wait until next frame
            }

            Debug.Log("Reached waypoint: " + (currentWaypointIndex + 1));
            currentWaypointIndex++;
            yield return new WaitForSeconds(0.5f); // Small pause between waypoints
        }

        Debug.Log("Rover has reached all waypoints.");
        isMoving = false;
    }
}
