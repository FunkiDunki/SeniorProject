import json
from mapwalker_data import World, Node, Edge, Player
from typing import List, Tuple, Union
import random
import sys
from pydantic import BaseModel
from openai import OpenAI
import textwrap

# The URL where the local server is running
url = "http://localhost:1234/v1/"
MODEL = "mathstral-7b-v0.1"

# The headers to indicate that we are sending JSON data
headers = {"Content-Type": "application/json"}

client = OpenAI(base_url=url, api_key="lm-studio")


class OptionalFormat(BaseModel):
    value: Union[int, List[str]]


def testing_structered():

    messages = [
        {
            "role": "system",
            "content": "either return a list of names, or a number, \
depending on what the user asks for.",
        },
        {"role": "user", "content": "give me a number"},
    ]

    response = (
        client.beta.chat.completions.parse(
            model=MODEL, messages=messages, response_format=OptionalFormat
        )
        .choices[0]
        .message.parsed
    )

    if isinstance(response, OptionalFormat):
        print(response.value)

    return


class NodeGenerateFormat(BaseModel):
    node_description: str
    outgoing_connections: List[str]


def node_generate(node_id: str, world: World) -> Tuple[Node, List[str]]:
    """input: name of node
    output: description,
    list of any connected new nodes."""
    # The JSON data payload
    #
    num_new = random.randrange(1, 3)
    print("new node detected... generating...\n")
    data = {
        "messages": [
            {
                "role": "system",
                "content": textwrap.dedent(
                    """
                    Given the name of a location, generate a brief \
                    description of it. Also, give names to 5 locations \
                    that would be nearby, in the outgoing_connections"""
                ),
            },
            {"role": "system", "content": f"name of node: {node_id}"},
            {
                "role": "user",
                "content": textwrap.dedent(
                    """
                    Generate and return information \
                    for a new node with the given name"""
                ),
            },
        ],
        "temperature": 0.5,
        "max_tokens": -1,
        "stream": False,
    }

    # Making the POST request to the local server
    # response = requests.post(url, headers=headers, data=json.dumps(data))
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=data["messages"],
        response_format=NodeGenerateFormat,
        temperature=data["temperature"],
    )
    response = response.choices[0].message.parsed

    # Checking if the request was successful
    if isinstance(response, NodeGenerateFormat):
        # Printing the response content
        node = Node(node_id, response.node_description)
        outgoings = response.outgoing_connections[:num_new]
        return (node, outgoings)
    else:
        print("Failed to get response")
        return None


class NodeMoveResponse(BaseModel):
    node_id: str


def decypher_move(
    current_world: World, player: Player, user_prompt: str
) -> NodeMoveResponse:
    """where does the player want to move to"""

    print("Crunching numbas....\n")

    cur_node = current_world.nodes[player.location]
    possibile_moves = valid_locations(player.location, current_world.edges)
    # tell the model which nodes could be moved to
    relevant_lore = {
        "possible_nodes": possibile_moves,
        "current_node": {
            "node_id": cur_node.node_id,
            "node_description": cur_node.node_description,
        },
    }
    # print(possible_nodes)

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": textwrap.dedent(
                    """
                    The player is in the current node. \
                    Decide which of the available locations the player \
                    is trying to move to. return 'other' if the command \
                    doesnt match any of the available locations."""
                ),
            },
            {"role": "system", "content": json.dumps(relevant_lore)},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }

    # Making the POST request to the local server
    # response = requests.post(url, headers=headers, data=json.dumps(data))
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=data["messages"],
        response_format=NodeMoveResponse,
        temperature=0.1,
    )

    response = response.choices[0].message.parsed

    # Checking if the request was successful
    if isinstance(response, NodeMoveResponse):
        print(response)
        new_node = response.node_id
        if new_node not in relevant_lore["possible_nodes"]:
            return None
        return response
    else:
        print("Failed to get response")
        return None


class NodeInteractResponse(BaseModel):
    event_description: str
    node_description: str


def decypher_interaction(
    current_world: World, player: Player, user_prompt: str
) -> NodeInteractResponse:
    """What does the player want to do?"""

    print("Crunching numbas....\n")

    cur_node = current_world.nodes[player.location]
    # tell the model which nodes could be moved to
    relevant_lore = {
        "current_node": {
            "node_id": cur_node.node_id,
            "node_description": cur_node.node_description,
        }
    }
    # print(possible_nodes)

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": textwrap.dedent(
                    """
                    The player is in the current node. \
                    Decide how to player is trying to interact with the node, \
                    and determine what reasonable would happen. \
                    Return a description of the event. \
                    If the event changes the nodes significantly, \
                    return a new description of the node. \
                    Otherwise, return an empty description of the node."""
                ),
            },
            {"role": "system", "content": json.dumps(relevant_lore)},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }

    # Making the POST request to the local server
    # response = requests.post(url, headers=headers, data=json.dumps(data))
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=data["messages"],
        response_format=NodeInteractResponse,
        temperature=0.5,
    )

    response = response.choices[0].message.parsed

    # Checking if the request was successful
    if isinstance(response, NodeInteractResponse):
        # print(response)
        return response
    else:
        print("Failed to get response")
        return None


class ParsedChoiceResponse(BaseModel):
    choice_type: str


def understand_input(
    current_world: World, player: Player, user_prompt: str
) -> str:
    """find out if the player is trying to move or interact"""

    print("Crunching numbas....\n")

    cur_node = current_world.nodes[player.location]
    # tell the model which nodes could be moved to
    relevant_lore = {
        "choice_types": ["move", "interact", "other"],
        "current_node": {
            "node_id": cur_node.node_id,
            "node_description": cur_node.node_description,
        },
    }
    # print(possible_nodes)

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": textwrap.dedent(
                    """
                    The player is in the current node. \
                    Decide whether the player wants to move to another node, \
                    or interact with the current node \
                    (or anything inside the current node). \
                    return one of the given choice types. \
                    Return 'other' if the input did not make sense"""
                ),
            },
            {"role": "system", "content": json.dumps(relevant_lore)},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }

    # Making the POST request to the local server
    # response = requests.post(url, headers=headers, data=json.dumps(data))
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=data["messages"],
        response_format=ParsedChoiceResponse,
        temperature=0.1,
    )

    response = response.choices[0].message.parsed

    # Checking if the request was successful
    if isinstance(response, ParsedChoiceResponse):
        print(response)
        pc = response.choice_type
        if pc != "other" and pc in relevant_lore["choice_types"]:
            return pc
        else:
            return None
    else:
        print("Failed to get response")
        return None


def valid_locations(from_id: str, edge_list: List[Edge]) -> List[str]:
    result = []
    for n in edge_list:
        if n.from_id == from_id:
            result.append(n.to_id)
    return result


def main(player=None, world=None):

    # default adventure
    nodes = {
        "forest": Node("forest", "dark forest"),
    }
    edges = [
        Edge("forest", "forest_well"),
        Edge("forest_well", "forest"),
    ]

    # if an adventure is input, we do that one
    if world is None:
        world = World(nodes, edges)
    if player is None:
        player = Player("forest_1")

    while True:
        print(f"you are in {player.location}\n")

        if player.location not in world.nodes:
            # we need to generate the node
            (n, o) = node_generate(player.location, world)
            # print(n)
            # print(o)
            world.nodes[player.location] = n
            for n2 in o:
                if n2 not in world.nodes:
                    world.edges.append(Edge(n.node_id, n2))
                    world.edges.append(Edge(n2, n.node_id))

        print(world.nodes[player.location].node_description)

        # where we could go next
        print("\nAround you are the following locations:")
        print(set(valid_locations(player.location, world.edges)))

        # get input from user
        prompt = input("\n>> ")

        # find the next node to go to
        pc = understand_input(world, player, prompt)

        if pc == "move":
            # print(f"You moved to {new_node}.")
            result = decypher_move(world, player, prompt)
            if isinstance(result, NodeMoveResponse):
                player.location = result.node_id
            else:
                print("invalid move command")
        elif pc == "interact":
            # print what happened:
            print("you try to interact with the node:")
            result = decypher_interaction(world, player, prompt)
            if isinstance(result, NodeInteractResponse):
                print(f"{result.event_description}\n")
                if result.node_description != "":
                    world.nodes[player.location].node_description = (
                        result.node_description
                    )
            else:
                print("invalid interaction")
        else:
            print("Sorry, but that wasn't a valid move nearby.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        player = Player("Start")
        world = World(
            nodes={
                "Start": Node(
                    node_id="Start", node_description="Anything could happen!"
                )
            },
            edges=[Edge("Start", sys.argv[1])],
        )
        main(player, world)
    else:
        main()
