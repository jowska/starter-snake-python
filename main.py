# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing
import math
import copy

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data

# weight constants
WEIGHT_LENGTH = 0.1
WEIGHT_HEALTH = 0.2
WEIGHT_FOOD_DISTANCE = -0.3
WEIGHT_SPACE = 0.4
WEIGHT_CENTER_CONTROL = 0.2
WEIGHT_TRAP_OPPONENT = 0.5


def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",
        "color": "#E80978",
        "head": "beluga",
        "tail": "fat-rattle",
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:

    me = game_state["you"]
    my_head = game_state["you"]["body"][0]  # Coordinates of head
    my_neck = game_state["you"]["body"][1]  # Coordinates of neck
    my_length = len(me["body"])
    my_health = 100 - me['health']

    # my_body is list of all body coords, including head/tail
    my_body = game_state['you']['body']
    # Remove my_head from my_body list
    my_body.remove(my_head)

    left_head = {'x': my_head['x'] - 1, 'y': my_head['y']}
    right_head = {'x': my_head['x'] - 1, 'y': my_head['y']}
    up_head = {'x': my_head['x'], 'y': my_head['y'] + 1}
    down_head = {'x': my_head['x'], 'y': my_head['y'] - 1}

    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    food = game_state['board']['food']
    opponents = game_state['board']['snakes']

    def find_opponent():
        for opponent in opponents:
            if opponent['id'] != me['id']:
                return opponent

    opp = find_opponent()

    # find distance between 2 coords
    def calc_distance(c1, c2):
        return abs(c1['x'] - c2['x']) + abs(c2['y'] - c1['y'])

    # find where head would be at if we made a move
    def get_move_coordinate(move):
        if move == "left":
            return left_head
        if move == "right":
            return right_head
        if move == "up":
            return up_head
        if move == "down":
            return down_head

    def heuristic():
        length_score = my_length * WEIGHT_LENGTH
        health_score = my_health * WEIGHT_HEALTH
        food_score = min(calc_distance(my_head, pellet_pos)
                         for pellet_pos in food) * WEIGHT_FOOD_DISTANCE

        value = length_score + health_score + food_score
        return value

    def minimax(game_state, depth, maximizingPlayer):
        if depth == 0:
            return heuristic()
        if maximizingPlayer == True:  # opp
            max_eval = float('-inf')
            for child in get_child_states(maximizingPlayer):
                eval = minimax(child, depth - 1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        if maximizingPlayer == False:  # me
            min_eval = float('inf')
            for child in get_child_states(maximizingPlayer):
                eval = minimax(child, depth - 1, True)
                min_eval = min(min_eval, eval)
            return min_eval

    def get_child_states(is_maximizing_player):
        safe_moves = get_safe_moves()
        child_states = []

        for move in safe_moves:
            c_state = simulate_move(move, is_maximizing_player)
            child_states.append(c_state)

        return child_states

    def simulate_move(move, is_maximizing_player):
        n_state = copy.deepcopy(game_state)

        snake = None
        if is_maximizing_player:
            snake = me
        else:
            snake = opp

        # Update the snake's head position based on the move
        head = snake['body'][0]
        if move == 'up':
            new_head = {'x': head['x'], 'y': head['y'] - 1}
        elif move == 'down':
            new_head = {'x': head['x'], 'y': head['y'] + 1}
        elif move == 'left':
            new_head = {'x': head['x'] - 1, 'y': head['y']}
        elif move == 'right':
            new_head = {'x': head['x'] + 1, 'y': head['y']}

        # if head touches food, grow
        if new_head in n_state['board']['food']:
            n_state['you']['body'].insert(0, new_head)
            n_state['my_food'].remove(new_head)
        else:  # move snake
            snake['body'].insert(0, new_head)
            snake['body'].pop()

        return n_state

    def get_safe_moves():
        is_move_safe = {"up": True, "down": True, "left": True, "right": True}

        if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
            is_move_safe["left"] = False

        elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
            is_move_safe["right"] = False

        elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
            is_move_safe["down"] = False

        elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
            is_move_safe["up"] = False

        # Dodge left wall
        if my_head["x"] == 0:
            is_move_safe["left"] = False
        # Dodge right wall
        if my_head["x"] == board_width - 1:
            is_move_safe["right"] = False
        # Dodge bottom wall
        if my_head["y"] == 0:
            is_move_safe["down"] = False
        # Dodge top wall
        if my_head["y"] == board_height - 1:
            is_move_safe["up"] = False

        if left_head in my_body:
            is_move_safe["left"] = False
        if right_head in my_body:
            is_move_safe["right"] = False
        if up_head in my_body:
            is_move_safe["up"] = False
        if down_head in my_body:
            is_move_safe["down"] = False

        unsafe_coords = []

        for opp in opponents:
            # Remove ourself from opponents list
            if opp["name"] == "SnakeOne":
                opponents.remove(opp)
            # Get coordinates occupied by opp
            for coord in opp["body"]:
                unsafe_coords.append(coord)

        # Mark move unsafe if next to coord where an opp is
        for coord in unsafe_coords:
            if coord == left_head:
                is_move_safe["left"] = False
            if coord == right_head:
                is_move_safe["right"] = False
            if coord == up_head:
                is_move_safe["up"] = False
            if coord == down_head:
                is_move_safe["down"] = False

        # find safe moves
        safe_moves = []
        for move, isSafe in is_move_safe.items():
            if isSafe:
                safe_moves.append(move)

        return safe_moves

    safe_moves = get_safe_moves()

    """
    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']
                      }: No safe moves detected! Moving down")
        return {"move": "down"}
    """

    next_move = minimax(game_state, 3, False)

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
