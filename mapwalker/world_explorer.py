import json
import pickle
from mapwalker_data import World, Node, Edge, Player
from typing import List, Tuple, Union, Type, Dict
import random
import sys
from pydantic import BaseModel, Field
from openai import OpenAI
from enum import Enum
import argparse
from devtools import pprint
from narative_tree import call_llm_structured, call_llm_unstructured
import os


# -------- Globals & Consts ------------------

# The URL where the local server is running
url = "http://localhost:1234/v1/"
MODEL = "mistral-nemo-instruct-2407"
#get the client:
client = OpenAI(base_url=url, api_key="lm-studio")

#prompt for user
USR_CONSOLE_PROMPT = ">*&*> "

NODE_COUNTER = 1

# -------- Class Defnitions ---------

#      -----classes for generation:
#generating the original story can be unstructured.

#classes for generating the layer-1 regions
class SingleRegionResponse(BaseModel):
    name: str
    description: str
    connection_to_history: str
    
class RegionGenerateResponse(BaseModel):
    regions: List[SingleRegionResponse]

#classes for generating the layer-2 regions
class SingleSubRegionResponse(BaseModel):
    name: str
    description: str
    connection_to_history: str
    
class SubRegionGenerateResponse(BaseModel):
    subregions: List[SingleSubRegionResponse]

#     -----classes for actually storing the data

class Node(BaseModel):
    node_id: int
    node_name: str
    node_description: str
    connection_to_history: str
    outgoing_edges: List[int]
    children: List[int]

class Player(BaseModel):
    region_id: int = Field(default=-1)
    subregion_id: int = Field(default=-1)

class World(BaseModel):
    history: str
    regions: List[int]
    all_nodes: Dict[int, Node]
    player: Player


# -------- Helper Funcs -------------


def generate_main_history(story_prompt: str = "") -> str:
    messages = [
        {"role": "system", "content": "You are a storyteller, describing the history of a world based on the user's prompt."},
        {"role": "user", "content": story_prompt},
    ]

    return call_llm_unstructured(messages) 

def generate_regions(world: World) -> World:

    global NODE_COUNTER

    prompt = (
        "For the following world, describe 2-6 overall regions that exist. "
        "For each location, give a name and a paragraph description of the location. "
        "Also, give a description of how that region connects to the overall history. "
    )
    messages = [
        {"role": "system", "content": "You are a designer of fantastic world, describing a world as the user desires."},
        {"role": "user", "content": prompt},
        {"role": "user", "content": f"{world.history}"}
    ]

    result: RegionGenerateResponse = call_llm_structured(messages, RegionGenerateResponse) 

    for region in result.regions:
        world.regions.append(NODE_COUNTER)
        world.all_nodes[NODE_COUNTER] = \
            Node(
                node_id=NODE_COUNTER,
                node_name=region.name,
                node_description=region.description,
                connection_to_history=region.connection_to_history,
                outgoing_edges=[],
                children=[]
            )
        NODE_COUNTER += 1
    
    return world

def generate_cities(world: World) -> World:
    '''
    Assuming the player has just entered a new region, generate the cities for that region (if they don't exist)
    '''

    global NODE_COUNTER

    if len(world.all_nodes[world.player.region_id].children) > 0:
        #the region has already been generated
        return world
    
    regions_info = [
        {
            "name": world.all_nodes[region].node_name,
            "description": world.all_nodes[region].node_description,
            "connection_to_history": world.all_nodes[region].connection_to_history
        }
        for region in world.regions
    ]

    #now actually generate the cities
    prompt = (
        f"based on the history of the world and the descriptions of the main regions, list 2-5 sub-locations that might exist within the region of {world.all_nodes[world.player.region_id].node_name}. "
        "For each location, give a name and a paragraph description of the location. "
        "Also, give a description of how that subregion connects to the region it exists within."
        "Don't generate a subregion named after the region it is in. "
    )
    info = get_relevant_information(world)
    messages = [
        {"role": "system", "content": "You are a designer of fantastic world, expanding on how the regions and subregions connect to the world's story."},
        {"role": "user", "content": prompt},
        *info,
    ]

    result: SubRegionGenerateResponse = call_llm_structured(messages, SubRegionGenerateResponse) 

    for city in result.subregions:
        world.all_nodes[world.player.region_id].children.append(NODE_COUNTER)
        world.all_nodes[NODE_COUNTER] = \
            Node(
                node_id=NODE_COUNTER,
                node_name=city.name,
                node_description=city.description,
                connection_to_history=city.connection_to_history,
                outgoing_edges=[],
                children=[]
            )
        NODE_COUNTER += 1
    
    return world

def place_player_region(world: World) -> World:
    '''place the player into a region of their choosing to explore'''
    print(f"In this world, there are {len(world.regions)} main regions:")
    for i, region in enumerate(world.regions):
        print(f"\t({i+1}). {world.all_nodes[region].node_name}")
    
    choice = input("Pick the number of a region to explore!")
    while not (choice.isnumeric() and int(choice) >= 1 and int(choice) <= len(world.regions)):
        print("Whoops, that wasn't a valid choice!")
        choice = input("Pick the number of a region to explore!")
    
    choice = int(choice) - 1
    print(f"Okay! Let's explore {world.all_nodes[world.regions[choice]].node_name}!")

    world.player.region_id = world.regions[choice]

    return world

def get_relevant_information(world: World) -> List[dict]:
    '''based on the current state and location of player, get the relevant information for the model.'''

    result = []

    if world.player.region_id != -1:

        #add info of the regions in the world
        regions_info = [
            {
                "name": world.all_nodes[region].node_name,
                "description": world.all_nodes[region].node_description,
                "connection_to_history": world.all_nodes[region].connection_to_history
            }
            for region in world.regions
        ]
        result.append(
            {"role":"user", "content":f"There are a few main regions of the world: {regions_info}"})

        result.append(
            {"role":"user", "content":f"The player is in the main region of {world.all_nodes[world.player.region_id].node_name}"}
        )

        if world.player.subregion_id != -1:
            #add info of the subregions for the player's region
            subregions_info = [
                {
                    "name": world.all_nodes[region].node_name,
                    "description": world.all_nodes[region].node_description,
                    "connection_to_history": world.all_nodes[region].connection_to_history
                }
                for region in world.all_nodes[world.player.region_id].children
            ]
            result.append(
                {"role":"user", "content":f"Here are all generated subregions for this region so far: {subregions_info}"})
            result.append(
                {"role": "user", "content": f"The player is in the subregion called {world.all_nodes[world.player.subregion_id].node_name}"}
            )

    return result

def place_player_subregion(world: World) -> World:
    '''place the player into a subregion of their choosing to explore'''
    #find the player's region:
    
    region = world.all_nodes[world.player.region_id]

    print(f"In this region, there are {len(region.children)} subregions:")
    for i, subregion in enumerate(region.children):
        print(f"\t({i+1}). {world.all_nodes[subregion].node_name}")
    
    choice = input("Pick the number of a subregion to explore!")
    while not (choice.isnumeric() and int(choice) >= 1 and int(choice) <= len(region.children)):
        print("Whoops, that wasn't a valid choice!")
        choice = input("Pick the number of a subregion to explore!")
    
    choice = int(choice) -1

    print(f"Okay! Let's explore {world.all_nodes[region.children[choice]].node_name}!")

    world.player.subregion_id = region.children[choice]

    return world

def explore_subregion(world: World) -> World:

    subregion = world.all_nodes[
        world.player.subregion_id
    ]

    regions_info = [
        {
            "name": world.all_nodes[region].node_name,
            "description": world.all_nodes[region].node_description,
            "connection_to_history": world.all_nodes[region].connection_to_history
        }
        for region in world.regions
    ]

    subregions_info = [
        {
            "name": world.all_nodes[region].node_name,
            "description": world.all_nodes[region].node_description,
            "connection_to_history": world.all_nodes[region].connection_to_history
        }
        for region in world.all_nodes[world.player.region_id].children
    ]

    #describe the region
    prompt = (
        f"Describe the subregion of {subregion.node_name}, as if the player is just entering the subregion. "
        "Truly paint the scene vividly, including all that the player might see. "
    )

    messages = [
        {"role": "system", "content": "You are a storyteller, helping the player to explore the given world and discover its history."},
        {"role": "user", "content": f"Here is the history of the world: {world.history}"},
        {"role": "user", "content": f"Here are the main regions of the world: {regions_info}"},
        {"role": "user", "content": f"The player is in the region of {world.all_nodes[world.player.region_id].node_name}."},
        {"role": "user", "content": f"The region the player is in has subregions: {subregions_info}"},
        {"role": "user", "content": prompt}
    ]

    result = call_llm_unstructured(messages)
    print(result)
    return world

# -------- Main Runtime -------------

def main(story_prompt: str, verbose: bool, load_level: int, load_file: str):
    world = World(
        history="",
        regions=[],
        all_nodes = {},
        player=Player()
    )

    #check for load file
    if load_level >= 0 and os.path.exists(load_file):
        #load from file
        with open(load_file, 'rb') as file:
            world_save = pickle.load(file)
        world_save: World
        world.history= world_save.history
    else:
        print("no save found, starting from scratch.")
        world_save = None
        world.history = generate_main_history(story_prompt)
        if verbose:
            #lets try to print that out:
            pprint(f"Story: {world.history}")


    if load_level >= 1 and world_save is not None:
        for key in world_save.regions:
            world.regions.append(key)
            world.all_nodes[key] = world_save.all_nodes[key]
            world.all_nodes[key].children = []

    else:
        print("Generating regions...")
        world = generate_regions(world)
    
    if load_level >= 0:
        #save the world
        with open(load_file, 'wb') as file:
            pickle.dump(world, file)
        print(f"Saved world into file: {load_file}.")
    
    world = place_player_region(world)
    world = generate_cities(world)
    world = place_player_subregion(world)
    world = explore_subregion(world)


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
        "-l", "--load_level",
        dest="load_level",
        type=int,
        help="level of loading if desired"
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

    main(story_prompt=args.story_prompt, verbose=args.verbose, load_level=args.load_level, load_file=args.filename)