import requests
import json
from mapwalker_data import World, Node, Edge, Player
from typing import List, Tuple
import random
import sys
from pydantic import BaseModel

# The URL where the local server is running
url = "http://localhost:1234/v1/chat/completions"

# The headers to indicate that we are sending JSON data
headers = {
    "Content-Type": "application/json"
}

def testing_structered():
    {
        "name": "ui",
        "description": "Dynamically generated UI",
        "strict": true,
        "schema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "The type of the UI component",
                    "enum": ["div", "button", "header", "section", "field", "form"]
                },
                "label": {
                    "type": "string",
                    "description": "The label of the UI component, used for buttons or form fields"
                },
                "children": {
                    "type": "array",
                    "description": "Nested UI components",
                    "items": {
                        "$ref": "#"
                    }
                },
                "attributes": {
                    "type": "array",
                    "description": "Arbitrary attributes for the UI component, suitable for any element",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the attribute, for example onClick or className"
                            },
                            "value": {
                                "type": "string",
                                "description": "The value of the attribute"
                            }
                        },
                      "additionalProperties": false,
                      "required": ["name", "value"]
                    }
                }
            },
            "required": ["type", "label", "children", "attributes"],
            "additionalProperties": false
        }
    }

def node_generate(node_id: str, world: World) -> Tuple[Node, List[str]]:
    '''input: name of node
        output: description,
        list of any connected new nodes.'''
    # The JSON data payload
    # 
    num_new = random.randrange(1, 3)
    print(f"new node detected... generating...\n")
    data = {
        "messages": [
            {"role": "system", "content": f"Given the name of a location, generate a brief description of it. Also, give names to 5 locations that would be nearby, in the outgoing_connections"},
            {"role": "system", "content": f"name of node: {node_id}"},
            {"role": "user", "content": "Generate and return information for a new node with the given name"}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "new_node_response",
                "strict": "true",
                "schema": {
                    "type": "object",
                    "properties": {
                        "node_description": {
                            "type": "string"
                        },
                        "outgoing_connections": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    }
                },
                "required": ["node_description", "outgoing_connections"]
            }
        },
        "temperature": 0.5,
        "max_tokens": -1,
        "stream": False
    }

    # Making the POST request to the local server
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Checking if the request was successful
    if response.status_code == 200:
        # Printing the response content
        response = response.json()['choices'][0]['message']
        #print(response)
        response = json.loads(response['content'])
        node = Node(node_id, response['node_description'])
        outgoings = response['outgoing_connections'][:num_new]
        return (node, outgoings)
    else:
        print("Failed to get response:", response.status_code, response.text)
        return None

def understand_input(current_world: World, player: Player, user_prompt: str):
    #for now, everything would be a move command
    # The JSON data payload
    print("Crunching numbas....\n")
    possible_nodes = {
        "possible_nodes": valid_locations(player.location, current_world.edges)
    }
    possible_nodes['possible_nodes'].append("other")
    #print(possible_nodes)

    data = {
        "messages": [
            {"role": "system", "content": "Given the current world as json input. Assume the user wants to move to one of the listed nodes. Return the id of the node exactly as it appears in the list. Select other if the previous options don't apply to the prompt."},
            {"role": "system", "content": json.dumps(possible_nodes)},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "node_move_response",
                "strict": "true",
                "schema": {
                    "type": "object",
                    "properties": {
                        "node_id": {
                            "type": "string"
                        }
                    }
                },
                "required": ["node_id"]
            }
        },
        "temperature": 0.1,
        "max_tokens": -1,
        "stream": False
    }

    # Making the POST request to the local server
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Checking if the request was successful
    if response.status_code == 200:
        # Printing the response content
        response = response.json()['choices'][0]['message']
        #print(response)
        response = json.loads(response['content'])['node_id']
        #print(response)
        if response not in possible_nodes['possible_nodes'][:-1]:
            return None
        return response
    else:
        print("Failed to get response:", response.status_code, response.text)
        return None

def valid_locations(from_id: str, edge_list: List[Edge]) -> List[str]:
    result = []
    for n in edge_list:
        if n.from_id == from_id:
            result.append(n.to_id)
    return result

def main(player=None, world=None):

    #default adventure
    nodes = [
        Node("forest_1", "dark forest"),
        Node("forest_2", "dark forest"),
        #Node("forest_well", "a clearing in the dark forest, with a stone well"),
    ]
    edges = [
        Edge("forest_1", "forest_2"),
        Edge("forest_2", "forest_well"),
        Edge("forest_1", "forest_well"),
        Edge("forest_2", "forest_1"),
        Edge("forest_well", "forest_2"),
    ]

    #if an adventure is input, we do that one
    if world is None:
        world = World(nodes, edges)
    if player is None:
        player = Player("forest_1")

    while True:
        print(f"you are in {player.location}")

        if player.location not in [n.node_id for n in world.nodes]:
            #we need to generate the node
            (n, o) = node_generate(player.location, world)
            #print(n)
            #print(o)
            world.nodes.append(n)
            for n2 in o:
                world.edges.append(Edge(n.node_id, n2))
                world.edges.append(Edge(n2, n.node_id))
        
        for n in world.nodes:
            if n.node_id == player.location:
                print(f"Description: {n.node_description}")
                break

        #where we could go next
        print("\nAround you are the following locations:")
        print(set(valid_locations(player.location, world.edges)))

        #get input from user
        prompt = input("\n>> ")

        #find the next node to go to
        new_node = understand_input(world, player, prompt)
        if new_node is not None:
            #print(f"You moved to {new_node}.")
            player.location = new_node
        else:
            print("Sorry, but that wasn't a valid move nearby.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        player = Player("Start")
        world = World(
            nodes= [ Node(node_id="Start", node_description="Anything could happen!") ],
            edges= [ Edge("Start", sys.argv[1])]
        )
        main(player, world)
    else:
        main()