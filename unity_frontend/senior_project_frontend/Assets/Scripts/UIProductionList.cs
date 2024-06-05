using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
using System;


public class UIProductionList : MonoBehaviour
{
    public UIDocument document; // Assign this in the inspector
    public VisualTreeAsset activeRecipeItemTemplate; // Assign the UXML file in the inspector
    public VisualTreeAsset availableRecipeItemTemplate; // Assign the UXML file in the inspector
    public VisualTreeAsset itemCostTemplate;

    private ListView activesList;
    private List<ActiveRecipe> items;

    private ListView availList;
    private List<AvailableRecipe> availItems;

     private ListView costList;
    private List<UIInventory.Item> costItems;


    [Serializable]
    public class AvailableRecipe
    {
        public int recipe_id;
        public int out_item_id;
        public string out_item_name;
        public int out_item_quantity;

        public static AvailableRecipe CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<AvailableRecipe>(jsonString);
        }
    }

    [Serializable]
    public class AvailableRecipeList 
    {
        public AvailableRecipe[] available_recipes;
        public static AvailableRecipeList CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<AvailableRecipeList>(jsonString);
        }
    }
    void RefreshAvailableRecipes()
    {
        if (!GameInstanceScript.hasCompanyId)
        {
            return;
        }
        string url = HttpManager.EndpointToUrl("/recipes/available_recipes/" + GameInstanceScript.companyId, HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.SendRequest(type: "Get", new { }, url, RefreshAvailableRecipesSuccess));
    }

    void RefreshAvailableRecipesSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        AvailableRecipeList activeRecipesListPacket = AvailableRecipeList.CreateFromJson(text);
        List<AvailableRecipe> itemDatas = new();
        for (int i = 0; i < activeRecipesListPacket.available_recipes.Length; i++)
        {
            itemDatas.Add(activeRecipesListPacket.available_recipes[i]) ;
        }
        RefreshAvailableItems(itemDatas);
    }

    private void RefreshAvailableItems(List<AvailableRecipe> newItems)
    {
        availItems = newItems;
        availList.itemsSource = availItems;
        availList.Rebuild();
    }


//----------------------------start cost section
   
        void RefreshCost()
    {
        VisualElement startSection = document.rootVisualElement.Q<VisualElement>("RecipeCost");
        int rec_id = startSection.Q<IntegerField>("RecipeIdField").value;

        string url = HttpManager.EndpointToUrl("/recipes/recipe_cost/" + rec_id, HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.SendRequest(type: "Get", new { }, url, RefreshCostSuccess));
    }

    void RefreshCostSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        UIInventory.Inventory costsPacket = UIInventory.Inventory.CreateFromJson(text);
        List<UIInventory.Item> itemDatas = new();
        for (int i = 0; i < costsPacket.items.Length; i++)
        {
            itemDatas.Add(costsPacket.items[i]) ;
        }
        RefreshCostItems(itemDatas);
    }

    private void RefreshCostItems(List<UIInventory.Item> newItems)
    {
        costItems = newItems;
        costList.itemsSource = costItems;
        costList.Rebuild();
    }

//--------------------------------------------------end

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
        activesList.makeItem = () => activeRecipeItemTemplate.Instantiate();

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
        rootVisualElement.Q<VisualElement>("ActiveRecipes").Q<Button>("RefreshButton").clickable.clicked += RefreshActiveRecipes;
        rootVisualElement.Q<VisualElement>("StartRecipeSection").Q<Button>("StartRecipeButton").clickable.clicked += AttemptStartRecipe;


        //----------------- available recipes
        // Find the ListView by name or class
        availList = rootVisualElement.Q<ListView>("AvailableRecipesList");

        // Prepare some initial items data
        availItems = new List<AvailableRecipe> { };

        // Set up ListView's makeItem and bindItem to use the custom UXML
        availList.makeItem = () => availableRecipeItemTemplate.Instantiate();

        availList.bindItem = (element, i) => {
            var itemData = availItems[i];
            element.Q<IntegerField>("RecipeIdField").value = itemData.recipe_id;
            element.Q<IntegerField>("ItemIdField").value = itemData.out_item_id;
            element.Q<TextField>("ItemNameField").value = itemData.out_item_name;
            element.Q<IntegerField>("AmountField").value = itemData.out_item_quantity;
        };

        availList.itemsSource = items;
        availList.selectionType = SelectionType.Single;
        rootVisualElement.Q<VisualElement>("AvailableRecipes").Q<Button>("RefreshButton").clickable.clicked += RefreshAvailableRecipes;
        //-------------------
        //--------------------------------cost
        costList= rootVisualElement.Q<ListView>("RecipeCostList");

        // Prepare some initial items data
        costItems= new List<UIInventory.Item> { };

        // Set up ListView's makeItem and bindItem to use the custom UXML
        costList.makeItem = () => itemCostTemplate.Instantiate();

        costList.bindItem = (element, i) => {
            var itemData = costItems[i];
            element.Q<TextField>("NameField").value = itemData.name;
            element.Q<IntegerField>("IdField").value = itemData.id;
            element.Q<IntegerField>("AmountField").value = itemData.amount;
        };

        costList.itemsSource = items;
        costList.selectionType = SelectionType.Single;
        rootVisualElement.Q<VisualElement>("RecipeCost").Q<Button>("RefreshButton").clickable.clicked += RefreshCost;

        //---------------------end
    }

    [Serializable]
    public class RecipeData
    {
        public int recipe_id;
        public int employee_id;
    }

    private void AttemptStartRecipe()
    {
        if (!GameInstanceScript.hasCompanyId)
        {
            return;
        }
        string url = HttpManager.EndpointToUrl("/recipes/create_recipe", HttpManager.manager.host, HttpManager.manager.port);
        VisualElement startSection = document.rootVisualElement.Q<VisualElement>("StartRecipeSection");
        int rec_id = startSection.Q<IntegerField>("RecipeIdField").value;
        int employee_id = startSection.Q<IntegerField>("EmployeeIdField").value;

        StartCoroutine(HttpManager.SendRequest(type: "POST", new RecipeData { recipe_id=rec_id, employee_id=employee_id}, url, StartRecipeSuccess));

    }
    void StartRecipeSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        RefreshActiveRecipes();
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
