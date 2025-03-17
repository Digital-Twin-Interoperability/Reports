using System;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

[RequireComponent(typeof(Rigidbody))] // ✅ Clearly ensures Rigidbody presence
public class AISocketClient : MonoBehaviour
{
    private TcpClient client;
    private NetworkStream stream;
    private string serverIP = "10.96.145.18"; // ✅ Clearly your Mac's IP
    private int port = 6000;

    private Rigidbody rb; // ✅ clearly to hold reference to Rigidbody

    void Start()
    {
        rb = GetComponent<Rigidbody>(); // ✅ clearly fetch the Rigidbody component

        try
        {
            Debug.Log("🟡 Connecting to AI agent...");
            client = new TcpClient(serverIP, port);
            stream = client.GetStream();

            // ✅ Clearly fetching real-time physics data dynamically:
            string physicsEngine = "Unity3D(Chaos Physics)"; // clearly identifying engine
            float force = rb.velocity.magnitude;    // clearly using velocity as proxy for force
            float friction = rb.drag;               // clearly drag as friction approximation
            float gravity = Physics.gravity.y;      // clearly actual gravity value from Unity

            // ✅ Dynamically creating message from real physics values:
            string physicsMessage = $"PhysicsDetection: name={physicsEngine}; force={force}N; friction={friction};gravity={gravity}";
            physicsMessage = "request_move";
            // Clearly sending this dynamically generated message:
            byte[] data = Encoding.ASCII.GetBytes(physicsMessage);
            stream.Write(data, 0, data.Length);
            Debug.Log("✅ Sent to AI agent: " + physicsMessage);

            byte[] responseData = new byte[1024];
            int bytesRead = stream.Read(responseData, 0, responseData.Length);
            string responseMessage = Encoding.ASCII.GetString(responseData, 0, bytesRead);
            Debug.Log("🟢 AI Agent Response: " + responseMessage);
        }
        catch (Exception e)
        {
            Debug.LogError("🔴 Error connecting to AI agent: " + e.Message);
        }
    }

    // new functions ---------------------------------------------------
    void Update()
    {
        if (stream != null && stream.DataAvailable)
        {
            byte[] responseData = new byte[1024];
            int bytesRead = stream.Read(responseData, 0, responseData.Length);
            string responseMessage = Encoding.ASCII.GetString(responseData, 0, bytesRead);
            Debug.Log("🟢 AI Agent Response: " + responseMessage);

            // Try to parse as movement data, if applicable
            try
            {
                MovementData data = JsonUtility.FromJson<MovementData>(responseMessage);
                if (data == null)
                {
                    Debug.Log("Data object is null after parsing");
                }
                else
                {
                    Debug.Log("Data object is NOT null. Checking data.move...");
                    if(data.move == null)
                    {
                        Debug.Log("Data.move is null.");
                    }
                    else
                    {
                        Debug.Log("data.move is valid! " + data.move.x + ", " + data.move.y + ", " + data.move.z);
                        ApplyMovement(data.move);
                    }

                }
            }
            catch
            {
                Debug.Log("Received non-movement data or invalid JSON.");
            }
        }
    }

    void ApplyMovement(VectorData moveVector)
    {
        // Apply the movement as a force to the Rigidbody
        Vector3 force = new Vector3(moveVector.x, moveVector.y, moveVector.z);
        Debug.Log("Applying movement force: " + force);
        rb.AddForce(force, ForceMode.VelocityChange);
    }

    //---------------------------------------------------------------
    void OnApplicationQuit()
    {
        if (stream != null) stream.Close();
        if (client != null) client.Close();
        Debug.Log("🔵 Connection closed.");
    }

    // new function test -------------------------------------------

    [System.Serializable]
    public class VectorData
    {
        public float x;
        public float y;
        public float z;
    }

    [System.Serializable]
    public class MovementData
    {
        public VectorData move;
    }
    // --------------------------------------------------------------
}
