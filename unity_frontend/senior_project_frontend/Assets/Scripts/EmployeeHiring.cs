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
        public int id;
        public string name;
        public float salary;
        public float morale;

        public static EmployeePacket CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<EmployeePacket>(jsonString);
        }
    }

    [Serializable]
    public class EmployeeListPacket
    {
        public EmployeePacket[] employees;
        public static EmployeeListPacket CreateFromJson(string jsonString)
        {
            string fixedJson = jsonString;
            return JsonUtility.FromJson<EmployeeListPacket>(fixedJson);
        }
    }

    public UIListScript employeeList;

    // Start is called before the first frame update
    void Start()
    {
        employeeList.document.rootVisualElement.Q<Button>("HireButton").clickable.clicked += AttemptToHire;
        employeeList.document.rootVisualElement.Q<VisualElement>("Employees").Q<Button>("RefreshButton").clickable.clicked += RefreshEmployees;
    }

    void RefreshEmployees()
    {
        if (!GameInstanceScript.hasCompanyId)
        {
            return;
        }
        string url = HttpManager.EndpointToUrl("/employees/" + GameInstanceScript.companyId, HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.SendRequest(type: "Get", new { }, url, RefreshSuccess));
    }

    void RefreshSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        EmployeeListPacket employeeListPacket = EmployeeListPacket.CreateFromJson(text);
        List<UIListScript.ItemData> itemDatas = new List<UIListScript.ItemData>();
        for (int i = 0; i < employeeListPacket.employees.Length; i++)
        {
            itemDatas.Add(new UIListScript.ItemData
            {
                id = employeeListPacket.employees[i].id,
                name = employeeListPacket.employees[i].name,
                salary = employeeListPacket.employees[i].salary,
                morale = employeeListPacket.employees[i].morale
            }) ;
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
