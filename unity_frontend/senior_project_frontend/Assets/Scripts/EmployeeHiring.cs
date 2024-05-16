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
        public string name;
        public float salary;
        public float morale;
        public string[] tags;

        public static EmployeePacket CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<EmployeePacket>(jsonString);
        }
    }

    public UIListScript employeeList;

    // Start is called before the first frame update
    void Start()
    {
        employeeList.document.rootVisualElement.Q<Button>("HireButton").clickable.clicked += AttemptToHire;
    }

    void AttemptToHire()
    {
        string url = HttpManager.EndpointToUrl("/employees", HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.PostRequest(new { }, url, WeGotAnEmployee));
    }

    void WeGotAnEmployee(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        EmployeePacket employee = EmployeePacket.CreateFromJson(text);
        UIListScript.ItemData data = new UIListScript.ItemData { name= employee.name, salary= employee.salary, morale = employee.morale};
        employeeList.AddItem(data);
    }
    // Update is called once per frame
    void Update()
    {
    }
}
