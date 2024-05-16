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

    [Serializable]
    public class EmployeeListPacket
    {
        public EmployeePacket[] employeePackets;
        public static EmployeeListPacket CreateFromJson(string jsonString)
        {
            string fixedJson = "{\"employeePackets\":" + jsonString + "}";
            return JsonUtility.FromJson<EmployeeListPacket>(fixedJson);
        }
    }

    public UIListScript employeeList;

    // Start is called before the first frame update
    void Start()
    {
        employeeList.document.rootVisualElement.Q<Button>("HireButton").clickable.clicked += AttemptToHire;
        employeeList.document.rootVisualElement.Q<Button>("RefreshButton").clickable.clicked += RefreshEmployees;
    }

    void RefreshEmployees()
    {
        if (!GameInstanceScript.hasInstance)
        {
            return;
        }
        string url = HttpManager.EndpointToUrl("/employees/" + GameInstanceScript.instanceId, HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.SendRequest(type: "Get", new { }, url, RefreshSuccess));
    }

    void RefreshSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        EmployeeListPacket employeeListPacket = EmployeeListPacket.CreateFromJson(text);
        List<UIListScript.ItemData> itemDatas = new List<UIListScript.ItemData>();
        for (int i = 0; i < employeeListPacket.employeePackets.Length; i++)
        {
            itemDatas.Add(new UIListScript.ItemData
            {
                name = employeeListPacket.employeePackets[i].name,
                salary = employeeListPacket.employeePackets[i].salary,
                morale = employeeListPacket.employeePackets[i].morale
            });
        }
        employeeList.RefreshItems(itemDatas);
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
