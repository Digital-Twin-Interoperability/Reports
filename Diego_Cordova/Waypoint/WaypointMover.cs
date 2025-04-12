using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WaypointMover : MonoBehaviour
{
    [SerializeField] private Waypoints waypoints;
    [SerializeField] private float moveSpeed = 2f;
    [SerializeField] private float distance = 1f;
    [SerializeField] private float rotateSpeed = 1f;

    private Transform currentWaypoint;  


    // the rotation target for the current frame
    private Quaternion rotationGoal;
    // trhe direction to the next waypoint we need to roatet to 
    private Vector3 directionToWaypoint;


    void Start()
    {
        currentWaypoint = waypoints.GetNextWaypoint(currentWaypoint);
    }



    void Update()
    {
        transform.position = Vector3.MoveTowards(transform.position, currentWaypoint.position, moveSpeed * Time.deltaTime);
        if(Vector3.Distance(transform.position,currentWaypoint.position) < distance)
        {
            currentWaypoint = waypoints.GetNextWaypoint(currentWaypoint);
        }
        RotateTowardsWaypoint();    
    }


    //will rotate the object to face the next waypoint
    private void RotateTowardsWaypoint()
    {
        directionToWaypoint = (currentWaypoint.position - transform.position).normalized;
        rotationGoal = Quaternion.LookRotation(directionToWaypoint);
        transform.rotation = Quaternion.Slerp(transform.rotation, rotationGoal, rotateSpeed * Time.deltaTime);
    }


}
