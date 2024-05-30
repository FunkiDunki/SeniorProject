using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

public class UIListScript : MonoBehaviour
{
   
    public UIDocument document; // Assign this in the inspector
    public VisualTreeAsset itemTemplate; // Assign the UXML file in the inspector

    private ListView employeesList;
    private System.Collections.Generic.List<ItemData> items;

    void Start()
    {
        var rootVisualElement = document.rootVisualElement;

        // Find the ListView by name or class
        employeesList = rootVisualElement.Q<ListView>("EmployeeList");

        // Prepare some initial items data
        items = new System.Collections.Generic.List<ItemData> { };

        // Set up ListView's makeItem and bindItem to use the custom UXML
        employeesList.makeItem = () => itemTemplate.Instantiate();

        employeesList.bindItem = (element, i) => {
            var itemData = items[i];
            element.Q<IntegerField>("IdField").value = itemData.id;
            element.Q<Label>("Name").text = itemData.name;
            element.Q<FloatField>("SalaryField").value = itemData.salary;
            element.Q<FloatField>("MoraleField").value = itemData.morale;
            Button removeButton = element.Q<Button>("FireButton");
            removeButton.clickable.clicked += () => RemoveItem(i);
        };

        employeesList.itemsSource = items;
        employeesList.selectionType = SelectionType.Single;
    }

    public class ItemData
    {
        public int id { get; set; }
        public string name { get; set; }
        public float salary { get; set; }
        public float morale { get; set; }
    }

    public void AddItem(ItemData newItem)
    {
        items.Add(newItem);
        employeesList.Rebuild();
    }

    public void RefreshItems(List<ItemData> newItems)
    {
        items = newItems;
        employeesList.itemsSource = items;
        employeesList.Rebuild();
    }

    void RemoveItem(int index)
    {
        if (index >= 0 && index < items.Count)
        {
            items.RemoveAt(index);
            employeesList.Rebuild();
        }
    }

    public int Count { get { return items.Count; } }
}
