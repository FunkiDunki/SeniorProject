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
from narative_tree import call_llm_structured, call_llm_unstructured, pretty_chat


# -------- Globals & Consts ------------------
FACT_COUNTER=10
# -------- Class Defnitions ---------

class Fact(BaseModel):
    fact_id: int
    fact_content: str

class HiddenFact(BaseModel):
    fact: Fact
    discovery_condition: str

class KnownFact(BaseModel):
    fact: Fact

class HiddenFactList(BaseModel):
    reasoning: str
    facts: List[HiddenFact]

class DicoveredFactsIds(BaseModel):
    reasoning: str
    dicoveries: List[int]

class GeneratedFactsResponse(BaseModel):
    reasoning: str
    hidden_facts: List[HiddenFact]
    known_facts: List[KnownFact]
    player_context: Dict

# -------- Helper Funcs -------------

def generate_initial_facts(story_prompt: str) -> Tuple[List[KnownFact], List[HiddenFact], Dict]:
    """
    Generates an initial set of known and hidden facts based on the given story prompt.
    
    Args:
        story_prompt (str): The prompt describing the story scenario (e.g., "A murder mystery").
    
    Returns:
        Tuple[List[KnownFact], List[HiddenFact], Dict]: A tuple containing lists of known facts and hidden facts and player context.
    """
    initial_facts_prompt = (
        f"Generate an initial set of facts for a game scenario based on the following theme: '{story_prompt}'. "
        "Create two categories of facts: known facts that are available to the player at the start, and hidden facts that must be discovered. "
        "Ensure the known facts establish the context for the mystery, while the hidden facts contain deeper secrets or twists that add complexity. "
        "Provide enough detail to make the story rich and interesting."
        "For the hidden facts, provide some very brief description of what condition would need to be met in order to discover each fact."
    )

    context_prompt = (
        f"Based on the following story prompt: '{story_prompt}', "
        "generate an initial context for the player including their location, time of day, and current situation. Provide enough detail to establish the scene."
    )

    messages = [
        {"role": "system", "content": "You are an AI that generates a list of known and hidden facts for a narrative game."},
        {"role": "user", "content": initial_facts_prompt},
        {"role": "user", "content": context_prompt}
    ]

    # Call LLM to generate initial facts
    generated_fact_list: GeneratedFactsResponse = call_llm_structured(messages, GeneratedFactsResponse)

    # Extract known and hidden facts from the generated response
    known_facts_data = generated_fact_list.known_facts
    hidden_facts_data = generated_fact_list.hidden_facts
    player_context_data = generated_fact_list.player_context

    # Create lists of KnownFact and HiddenFact from the generated data
    known_facts = [KnownFact(fact=Fact(fact_id=index + 1, fact_content=content.fact.fact_content)) for index, content in enumerate(known_facts_data)]
    hidden_facts = [
        HiddenFact(
            fact=Fact(fact_id=len(known_facts) + index + 1, fact_content=content.fact.fact_content),
            discovery_condition=content.discovery_condition
        )
        for index, content in enumerate(hidden_facts_data)
    ]

    return known_facts, hidden_facts, player_context_data

def generate_narrative_response(player_action: str, known_facts: List[KnownFact]) -> str:
    """
    This function generates a narrative response based on the player's action and known facts.
    
    Args:
        player_action (str): The action taken by the player.
        known_facts (List[KnownFact]): The list of all known facts.
    
    Returns:
        str: A narrative response to the player's action.
    """
    known_facts_content = [known_fact.fact.fact_content for known_fact in known_facts]
    response_prompt = (
        f"The player took the action: '{player_action}'. "
        f"Here are the current known facts: {known_facts_content}. "
        "Based on this, provide an appropriate narrative response to the player's action that maintains consistency with the story and known information."
    )
    
    response_messages = [
        {"role": "system", "content": "You are an AI that generates narrative responses for a murder mystery game."},
        {"role": "user", "content": response_prompt}
    ]
    
    response = call_llm_unstructured(response_messages)
    return response

def generate_hidden_facts(hidden_facts, known_facts, player_action, player_context) -> HiddenFactList:
    """
    This function generates new hidden facts based on the player's action and context.
    
    Args:
        hidden_facts (List[HiddenFact]): The list of all hidden facts.
        known_facts (List[KnownFact]): The list of all known facts.
        player_action (str): The action taken by the player.
        player_context (dict): The current context of the player in the game.
    
    Returns:
        HiddenFactList: A list of new hidden facts that have been generated with reasoning.
    """
    # Construct prompt with current hidden facts to provide context to the LLM
    hidden_facts_content = [hidden_fact.fact.fact_content for hidden_fact in hidden_facts]
    known_facts_content = [known_fact.fact.fact_content for known_fact in known_facts]
    prompt = (
        f"The player took the action: '{player_action}' in the context: '{player_context}'. "
        f"Here are the current hidden facts: {hidden_facts_content}. "
        f"Here are the current known facts: {known_facts}."
        "Based on this, generate new hidden facts that are relevant to the game and are needed to decide the outcome of the player's action. "
        "Make sure that the new facts do not duplicate existing facts and fit logically within the existing story and situation."
    )
    
    messages = [
        {"role": "system", "content": "You are an AI that generates hidden knowledge for a murder mystery game."},
        {"role": "user", "content": prompt}
    ]
    
    # actuall llm call
    generated_hidden_fact_list: HiddenFactList = call_llm_structured(messages, HiddenFactList)
    global FACT_COUNTER

    for i in range(len(generated_hidden_fact_list.facts)):
        generated_hidden_fact_list.facts[i].fact.fact_id = FACT_COUNTER
        FACT_COUNTER += 1
    
    return generated_hidden_fact_list


def discover_hidden_facts(player_action: str, hidden_facts: List[HiddenFact], player_context) -> DicoveredFactsIds:
    """
    This function identifies which hidden facts are discovered based on the player's action.
    
    Args:
        player_action (str): The action taken by the player.
        hidden_facts (List[HiddenFact]): The list of all hidden facts.
    
    Returns:
        List[int]: A list of fact IDs that are discovered by the player's action.
    """
    # Construct prompt with player's action and current hidden facts
    hidden_facts_content = [hidden_fact.model_dump_json() for hidden_fact in hidden_facts]
    prompt = (
        f"The player took the action: '{player_action}'. "
        f"They were in the context: {player_context}"
        f"Here are the current hidden facts: {hidden_facts_content}. "
        "Identify which hidden facts, if any, would be discovered based on the player's action. "
        "Provide a list of fact IDs that are discovered by the action, along with a brief reasoning."
    )
    
    messages = [
        {"role": "system", "content": "You are an AI that determines which hidden facts are discovered in a murder mystery game."},
        {"role": "user", "content": prompt}
    ]
    
    discovered_fact_ids = call_llm_structured(messages, DicoveredFactsIds)
    
    return discovered_fact_ids

# -------- Main Runtime -------------

def main(story_prompt: str, verbose: bool):
    #define our facts
    '''
    hidden_facts: List[HiddenFact] = [
        HiddenFact(
            fact=Fact(
                fact_id=1,
                fact_content="Lady Margaret Blackwell and Mr. Charles Gray were secretly having an affair."
            ),
            discovery_condition="Uncovering a love letter in Margaret’s room."
        ),
        HiddenFact(
            fact=Fact(
                fact_id=2,
                fact_content="Lord Blackwell planned to cut Mr. Charles Gray out of a lucrative business deal."
            ),
            discovery_condition="Finding a draft of the business contract in the victim's study."
        ),
        HiddenFact(
            fact=Fact(
                fact_id=3,
                fact_content="The ceremonial dagger used in the murder was taken from the display case in the library."
            ),
            discovery_condition="Examining the display case in the library."
        ),
        HiddenFact(
            fact=Fact(
                fact_id=4,
                fact_content="Miss Eleanor Birch was seen entering the library shortly before the murder."
            ),
            discovery_condition="Interrogating Mrs. Agnes Halloway, the housekeeper."
        ),
        HiddenFact(
            fact=Fact(
                fact_id=5,
                fact_content="Dr. Victor Harper was in the study with Lord Blackwell an hour before his death."
            ),
            discovery_condition="Finding Dr. Harper’s handkerchief on the floor in the study."
        ),
        HiddenFact(
            fact=Fact(
                fact_id=6,
                fact_content="The study door can be locked from the inside but also has a hidden latch accessible from the hallway."
            ),
            discovery_condition="Examining the study door closely."
        )
    ]
    known_facts: List[KnownFact] = [
        KnownFact(
            fact=Fact(
                fact_id=7,
                fact_content="The sky is red due to ancient magical rituals."
            )
        ),
        KnownFact(
            fact=Fact(
                fact_id=8,
                fact_content="The knife used in the murder is a ceremonial dagger from Lord Blackwell’s personal collection."
            )
        ),
        KnownFact(
            fact=Fact(
                fact_id=9,
                fact_content="Six individuals were in the house at the time of the murder."
            )
        )
    ]
    '''

    story_prompt = input("Enter a story prompt: ")
    known_facts, hidden_facts, player_context = generate_initial_facts(story_prompt=story_prompt)

    print("Hidden facts:")
    pprint(hidden_facts)

    print("Known facts:")
    pprint(known_facts)

    print("Player Context:")
    pprint(player_context)

    while True:
        #get player input
        player_input = input("Enter your action: ")

        #generate any needed facts
        new_facts: HiddenFactList = generate_hidden_facts(
            hidden_facts=hidden_facts,
            known_facts=known_facts,
            player_action=player_input,
            player_context=player_context
        )
        pprint(new_facts)

        hidden_facts.extend(
            new_facts.facts
        )
        print("\n\nnew hidden facts list:")
        pprint(hidden_facts)

        #move facts from hidden to known
        discovered_facts = discover_hidden_facts(
            player_action=player_input,
            hidden_facts=hidden_facts,
            player_context=player_context
        )
        pprint(discovered_facts)

        for fact_id in discovered_facts.dicoveries:
            for hidden_fact in hidden_facts:
                if hidden_fact.fact.fact_id == fact_id:
                    known_facts.append(KnownFact(fact=hidden_fact.fact))
                    hidden_facts.remove(hidden_fact)

        #generate response using only known facts
        response = generate_narrative_response(player_input, known_facts)
        print("Narrative Response:")
        pprint(response)

        #add last action to centext
        player_context["last_action"] = player_input




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