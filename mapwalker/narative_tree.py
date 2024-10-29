import json
from mapwalker_data import World, Node, Edge, Player
from typing import List, Tuple, Union, Type, Dict
import random
import sys
from pydantic import BaseModel, Field
from openai import OpenAI
import textwrap
from enum import Enum
import argparse
from devtools import pprint


# -------- Globals & Consts ------------------

# The URL where the local server is running
url = "http://localhost:1234/v1/"
MODEL = "qwen2.5-14b-instruct"
#get the client:
client = OpenAI(base_url=url, api_key="lm-studio")

#prompt for user
USR_CONSOLE_PROMPT = ">*&*> "

# -------- Class Defnitions ---------

#      -----classes for storyline generation:
class StoryArcResponse(BaseModel):
    name: str
    description: str

class ArcCollectionResponse(BaseModel):
    name: str
    all_arcs: List[StoryArcResponse]

class StorySceneResponse(BaseModel):
    name: str
    description: str

class SceneCollectionResponse(BaseModel):
    all_scenes: List[StorySceneResponse]

class PlayerCreationResponse(BaseModel):
    character_background: str

class SingleInteractionResponse(BaseModel):
    response_to_player: str
    player_state: str

#     -----classes for actually storing the data
class SceneCompletion (BaseModel):
    is_completed: bool

class PlayerData (BaseModel):
    background: str #background of the player before the story
    current_state: str #any other description of player state

class SceneExitData (BaseModel):
    #data returned to describe how the scene played out
    real_history: str #what events actually happened
    player_description: PlayerData#how is the player now described?

class NarrativeScene(BaseModel):
    scene_name: str
    scene_description: str
    scene_transition_condition: str = Field(default="")

class NarrativeArc(BaseModel):
    arc_name: str
    arc_description: str
    scenes: List[NarrativeScene] = Field(default=[])
    scene_plans: SceneCollectionResponse = Field(default= SceneCollectionResponse(all_scenes=[]))

class NarrativeTree(BaseModel):
    story_name: str = Field(default="")
    arcs: List[NarrativeArc] = Field(default=[])
    arc_plans: ArcCollectionResponse = Field(default=ArcCollectionResponse(name="", all_arcs=[]))


# -------- Helper Funcs -------------

def pretty_chat(text: str, width=80):
    print(textwrap.fill(text, width=width))

def update_schema(input_model: Type[BaseModel]) -> Dict[str, any]:
    #new update to lmstudio has stricter reqs for structured_output:
    tmp = input_model.model_json_schema()

    return {
        "type": "json_schema",
        "json_schema": {
            "name": "test_schema",
            "strict": True,
            "schema": tmp
        }
    }

def call_llm_structured(messages: List, model_format: Type[BaseModel], temperature=0.5):
    '''
    Make api call to create an object with specified format, as a response from llm.
    '''

    #first get the schema for the model:
    schema = update_schema(model_format)

    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=schema,
        temperature=temperature,
    ).choices[0].message.content

    return model_format.model_validate_json(response)

def call_llm_unstructured(messages: List, temperature=0.5) -> str:
    '''
    Make api call to llm, for basic string
    '''

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        stream=False
    ).choices[0].message.content

    return response

def generate_story_arcs(story_prompt: str = "") -> ArcCollectionResponse:
    ARC_GENERATE_PROMPT = textwrap.dedent(
        """
        You are a virtual Dungeon Master, \
        crafting a solo campaign for a player. \
        Given the context given by the user, \
        Craft a rough outline of the main arcs in the story. \
        For each arc, give a name and a short description. \
        Generate prefer generating about 3 arcs. \
        Also generate a name for the campaign.
        """
    )
    arc_messages = [
        {
            "role": "system",
            "content": ARC_GENERATE_PROMPT 
        },
        {
            "role": "user",
            "content": story_prompt 
        }
    ]

    response = call_llm_structured(arc_messages, ArcCollectionResponse)
    return response

def generate_scene_plans(full_tree: NarrativeTree, arc_identifier: Tuple[int]) -> SceneCollectionResponse:
    SCENE_GENERATE_PROMPT = textwrap.dedent(
        """
        You are a virtual Dungeon Master, \
        crafting a solo campaign for a player. \
        The name of the story, as well as the \
        main arcs have already been outlined. \
        Based on the prompt (selecting one of the arcs), \
        generate an outline of the main scenes in that arc. \
        For each scene, give a name and a short description. \
        For each scene, focus mostly on where it is and what \
        npcs do. Try not to determine how the player would act. \
        Prefer generating around 3 scenes.
        """
    )

    arc_idx = arc_identifier

    scenes_messages = [
        {
            "role": "system",
            "content": SCENE_GENERATE_PROMPT 
        },
        {
            "role": "system",
            "content": f"Current Arc Plans: {full_tree.arc_plans.model_dump_json()}"
        },
        {
            "role": "user",
            "content": f"Generate Scenes for arc number {arc_idx}: '{full_tree.arcs[arc_idx].arc_name}'."
        }
    ]

    response = call_llm_structured(scenes_messages, SceneCollectionResponse)
    return response

def generate_scene_transition_condition(full_tree: NarrativeTree, scene_identifier: Tuple[int, int]) -> str:

    TRANSITION_GENERATE_PROMPT = textwrap.dedent(
        """
        You are a virtual Dungeon Master, \
        crafting a solo campaign for a player. \
        The name of the story, as well as the \
        main arcs have already been outlined. \
        The player is in one of the arcs. \
        The name of the arc is given. \
        The rough scene plans for that arc are also given. \
        The name of which scene the player will now start is also given. \
        The player will soon interact with a Dungeon Master to explore the scene. \
        Based on the plan for the scene, determine some conditions that should \
        describe to the dungeon master when the scene is over. \
        These conditions should be a paragraph of at most 3 sentences. \
        Keep in mind that the player will have some level of freedom, so the conditions \
        Should be general. \
        Try not to determine how the player would act. \
        """
    )

    arc_idx, scene_idx = scene_identifier

    condition_generate_messages = [
        {
            "role": "system",
            "content": TRANSITION_GENERATE_PROMPT
        },
        {
            "role": "system",
            "content": f"Planned arcs: {full_tree.arc_plans.model_dump_json()}"
        },
        {
            "role": "system",
            "content": f"Current arc: Arc {arc_idx}: '{full_tree.arcs[arc_idx].arc_name}'"
        },
        {
            "role": "system",
            "content": f"Planned scenes for arc: {full_tree.arcs[arc_idx].scene_plans.model_dump_json()}"
        },
        {
            "role": "system",
            "content": f"Current scene: Scene {scene_idx}: '{full_tree.arcs[arc_idx].scenes[scene_idx].scene_name}'"
        }
    ]

    condition = call_llm_unstructured(condition_generate_messages)
    return condition

def is_scene_completed(scene_history: List, scene_transition_condition) -> bool:
    SCENE_COMPLETION_PROMPT= textwrap.dedent(
        """
        You are a virtual Dungeon master helping a player go through a solo campaign. \
        Below is a scene transition condition, as well as a list of the history of the current scene. \
        Determine if the condition is roughly met, and therefore if we should move on to the next scene.
        """
    )

    messages = [
        {
            "role": "system",
            "content": SCENE_COMPLETION_PROMPT
        },
        {
            "role": "system",
            "content": f"Transition condition: {scene_transition_condition}" 
        }
    ]
    messages += scene_history

    result: SceneCompletion = call_llm_structured(messages, SceneCompletion)
    return result.is_completed

def describe_scene_history(original_plan: str, scene_history: List) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant tasked with summarizing conversations." 
        },
        {
            "role": "user",
            "content": "Please provide a summary of the following conversation, including any details that might be relavant for the story:"
        },
        {
            "role": "user",
            "content": f"Here is the conversation: {json.dumps(scene_history)}"
        }
    ]

    result: str = call_llm_unstructured(messages)
    return result

def play_planned_scene(
        player_data: PlayerData,
        full_tree: NarrativeTree,
        scene_identifier: Tuple[int, int],
        real_history: str = "No history yet"
    ) -> SceneExitData:
    '''
    Play out a planned scene.
    The identified scene must have been generated, including the condition for transition.
    return some information to pass along to other scenes for context.'''
    arc_idx, scene_idx = scene_identifier
    exit_data = SceneExitData(
        player_description=player_data,
        real_history=full_tree.arcs[arc_idx].scenes[scene_idx].scene_description
    )

    #setup the main prompt for interaction:
    SCENE_MAIN_PROMPT = textwrap.dedent(
        """
        You are a virtual dungeon master for a solo campaign. \
        The storyline you are running is already planned, and some of it is given to you. \
        The format of the story describes the name of the story, \
        the names and descriptions of the main arcs, and the names and \
        descriptions of the scenes planned within the current arc. \
        The current arc, and the current scene are identified to you. \
        Additionally, a description of a transition condition is given. \
        This is roughly what must happen for the player to get from the current scene \
        to the next scene. \
        Also, there is a 'real_history' given. This is what has happened so far in the story. \
        If there is a difference between previous planned events and the real_history, use the real_history as true. \
        The player's background and current state are also given. \
        Your job is to act as the DM on this campaign, describing the current scene as the \
        player interacts with it. \
        Let the player be creative and explore, but subtly and slowly guide them towards the scene \
        transition conditions. \
        Do not push the player forward automatically. \
        Instead, make sure the player makes their own choices. \
        Return an object containing what you want to say to the player, \
        and the player's current state, which depends on their past state and the scene. \
        If the players state doesn't change much, return the same state that was given in. \
        If there are no messages from the player, this means that the scene has just started. \
        """
    )

    prompt_messages = [
        {
            "role": "system",
            "content": SCENE_MAIN_PROMPT 
        },
        {
            "role": "system",
            "content": f"Planned story name: {full_tree.story_name}"
        },
        {
            "role": "system",
            "content": f"Planned story arcs: {full_tree.arc_plans.model_dump_json()}"
        },
        {
            "role": "system",
            "content": f"Current arc: Arc {arc_idx}: '{full_tree.arcs[arc_idx].arc_name}'"
        },
        {
            "role": "system",
            "content": f"Planned scenes for this arc: {full_tree.arcs[arc_idx].scene_plans.model_dump_json()}"
        },
        {
            "role": "system",
            "content": f"Current scene: Scene {scene_idx}: '{full_tree.arcs[arc_idx].scenes[scene_idx].scene_name}'"
        },
        {
            "role": "system",
            "content": f"real_history: {real_history}"
        },
        {
            "role": "system",
            "content": f"Current scene transition condition: {full_tree.arcs[arc_idx].scenes[scene_idx].scene_transition_condition}"
        },
        {
            "role": "system",
            "content": f"Player data: {player_data.model_dump_json()}"
        }
    ]
    messages = []

    result: SingleInteractionResponse = call_llm_structured(prompt_messages + messages, SingleInteractionResponse)
    
    #first of all, print response to user:
    pretty_chat(result.response_to_player)

    #add this response to our context
    messages.append(
        {
            "role": "assistant",
            "content": result.model_dump_json() 
        }
    )

    print()#empty line for good spacing
    usr_input = input(USR_CONSOLE_PROMPT)

    # add the input from user to our messages
    messages.append(
        {
            "role": "user",
            "content": usr_input
        }
    )

    #next, determine if the scene is over:
    while(not is_scene_completed(messages, full_tree.arcs[arc_idx].scenes[scene_idx].scene_transition_condition)):

        result: SingleInteractionResponse = call_llm_structured(prompt_messages + messages, SingleInteractionResponse)
        
        #first of all, print response to user:
        print()
        pretty_chat(result.response_to_player)

        #add this response to our context
        messages.append(
            {
                "role": "assistant",
                "content": result.model_dump_json() 
            }
        )

        print()#empty line for good spacing
        usr_input = input(USR_CONSOLE_PROMPT)


        # add the input from user to our messages
        messages.append(
            {
                "role": "user",
                "content": usr_input
            }
        )

    # when finished, get a summary of the scene for the next scene to use as context
    exit_data.player_description = PlayerData(background=player_data.background, current_state=result.player_state)
    exit_data.real_history = describe_scene_history(full_tree.arcs[arc_idx].scenes[scene_idx].scene_description, messages)

    return exit_data

def player_creation(full_tree: NarrativeTree) -> PlayerData:
    '''
    Help the player to create their character, given the planned story.
    '''
    PLAYER_GEN_PROMPT = textwrap.dedent(
        """
        You are a virtual Dungeon Master, \
        crafting a solo campaign for a player. \
        The planned arcs for the campaign are given. \
        Your goal is to help the player craft a character that will fit well with the story to come. \
        Do not spoil the story. \
        You may offer ideas of characters, without ever spoiling the story. \
        If there is user feedback, adjust the character accordingly. \
        Return the proposed character's background. \
        The background should be short (at most 6 sentences). 
        """
    )
    gen_messages = [
        {
            "role": "system",
            "content": PLAYER_GEN_PROMPT 
        },
        {
            "role": "system",
            "content": f"Planned story: {full_tree.arc_plans.model_dump_json()}"
        }
    ]

    response: PlayerCreationResponse = call_llm_structured(gen_messages, PlayerCreationResponse)
    print("Proposed character:")
    pprint(response)
    print("Is this acceptable? [Y for yes or give feedback]")

    #get feedback from the user:
    choice = input(USR_CONSOLE_PROMPT)
    while choice.lower() != "y":
        gen_messages += [
            {
                "role": "assistant",
                "content": response.model_dump_json()
            },
            {
                "role": "user",
                "content": choice
            }
        ]
        response: PlayerCreationResponse = call_llm_structured(gen_messages, PlayerCreationResponse)
        print("Proposed character:")
        pprint(response)
        print("Is this acceptable? [Y for yes or give feedback]")
        choice = input(USR_CONSOLE_PROMPT)


    return PlayerData(background=response.character_background, current_state="")

# -------- Main Runtime -------------

def main(story_prompt: str, verbose: bool):
    #create a narrative tree
    narrative_tree = NarrativeTree()

    #first, we need to generate our story:
    arcs = generate_story_arcs(story_prompt)
    if verbose:
        #lets try to print that out:
        print(f"Story for prompt: {story_prompt}:")
        pprint(arcs)
    #add to the tree:
    narrative_tree.story_name = arcs.name
    narrative_tree.arcs = [ NarrativeArc(arc_name=arc.name, arc_description=arc.description) for arc in arcs.all_arcs ]
    narrative_tree.arc_plans = arcs

    #now create our player:
    player = player_creation(narrative_tree)

    #lets create our chat that will be built over time within this scene:
    real_history = "No history yet."

    #loop over the arcs (they will occur linearly):
    for arc_idx in range(len(arcs.all_arcs)):

        #generate the scenes for this arc:
        scene_plans = generate_scene_plans(narrative_tree, (arc_idx))
        if verbose:
            #try to print that out:
            print("Printing scene plans:")
            pprint(scene_plans)
        #now add it to the tree:
        narrative_tree.arcs[arc_idx].scene_plans = scene_plans
        narrative_tree.arcs[arc_idx].scenes = [ NarrativeScene(scene_name=scene.name, scene_description=scene.description) for scene in scene_plans.all_scenes ]


        for scene_idx in range(len(scene_plans.all_scenes)):

            #finally, lets explore this scene!
            #generate the transition conditions:
            scene_transition_condition = generate_scene_transition_condition(narrative_tree, (arc_idx, scene_idx))
            if verbose:
                #print that condition out
                print(f"Scene transition conditions for {narrative_tree.arcs[arc_idx].scenes[scene_idx].scene_name}")
                pprint(scene_transition_condition)
            #store the conditions:
            narrative_tree.arcs[arc_idx].scenes[scene_idx].scene_transition_condition = scene_transition_condition


            #play out the scene
            exit_data = play_planned_scene(player_data=player, full_tree=narrative_tree, scene_identifier=(arc_idx, scene_idx), real_history=real_history)
            player = exit_data.player_description
            real_history = exit_data.real_history



            print("you finished the scene, good job!")
            print(f"Here is what happened: {real_history}")
            print()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate and traverse a narative tree campaign.",
    )

    parser.add_argument(
        "-f", "--load_file",
        dest="filename",
        type=str,
        help="Load from a save file of a campaign"
    )

    parser.add_argument(
        "-p", "--prompt",
        dest="story_prompt",
        default="",
        help="Specify a prompt to use when generating a story",
        type=str
    )

    parser.add_argument(
        "-v", "--verbose",
        dest="verbose",
        default=True,
        type=bool,
        help="Describe whether to print out extra debug information"
    )

    args = parser.parse_args()

    main(story_prompt=args.story_prompt, verbose=args.verbose)