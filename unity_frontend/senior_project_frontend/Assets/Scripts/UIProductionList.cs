using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
using System;


public class UIProductionList : MonoBehaviour
{
    public UIDocument document; // Assign this in the inspector
    public VisualTreeAsset itemTemplate; // Assign the UXML file in the inspector

    private ListView activesList;
    private List<ActiveRecipe> items;


    [Serializable]
    public class ActiveRecipe 
    {
        public string item;
        public int amount;
        public string employee;
        public bool is_ready;
        public int id;

        public static ActiveRecipe CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<ActiveRecipe>(jsonString);
        }
    }

    [Serializable]
    public class ActiveRecipeList 
    {
        public ActiveRecipe[] active_recipes;
        public static ActiveRecipeList CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<ActiveRecipeList>(jsonString);
        }
    }

    void RefreshActiveRecipes()
    {
        if (!GameInstanceScript.hasCompanyId)
        {
            return;
        }
        string url = HttpManager.EndpointToUrl("/recipes/active_recipes/" + GameInstanceScript.companyId, HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.SendRequest(type: "Get", new { }, url, RefreshActiveRecipesSuccess));
    }

    void RefreshActiveRecipesSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        ActiveRecipeList activeRecipesListPacket = ActiveRecipeList.CreateFromJson(text);
        List<ActiveRecipe> itemDatas = new();
        for (int i = 0; i < activeRecipesListPacket.active_recipes.Length; i++)
        {
            itemDatas.Add(activeRecipesListPacket.active_recipes[i]) ;
        }
        RefreshItems(itemDatas);
    }


    void Start()
    {
        var rootVisualElement = document.rootVisualElement;

        // Find the ListView by name or class
        activesList = rootVisualElement.Q<ListView>("ActiveRecipesList");

        // Prepare some initial items data
        items = new List<ActiveRecipe> { };

        // Set up ListView's makeItem and bindItem to use the custom UXML
        activesList.makeItem = () => itemTemplate.Instantiate();

        activesList.bindItem = (element, i) => {
            var itemData = items[i];
            element.Q<TextField>("ItemField").value = itemData.item;
            element.Q<IntegerField>("AmountField").value = itemData.amount;
            element.Q<TextField>("EmployeeField").value = itemData.employee;
            element.Q<IntegerField>("IdField").value = itemData.id;
            element.Q<Toggle>("IsReadyToggle").value = itemData.is_ready;
            if (itemData.is_ready)
            {
                element.Q<Button>("CompleteButton").clickable.clicked += ()=> AttemptCompleteRecipe(itemData.id);
            }
        };

        activesList.itemsSource = items;
        activesList.selectionType = SelectionType.Single;
        rootVisualElement.Q<VisualElement>("Production").Q<Button>("RefreshButton").clickable.clicked += RefreshActiveRecipes;
    }

    private void AttemptCompleteRecipe(int recipeId)
    {
        string url = HttpManager.EndpointToUrl("/recipes/complete_recipe/" + recipeId, HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.SendRequest(type: "POST", new { }, url, CompleteRecipeSuccess));
    }
    void CompleteRecipeSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        RefreshActiveRecipes();
    }


    public void RefreshItems(List<ActiveRecipe> newItems)
    {
        items = newItems;
        activesList.itemsSource = items;
        activesList.Rebuild();
    }

    public int Count { get { return items.Count; } }


}
