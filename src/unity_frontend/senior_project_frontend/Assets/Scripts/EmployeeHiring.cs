using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Runtime.InteropServices;
using System.Reflection;
using UnityEngine.UIElements;

public class EmployeeHiring : MonoBehaviour
{
    [Serializable]
    public class EmployeePacket
    {
        public int age;
        public string name;
        public string[] tags;

        public static EmployeePacket CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<EmployeePacket>(jsonString);
        }
    }

    public HttpManager manager;
    public UIListScript employeeList;

    // Start is called before the first frame update
    void Start()
    {
        employeeList.document.rootVisualElement.Q<Button>("HireButton").clickable.clicked += AttemptToHire;
    }

    void AttemptToHire()
    {
        StartCoroutine(HttpManager.PostRequest(new { }, "http://localhost:11000/hire/alice", WeGotAnEmployee));
    }

    void WeGotAnEmployee(string text)
    {
        print(text);
        manager.CubeIt(text);
        EmployeePacket employee = EmployeePacket.CreateFromJson(text);
        UIListScript.ItemData data = new UIListScript.ItemData { Title = employee.name, age = employee.age };
        employeeList.AddItem(data);
    }
    // Update is called once per frame
    void Update()
    {
        
    }
}
