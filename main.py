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

import typing
import copy
import random

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data

# weight constants
WEIGHT_LENGTH = 0.1
WEIGHT_HEALTH = 0.2
WEIGHT_FOOD_DISTANCE = -0.3


def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",
        "color": "#E80978",
        "head": "beluga",
        "tail": "fat-rattle",
    }


def start(game_state: typing.Dict):
    print("GAME START")


def end(game_state: typing.Dict):
    print("GAME OVER\n")


def move(game_state: typing.Dict) -> typing.Dict:
    me = game_state["you"]
    my_head = game_state["you"]["body"][0]  # Coordinates of head
    my_neck = game_state["you"]["body"][1]  # Coordinates of neck
    my_length = len(me["body"])
    my_health = 100 - me['health']
    my_body = me['body'][1:]

    left_head = {'x': my_head['x'] - 1, 'y': my_head['y']}
    right_head = {'x': my_head['x'] + 1, 'y': my_head['y']}
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

    def heuristic():
        length_score = my_length * WEIGHT_LENGTH
        health_score = my_health * WEIGHT_HEALTH
        closest_food_distance = min(calc_distance(
            my_head, pellet) for pellet in food) if food else 0
        food_score = -closest_food_distance * WEIGHT_FOOD_DISTANCE
        return length_score + health_score + food_score

    def minimax(game_state, depth, maximizingPlayer, alpha=float('-inf'), beta=float('inf')):
        if depth == 0:
            return heuristic()
        if maximizingPlayer:  # opp
            max_eval = float('-inf')
            for child in get_child_states(maximizingPlayer):
                eval = minimax(child, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:  # me
            min_eval = float('inf')
            for child in get_child_states(maximizingPlayer):
                eval = minimax(child, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_child_states(is_maximizing_player):
        safe_moves = get_safe_moves()
        return [simulate_move(move, is_maximizing_player) for move in safe_moves]

    def simulate_move(move, is_maximizing_player):
        new_state = copy.deepcopy(game_state)
        snake = new_state['you'] if not is_maximizing_player else next(
            (s for s in new_state['board']['snakes'] if s['id'] != new_state['you']['id']), None)

        if snake is None:
            return new_state

        move_offsets = {'up': (0, -1), 'down': (0, 1),
                        'left': (-1, 0), 'right': (1, 0)}
        offset = move_offsets[move]
        new_head = {'x': snake['body'][0]['x'] + offset[0],
                    'y': snake['body'][0]['y'] + offset[1]}

        if new_head in new_state['board']['food']:
            snake['body'].insert(0, new_head)
            new_state['board']['food'].remove(new_head)
        else:
            snake['body'].insert(0, new_head)
            snake['body'].pop()

        return new_state

    def get_safe_moves():
        is_move_safe = {"up": True, "down": True, "left": True, "right": True}

        if opp:
            # Add potential positions for the opponent's head
            opp_head = opp['body'][0]
            potential_opp_moves = [
                {'x': opp_head['x'] - 1, 'y': opp_head['y']},
                {'x': opp_head['x'] + 1, 'y': opp_head['y']},
                {'x': opp_head['x'], 'y': opp_head['y'] - 1},
                {'x': opp_head['x'], 'y': opp_head['y'] + 1}
            ]

            # Get the entire body of the opponent
            opp_body = opp['body']

            # Update is_move_safe based on potential opponent moves, own body, and opponent's body
            if left_head in potential_opp_moves or left_head in my_body or left_head in opp_body:
                is_move_safe["left"] = False
            if right_head in potential_opp_moves or right_head in my_body or right_head in opp_body:
                is_move_safe["right"] = False
            if up_head in potential_opp_moves or up_head in my_body or up_head in opp_body:
                is_move_safe["up"] = False
            if down_head in potential_opp_moves or down_head in my_body or down_head in opp_body:
                is_move_safe["down"] = False

        # Prevent moving backwards
        if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
            is_move_safe["left"] = False
        elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
            is_move_safe["right"] = False
        elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
            is_move_safe["down"] = False
        elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
            is_move_safe["up"] = False

        # Avoid board edges
        if my_head["x"] == 0:
            is_move_safe["left"] = False
        if my_head["x"] == board_width - 1:
            is_move_safe["right"] = False
        if my_head["y"] == 0:
            is_move_safe["down"] = False
        if my_head["y"] == board_height - 1:
            is_move_safe["up"] = False

        # Find safe moves
        safe_moves = [move for move,
                      is_safe in is_move_safe.items() if is_safe]
        return safe_moves

    def choose_best_move(state, depth):
        best_moves = []
        best_score = float('-inf')
        for move in get_safe_moves():
            child_state = simulate_move(move, True)
            score = minimax(child_state, depth, False)
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        chosen_move = random.choice(best_moves) if best_moves else None
        return chosen_move

    next_move = choose_best_move(game_state, 4)
    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
