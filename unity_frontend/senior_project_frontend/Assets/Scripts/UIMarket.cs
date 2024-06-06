using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
using System;

public class UIMarket : MonoBehaviour
{

    public UIDocument document;
    private VisualElement marketTab;

    [Serializable]
    public class item_sale
    {
        public int item_id;
        public int item_amount;
    }
    // Start is called before the first frame update
    void Start()
    {
        marketTab = document.rootVisualElement.Q<VisualElement>("Market");

        marketTab.Q<Button>("SellButton").clickable.clicked += AttemptSellItems;
        marketTab.Q<Button>("CheckPriceButton").clickable.clicked += AttemptPriceCheck;
    }

    private void AttemptPriceCheck()
    {
        int item_id = marketTab.Q<IntegerField>("ItemIdField").value;
        string url = HttpManager.EndpointToUrl("/market/" + item_id, HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.SendRequest(type: "GET", new {}, url, PriceCheckSuccess));
    }

    [Serializable]
    public class PriceReturnItem
    {
        public int price;
    }

    void PriceCheckSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        PriceReturnItem price = JsonUtility.FromJson<PriceReturnItem>(text);
        marketTab.Q<IntegerField>("PriceField").value = price.price;
    }

    private void AttemptSellItems()
    {
        if (!GameInstanceScript.hasCompanyId)
        {
            return;
        }
        string url = HttpManager.EndpointToUrl("/market/" + GameInstanceScript.companyId, HttpManager.manager.host, HttpManager.manager.port);
        int item_id= marketTab.Q<IntegerField>("ItemIdField").value;
        int item_amount= marketTab.Q<IntegerField>("ItemAmountField").value;

        StartCoroutine(HttpManager.SendRequest(type: "POST", new item_sale{ item_id=item_id, item_amount=item_amount}, url, SellItemsSuccess));

    }
    void SellItemsSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
    }

}
