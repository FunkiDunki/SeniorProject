import random
from narative_tree import call_llm_structured, call_llm_unstructured, pretty_chat
import argparse
from typing import List, Tuple, Union
from pydantic import BaseModel, Field
import textwrap
import json
from devtools import pprint



#------------ pydantic models --------

class SingleRankResult(BaseModel):
    goal_id: str
    goal_closeness: float
class GoalsRankResult(BaseModel):
    ranks: List[SingleRankResult]

class SingleChoiceResult(BaseModel):
    choice_description: str
    success_rate: float
class ChoicesResult(BaseModel):
    choices: List[SingleChoiceResult]
class ChoiceThoughtProcess(BaseModel):
    thoughts: str
    result: ChoicesResult

class StoryNodeResult(BaseModel):
    id: str
    description: str

class ActionResult(BaseModel):
    success: bool
    action_description: str
    new_story_node: StoryNodeResult
    knowlege: str


#------------- HELPER FUNCS ------------

def rank_goals(goals: List[dict], current_node: StoryNodeResult) -> GoalsRankResult:
    mesg = [
        {
            "role": "system",
            "content": textwrap.dedent(
                """The user is in a certain point in a choose your own adventure book. \
                The point they are at is described by their current node. \
                There is a list of goals which are some ways that the story could eventually end. \
                for each goal, rate how close the player is to accomplishing it, from 0 to 1. \
                return a list of single rank results, which include the goal's id and the rating.
                """
            )
        },
        {
            "role": "system",
            "content": "current node: " + current_node.model_dump_json()
        },
        {
            "role": "system",
            "content": "goals: " + json.dumps(goals)
        }
    ]

    return call_llm_structured(mesg, GoalsRankResult)

def generate_choices(goals: List[dict],
                     goal_closeness: GoalsRankResult, 
                     current_node: StoryNodeResult,
                     current_knowlege: str, 
                     n_best: int, 
                     n_natural: int,
                     n_terminal: int
                     ) -> ChoicesResult:
    
    #select the n_best goal choices:
    g_best = sorted(goal_closeness.ranks, key = (lambda x: x.goal_closeness))
    g_best = [g.goal_id for g in g_best[:n_best]]
    filtered_goals = list(filter(
        lambda goal: goal['id'] in g_best,
        goals
    ))

    mesg = [
        {
            "role": "system",
            "content": textwrap.dedent(
                """The user is in a certain point in a choose your own adventure book. \
                The point they are at is described by their current node. \
                There is a list of goals which are some ways that the story could eventually end. The player is unaware of these goals unless they are present in the knowlege. \
                You must give some choices to the player, where each choices is a short description of what action the player might intend to do. \
                Some number of choices should get the player in some way slightly closer to a listed goal. \
                some number of choices should be natural extensions of where the player is, and may or may not progress the story towards the goals. \
                The further a player is from the goals, the more the natural choices should be information gathering of some sort. \
                Some number of choices should be terminal, which means taking the action would in some way terminate the story. \
                For each choice, only describe what the action the player would intend to do based on their knowlege. \
                For each choice, also give the success rate, between 0 and 1. 0 means it is difficult and would fail often, 1 would be easy and almost never fail. \
                Never tell the player how the action would actually play out. \
                And, never describe what the player's reasoning is for the action. \
                An example: 'explore the cavern on foot.' is better than 'explore the cavern on foot, hoping to find the treasure.'\
                """
            )
        },
        {
            "role": "system",
            "content": "current node: " + current_node.model_dump_json()
        },
        {
            "role": "user",
            "content": f"Here is what I know: {current_knowlege}"
        },
        {
            "role": "system",
            "content": "goals: " + json.dumps(goals)
        },
        {
            "role": "system",
            "content": f"Generate one choice that progresses towards each of these goals: {json.dumps(filtered_goals)}"
        },
        {
            "role": "system",
            "content": f"Generate {n_natural} choices that are natural."
        },
        {
            "role": "system",
            "content": f"Generate {n_terminal} choices that are terminal."
        },
        {
            "role": "assistant",
            "content": "To avoid giving away the story goals in my choices, I will ensure each choice is presented as a general action ra" +
            "ther than explicitly mentioning the goal it leads towards. For example, instead of saying 'find the boss's dinner" +
            " drink', I'll say something like 'investigate the dining hall.' Also, for natural extensions, I’ll provide action" +
            "s that fit logically with being at the start of an adventure without directly advancing any goals."
        }
    ]

    return call_llm_structured(mesg, ChoicesResult)
    result: ChoiceThoughtProcess = call_llm_structured(mesg, ChoiceThoughtProcess)
    pprint(result.thoughts)
    return result.result

def present_and_gather_choice(choices: ChoicesResult) -> str:

    #present the choices to the player:
    print(f"What do you do?:\n")
    for i, choice in enumerate(choices.choices):
        difficulty = "EASY"
        if choice.success_rate < 0.8:
            difficulty = "MEDIUM"
        if choice.success_rate < 0.4:
            difficulty = "HARD"
        if choice.success_rate < 0.2:
            difficulty = "IMPOSSIBLE"
        print(f"({i+1}): {choice.choice_description} ({difficulty})")

    player_choice = input(">>> ")
    while not player_choice.isnumeric() and (int(player_choice) < 1 or int(player_choice) > len(choices)):
        player_choice = input("Please use a number from the given choices.\n>>> ")

    return choices.choices[int(player_choice)-1]

def follow_choice(goals: List[dict], current_node: StoryNodeResult, knowlege: str, choice: SingleChoiceResult) -> Tuple[dict, str, str]:

    succeeded = random.random() <= choice.success_rate
    mesg = [
        {
            "role": "system",
            "content": textwrap.dedent(
                """The user is in a certain point in a choose your own adventure book. \
                The point they are at is described by their current node. \
                There is a list of goals which are some ways that the story could eventually end. \
                The action has chosen to try a certain action. \
                Return an object that describes where they end up after that action, \
                what new knowlege they have, and what happened when they performed the action. \
                also report whether it was successful or not.
                """
            )
        },
        {
            "role": "system",
            "content": "current node: " +  current_node.model_dump_json()
        },
        {
            "role": "system",
            "content": "goals: " + json.dumps(goals)
        },
        {
            "role": "user",
            "content": f"I know the following: {knowlege}"
        },
        {
            "role": "user",
            "content": f"I choose to attempt: {choice.choice_description}"
        },
        {
            "role": "system",
            "content": ("The action will succeed") if succeeded else ("The action will fail")
        }
    ]

    result: ActionResult = call_llm_structured(mesg, ActionResult)
    current_node = result.new_story_node
    knowlege += ";;" + result.knowlege

    #print(result.action_description)

    return (current_node, knowlege, result.action_description)

def describe_situation(current_node: dict, knowlege: str) -> None:
    print(f"Here is where you are in the story:")
    pprint(current_node)
    print(f"\nHere is what you know: \n{knowlege}")
# ------------ MAIN RUNTIME ------------

def main(story_prompt: str, verbose: bool = False) -> None:
    goals = [
        {
            "id": "key get",
            "description": "get a key from a room in the fortress that could be used to unlock the treasure room.",
        },
        {
            "id": "boss poison",
            "description": "find the boss's dinner drink before he has finished it, and add poison to it without being seen.",
        },
        {
            "id": "guard bribe",
            "description": "bribe a guard to show you into the treasure room.",
        },
        {
            "id": "fight guard",
            "description": "fight the guards of the treasure room, to force your way in.",
        },
    ]   

    current_node = {
        "id": "start adventure",
        "description": "you are standing outside the fortress, ready to begin the adventure"
    }
    current_node = StoryNodeResult(
        id=current_node['id'],
        description=current_node['description']
    )

    knowlege = "I am trying to break into a guarded building that is owned by a mob boss. I was sent by my agency to 'destroy their prospects'."

    while True:
        describe_situation(current_node=current_node,
                           knowlege=knowlege)
        print("Ranking goals...")
        goal_ranks = rank_goals(goals, current_node)
        if verbose:
            pprint(goal_ranks)

        print("\nCreating choices...")
        n_best = 0
        if max(goal_ranks.ranks, key=lambda r: r.goal_closeness).goal_closeness > 0.3:
            n_best = 2
        n_natural = random.randint(1, 3)
        n_terminal = 0#random.randint(0, 1)

        choices = generate_choices(
            goals,
            goal_closeness=goal_ranks,
            current_node=current_node,
            current_knowlege=knowlege,
            n_best=n_best,
            n_natural=n_natural,
            n_terminal=n_terminal
        )

        print('\n')
        
        player_choice = present_and_gather_choice(choices)

        print('\n')

        current_node, knowlege, action_result = follow_choice(
            goals=goals,
            current_node=current_node,
            knowlege=knowlege,
            choice=player_choice
            )
        
        print("This is what happened: ")
        print(action_result)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a choose-your-own-adventure style text rpg",
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
        default=False,
        type=bool,
        help="Describe whether to print out extra debug information"
    )

    args = parser.parse_args()

    main(story_prompt=args.story_prompt, verbose=args.verbose)