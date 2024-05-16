using UnityEngine;
using UnityEngine.Networking;
using System.Text;
using System.Collections;
using System.Diagnostics;
using System;
using TMPro;

public class HttpManager : MonoBehaviour
{
    public TMP_Text cubetext;
    public Animator cubeAnimator;

    public string host;
    public int port;

    public static HttpManager manager;

    [Serializable]
    public class ExamplePacket
    {
        public int age;
        public string name;
        public string[] tags;

        public static ExamplePacket CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<ExamplePacket>(jsonString);
        }
    }

    private void Awake()
    {
        if (manager == null)
        {
            manager = this;
        }
        else
        {
            Destroy(this);
        }
    }
    // Start is called before the first frame update
    void Start()
    {

    }
    
    public static string EndpointToUrl(string endpoint, string host, int port)
    {
        return "http://" + host + ":" + port + endpoint;
    }

    public void CubeIt(string wisdom)
    {
        //put the wise words on the cube!
        cubeAnimator.SetTrigger("Speak");
        cubetext.text = wisdom;
    }


    public static IEnumerator PostRequest(object data, string url, Action<string> onSuccess)
    {
        // Convert the data to a JSON string
        string jsonData = JsonUtility.ToJson(data);

        // Convert jsonData to a byte array
        byte[] postData = Encoding.UTF8.GetBytes(jsonData);

        // Create a new UnityWebRequest, setting the URL, method, and body data
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            request.uploadHandler = (UploadHandler)new UploadHandlerRaw(postData);
            request.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            // Wait until the request is done
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
            {
                UnityEngine.Debug.LogError(request.error);
            }
            else
            {
                string text = request.downloadHandler.text;
                onSuccess(text);
            }
        }
    }
}