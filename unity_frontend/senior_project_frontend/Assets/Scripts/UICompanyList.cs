using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
using System;


public class UICompanyList : MonoBehaviour
{
    public UIDocument document; // Assign this in the inspector
    public VisualTreeAsset itemTemplate; // Assign the UXML file in the inspector

    private ListView companiesList;
    private List<ItemData> items;


    [Serializable]
    public class CompanyPacket
    {
        public string name;
        public int value;
        public int id;

        public static CompanyPacket CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<CompanyPacket>(jsonString);
        }
    }

    [Serializable]
    public class CompanyListPacket 
    {
        public CompanyPacket[] companies;
        public static CompanyListPacket CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<CompanyListPacket>(jsonString);
        }
    }

    void RefreshCompanies()
    {
        if (!GameInstanceScript.hasInstance)
        {
            return;
        }
        string url = HttpManager.EndpointToUrl("/game/" + GameInstanceScript.instanceId + "/companies", HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.SendRequest(type: "Get", new { }, url, RefreshSuccess));
    }

    void RefreshSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        CompanyListPacket companyListPacket = CompanyListPacket.CreateFromJson(text);
        List<ItemData> itemDatas = new();
        for (int i = 0; i < companyListPacket.companies.Length; i++)
        {
            itemDatas.Add(new ItemData
            {
                name = companyListPacket.companies[i].name,
                value = companyListPacket.companies[i].value,
                id = companyListPacket.companies[i].id,
            }) ;
        }
        RefreshItems(itemDatas);
    }


    void Start()
    {
        var rootVisualElement = document.rootVisualElement;

        // Find the ListView by name or class
        companiesList = rootVisualElement.Q<ListView>("CompaniesList");

        // Prepare some initial items data
        items = new List<ItemData> { };

        // Set up ListView's makeItem and bindItem to use the custom UXML
        companiesList.makeItem = () => itemTemplate.Instantiate();

        companiesList.bindItem = (element, i) => {
            var itemData = items[i];
            element.Q<Label>("Name").text = itemData.name;
            element.Q<FloatField>("ValueField").value = itemData.value;
            element.Q<IntegerField>("CompanyId").value = itemData.id;
        };

        companiesList.itemsSource = items;
        companiesList.selectionType = SelectionType.Single;
        rootVisualElement.Q<VisualElement>("Competition").Q<Button>("RefreshButton").clickable.clicked += RefreshCompanies;
    }

    public class ItemData
    {
        public string name { get; set; }
        public float value { get; set; }
        public int id { get; set; }
    }

    public void AddItem(ItemData newItem)
    {
        items.Add(newItem);
        companiesList.Rebuild();
    }

    public void RefreshItems(List<ItemData> newItems)
    {
        items = newItems;
        companiesList.itemsSource = items;
        companiesList.Rebuild();
    }

    public int Count { get { return items.Count; } }

}
