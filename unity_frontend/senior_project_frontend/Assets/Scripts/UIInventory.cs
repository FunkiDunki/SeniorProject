using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
using System;

public class UIInventory : MonoBehaviour
{
    public UIDocument document; // Assign this in the inspector
    public VisualTreeAsset itemTemplate; // Assign the UXML file in the inspector

    private VisualElement inventoryPanel;
    private ListView inventoryList;
    private List<Item> items;


    [Serializable]
    public class Item
    {
        public string name;
        public int amount;
        public int id;

        public static Item CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<Item>(jsonString);
        }
    }

    [Serializable]
    public class Inventory 
    {
        public Item[] items;
        public static Inventory CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<Inventory>(jsonString);
        }
    }

    void RefreshInventory()
    {
        if (!GameInstanceScript.hasCompanyId)
        {
            return;
        }
        string url = HttpManager.EndpointToUrl("/companies/" + GameInstanceScript.companyId + "/inventory", HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.SendRequest(type: "Get", new { }, url, RefreshInventorySuccess));
    }

    void RefreshInventorySuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        Inventory inventoryPacket = Inventory.CreateFromJson(text);
        List<Item> itemDatas = new();
        for (int i = 0; i < inventoryPacket.items.Length; i++)
        {
            itemDatas.Add(inventoryPacket.items[i]) ;
        }
        RefreshItems(itemDatas);
    }


    void Start()
    {
        inventoryPanel = document.rootVisualElement.Q<VisualElement>("Inventory");

        // Find the ListView by name or class
        inventoryList = inventoryPanel.Q<ListView>("ItemsList");

        // Prepare some initial items data
        items = new List<Item> { };

        // Set up ListView's makeItem and bindItem to use the custom UXML
        inventoryList.makeItem = () => itemTemplate.Instantiate();

        inventoryList.bindItem = (element, i) => {
            var itemData = items[i];
            element.Q<TextField>("NameField").value = itemData.name;
            element.Q<IntegerField>("AmountField").value = itemData.amount;
            element.Q<IntegerField>("IdField").value = itemData.id;
        };

        inventoryList.itemsSource = items;
        inventoryList.selectionType = SelectionType.Single;
        inventoryPanel.Q<Button>("RefreshButton").clickable.clicked += RefreshInventory;
    }

    public void RefreshItems(List<Item> newItems)
    {
        items = newItems;
        inventoryList.itemsSource = items;
        inventoryList.Rebuild();
    }

    public int Count { get { return items.Count; } }


}
