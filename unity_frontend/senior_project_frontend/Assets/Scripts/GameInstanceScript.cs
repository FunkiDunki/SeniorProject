using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using UnityEngine.UIElements;

public class GameInstanceScript : MonoBehaviour
{
    public static bool hasInstance;
    public static int instanceId;
    public static int companyId;
    public static bool hasCompanyId;

    [SerializeField]
    Sprite onlineSprite;
    [SerializeField]
    Sprite offlineSprite;

    [Serializable]
    public class GameInstancePacket
    {
        public int game_instance_id;
        public string name;

        public static GameInstancePacket CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<GameInstancePacket>(jsonString);
        }
    }

    public class CompanyInfoPacket
    {
        public int id;
        public string name;
        public int value;

        public static CompanyInfoPacket CreateFromJson(string jsonString)
        {
            return JsonUtility.FromJson<CompanyInfoPacket>(jsonString);
        }
    }

     public UIDocument document; // Assign this in the inspector

    private VisualElement gameInstanceSegment;





    // Start is called before the first frame update
    void Start()
    {
        hasInstance = false;
        hasCompanyId = false;
        gameInstanceSegment = document.rootVisualElement.Q<VisualElement>("GameInstance");
        gameInstanceSegment.Q<Button>("NewInstanceButton").clickable.clicked += AttemptInstance;
        gameInstanceSegment.Q<VisualElement>("ConnectionIndicator").style.backgroundImage = new StyleBackground(offlineSprite);
        gameInstanceSegment.Q<Button>("JoinInstanceButton").clickable.clicked += SetGameId;
        gameInstanceSegment.Q<Button>("NewCompanyButton").clickable.clicked += AttemptNewCompany;
        gameInstanceSegment.Q<Button>("JoinCompanyButton").clickable.clicked += SetCompanyId;
    }

    private void SetCompanyId()
    {
        if (hasCompanyId)
        {
            return;
        }
        companyId = gameInstanceSegment.Q<IntegerField>("CompanyId").value;
        hasCompanyId = true;
    }

    struct CompanyCreationStruct
    {
        public string name;
    }

    private void AttemptNewCompany()
    {
        
        if (hasCompanyId || !hasInstance)
        {
            return;
        }
        string companyName = gameInstanceSegment.Q<TextField>("CompanyNameField").value;
        string url = HttpManager.EndpointToUrl("/companies/" + instanceId, HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.PostRequest(new CompanyCreationStruct(){ name = companyName}, url, CompanyCreationSuccess));


    }
    void CompanyCreationSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        CompanyInfoPacket inst = CompanyInfoPacket.CreateFromJson(text);
        gameInstanceSegment.Q<IntegerField>("CompanyId").value = inst.id;
        hasCompanyId = true;
        companyId = inst.id;
        gameInstanceSegment.Q<VisualElement>("ConnectionIndicator").style.backgroundImage = new StyleBackground(onlineSprite);
    }
    private void SetGameId()
    {
        if (hasInstance)
        {
            return;
        }
        hasInstance = true;
        instanceId = gameInstanceSegment.Q<IntegerField>("GameId").value;
    }

    void AttemptInstance()
    {
        if (hasInstance)
        {
            //we don't want to get a new instance. Quit man
            return;
        }
        string gamename = gameInstanceSegment.Q<TextField>("GameNameField").value;
        string url = HttpManager.EndpointToUrl("/game/" + gamename, HttpManager.manager.host, HttpManager.manager.port);
        StartCoroutine(HttpManager.PostRequest(new { }, url, GameInstanceCreationSuccess));
    }

    void GameInstanceCreationSuccess(string text)
    {
        print(text);
        HttpManager.manager.CubeIt(text);
        GameInstancePacket inst = GameInstancePacket.CreateFromJson(text);
        gameInstanceSegment.Q<IntegerField>("GameId").value = inst.game_instance_id;
        hasInstance = true;
        instanceId = inst.game_instance_id;
        gameInstanceSegment.Q<VisualElement>("ConnectionIndicator").style.backgroundImage = new StyleBackground(onlineSprite);
    }
}
