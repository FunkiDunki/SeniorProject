using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using UnityEngine.UIElements;

public class GameInstanceScript : MonoBehaviour
{
    public static bool hasInstance;
    public static int instanceId;
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

     public UIDocument document; // Assign this in the inspector

    private VisualElement gameInstanceSegment;





    // Start is called before the first frame update
    void Start()
    {
        hasInstance = false;
        gameInstanceSegment = document.rootVisualElement.Q<VisualElement>("GameInstance");
        gameInstanceSegment.Q<Button>("NewInstanceButton").clickable.clicked += AttemptInstance;
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
    }
}
