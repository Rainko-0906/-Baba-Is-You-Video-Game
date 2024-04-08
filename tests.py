from game import *
from actor import *
import pytest
import pygame
import os

# USE PYGAME VARIABLES INSTEAD
keys_pressed = [0] * 323

# Setting key constants because of issue on devices
pygame.K_RIGHT = 1
pygame.K_DOWN = 2
pygame.K_LEFT = 3
pygame.K_UP = 4
pygame.K_LCTRIL = 5
pygame.K_z = 6
RIGHT = pygame.K_RIGHT
DOWN = pygame.K_DOWN
LEFT = pygame.K_LEFT
UP = pygame.K_UP
CTRL = pygame.K_LCTRL
Z = pygame.K_z


def setup_map(map: str) -> 'Game':
    """Returns a game with map1"""
    game = Game()
    game.new()
    game.load_map(os.path.abspath(os.getcwd()) + '/maps/' + map)
    game.new()
    game._update()
    game.keys_pressed = keys_pressed
    return game


def set_keys(up, down, left, right, CTRL=0, Z=0):
    keys_pressed[pygame.K_UP] = up
    keys_pressed[pygame.K_DOWN] = down
    keys_pressed[pygame.K_LEFT] = left
    keys_pressed[pygame.K_RIGHT] = right


def test1_move_player_up():
    """
    Check if player is moved up correctly
    """
    game = setup_map("student_map1.txt")
    set_keys(1, 0, 0, 0)
    result = game.player.player_move(game)
    assert result == True
    assert game.player.y == 1
    assert game.player.x == 6


def test1_false_to_move_player_up():
    """
    Check if player is false to moved up
    """
    game = setup_map("student_map2.txt")
    set_keys(1, 0, 0, 0)
    result = game.player.player_move(game)
    assert result == False
    assert game.player.y == 1
    assert game.player.x == 2


def test1_move_player_down():
    """
    Check if player is moved down correctly
    """
    game = setup_map("student_map5.txt")
    set_keys(0, 1, 0, 0)
    result = game.player.player_move(game)
    assert result == True
    assert game.player.y == 3
    assert game.player.x == 5


def test1_false_to_move_player_down():
    """
    Check if player is false to moved down
    """
    game = setup_map("student_map1.txt")
    set_keys(0, 1, 0, 0)
    result = game.player.player_move(game)
    assert result == False
    assert game.player.y == 2
    assert game.player.x == 6


def test1_move_player_left():
    """
    Check if player is moved left correctly
    """
    game = setup_map("student_map1.txt")
    set_keys(0, 0, 1, 0)
    result = game.player.player_move(game)
    assert result == True
    assert game.player.x == 5
    assert game.player.y == 2


def test1_false_to_move_player_left():
    """
    Check if player is false to moved left
    """
    game = setup_map("student_map3.txt")
    set_keys(0, 0, 1, 0)
    result = game.player.player_move(game)
    assert result == False
    assert game.player.x == 1
    assert game.player.y == 1


def test1_move_player_right():
    """
    Check if player is moved right correctly
    """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 0, 1)
    result = game.player.player_move(game)
    assert result == True
    assert game.player.x == 3
    assert game.player.y == 1


def test1_false_to_move_player_right():
    """
    Check if player is false to moved right
    """
    game = setup_map("student_map1.txt")
    set_keys(0, 0, 0, 1)
    result = game.player.player_move(game)
    assert result == False
    assert game.player.x == 6
    assert game.player.y == 2


def test2_push_block():
    """
    Check if player pushes block correctly
    """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 0, 1)
    wall = \
        [i for i in game._actors if isinstance(i, Block) and i.word == "Wall"][
            0]
    result = game.player.player_move(game)
    assert result == True
    assert game.player.x == 3
    assert wall.x == 4


def test3_create_rule_wall_is_push():
    """
    Check if player creates wall is push rule correctly
    """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 0, 1)
    wall = \
        [i for i in game._actors if isinstance(i, Block) and i.word == "Wall"][
            0]
    result = game.player.player_move(game)
    game._update()
    assert game._rules[0] == "Wall isPush"
    assert game.player.x == 3
    assert wall.x == 4
    assert result == True


def test_create_flag_is_win():
    """
    Check if player creates the rule of "Flag isVictory" correctly
    """
    game = setup_map("student_map5.txt")

    flag = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Subject) and ac.word == SUBJECTS["F"]:
            flag = ac
    flag.x, flag.y = 1, 1

    is_list = []
    for ac2 in game.get_actors():
        if isinstance(ac2, actor.Is):
            is_list.append(ac2)
    is_block = is_list[0]
    is_block.x, is_block.y = 2, 1

    victor = None
    for ac3 in game.get_actors():
        if isinstance(ac3, actor.Attribute) and ac3.word == ATTRIBUTES["V"]:
            victor = ac3
    victor.x, victor.y = 3, 1

    game._update()
    assert "Flag isVictory" in game.get_rules()


def test_create_wall_is_win():
    """
    Check if player creates the rule of "Wall isVictory" correctly
    """
    game = setup_map("student_map5.txt")

    wall = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Subject) and ac.word == SUBJECTS["W"]:
            wall = ac
    wall.x, wall.y = 1, 1

    is_list = []
    for ac2 in game.get_actors():
        if isinstance(ac2, actor.Is):
            is_list.append(ac2)
    is_block = is_list[0]
    is_block.x, is_block.y = 2, 1

    victor = None
    for ac3 in game.get_actors():
        if isinstance(ac3, actor.Attribute) and ac3.word == ATTRIBUTES["V"]:
            victor = ac3
    victor.x, victor.y = 3, 1

    game._update()
    assert "Wall isVictory" in game.get_rules()


def test_create_wall_is_you():
    """
    Check if player creates the rule of "Wall isYou" correctly
    """
    game = setup_map("student_map5.txt")

    wall = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Subject) and ac.word == SUBJECTS["W"]:
            wall = ac
    wall.x, wall.y = 1, 1

    is_list = []
    for ac2 in game.get_actors():
        if isinstance(ac2, actor.Is):
            is_list.append(ac2)
    is_block = is_list[0]
    is_block.x, is_block.y = 2, 1

    victor = None
    for ac3 in game.get_actors():
        if isinstance(ac3, actor.Attribute) and ac3.word == ATTRIBUTES["Y"]:
            victor = ac3
    victor.x, victor.y = 3, 1

    wall_obj = None
    for ac4 in game.get_actors():
        if isinstance(ac4, actor.Wall):
            wall_obj = ac4

    game._update()
    assert "Wall isYou" in game.get_rules()
    assert type(wall_obj) == type(game.player)


def test_create_flag_is_you():
    """
    Check if player creates the rule of "Flag isYou" correctly
    """
    game = setup_map("student_map5.txt")

    flag = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Subject) and ac.word == SUBJECTS["F"]:
            flag = ac
    flag.x, flag.y = 1, 1

    is_list = []
    for ac2 in game.get_actors():
        if isinstance(ac2, actor.Is):
            is_list.append(ac2)
    is_block = is_list[0]
    is_block.x, is_block.y = 2, 1

    victor = None
    for ac3 in game.get_actors():
        if isinstance(ac3, actor.Attribute) and ac3.word == ATTRIBUTES["Y"]:
            victor = ac3
    victor.x, victor.y = 3, 1

    flag_obj = None
    for ac4 in game.get_actors():
        if isinstance(ac4, actor.Flag):
            flag_obj = ac4

    game._update()
    assert "Flag isYou" in game.get_rules()
    assert game.player == flag_obj


def test_create_rock_is_win():
    """
    Check if player creates the rule of "Rock isVictory" correctly
    """
    game = setup_map("student_map5.txt")

    rock = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Subject) and ac.word == SUBJECTS["R"]:
            rock = ac
    rock.x, rock.y = 1, 1

    is_list = []
    for ac2 in game.get_actors():
        if isinstance(ac2, actor.Is):
            is_list.append(ac2)
    is_block = is_list[0]
    is_block.x, is_block.y = 2, 1

    victor = None
    for ac3 in game.get_actors():
        if isinstance(ac3, actor.Attribute) and ac3.word == ATTRIBUTES["V"]:
            victor = ac3
    victor.x, victor.y = 3, 1

    game._update()
    assert "Rock isVictory" in game.get_rules()


def test_create_rock_is_you():
    """
    Check if player creates the rule of "Rock isYou" correctly
    """
    game = setup_map("student_map5.txt")

    rock = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Subject) and ac.word == SUBJECTS["R"]:
            rock = ac
    rock.x, rock.y = 1, 1

    is_list = []
    for ac2 in game.get_actors():
        if isinstance(ac2, actor.Is):
            is_list.append(ac2)
    is_block = is_list[0]
    is_block.x, is_block.y = 2, 1

    victor = None
    for ac3 in game.get_actors():
        if isinstance(ac3, actor.Attribute) and ac3.word == ATTRIBUTES["Y"]:
            victor = ac3
    victor.x, victor.y = 3, 1

    rock_obj = None
    for ac4 in game.get_actors():
        if isinstance(ac4, actor.Rock):
            rock_obj = ac4

    game._update()
    assert "Rock isYou" in game.get_rules()
    assert game.player == rock_obj


def test_create_meepo_is_win():
    """
    Check if player creates the rule of "Meepo isVictory" correctly
    """
    game = setup_map("student_map5.txt")

    meepo = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Subject) and ac.word == SUBJECTS["M"]:
            meepo = ac
    meepo.x, meepo.y = 1, 1

    is_list = []
    for ac2 in game.get_actors():
        if isinstance(ac2, actor.Is):
            is_list.append(ac2)
    is_block = is_list[0]
    is_block.x, is_block.y = 2, 1

    victor = None
    for ac3 in game.get_actors():
        if isinstance(ac3, actor.Attribute) and ac3.word == ATTRIBUTES["V"]:
            victor = ac3
    victor.x, victor.y = 3, 1

    game._update()
    assert "Meepo isVictory" in game.get_rules()


def test_create_flag_is_lose():
    """
    Check if player creates the rule of "Flag isLose" correctly
    """
    game = setup_map("student_map5.txt")

    flag = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Subject) and ac.word == SUBJECTS["F"]:
            flag = ac
    flag.x, flag.y = 1, 1

    is_list = []
    for ac2 in game.get_actors():
        if isinstance(ac2, actor.Is):
            is_list.append(ac2)
    is_block = is_list[0]
    is_block.x, is_block.y = 2, 1

    victor = None
    for ac3 in game.get_actors():
        if isinstance(ac3, actor.Attribute) and ac3.word == ATTRIBUTES["L"]:
            victor = ac3
    victor.x, victor.y = 3, 1

    game._update()
    assert "Flag isLose" in game.get_rules()


def test_create_wall_is_lose():
    """
    Check if player creates the rule of "Wall isLose" correctly
    """
    game = setup_map("student_map5.txt")

    wall = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Subject) and ac.word == SUBJECTS["W"]:
            wall = ac
    wall.x, wall.y = 1, 1

    is_list = []
    for ac2 in game.get_actors():
        if isinstance(ac2, actor.Is):
            is_list.append(ac2)
    is_block = is_list[0]
    is_block.x, is_block.y = 2, 1

    victor = None
    for ac3 in game.get_actors():
        if isinstance(ac3, actor.Attribute) and ac3.word == ATTRIBUTES["L"]:
            victor = ac3
    victor.x, victor.y = 3, 1

    game._update()
    assert "Wall isLose" in game.get_rules()


def test_create_rock_is_lose():
    """
    Check if player creates the rule of "Rock isLose" correctly
    """
    game = setup_map("student_map5.txt")

    rock = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Subject) and ac.word == SUBJECTS["R"]:
            rock = ac
    rock.x, rock.y = 1, 1

    is_list = []
    for ac2 in game.get_actors():
        if isinstance(ac2, actor.Is):
            is_list.append(ac2)
    is_block = is_list[0]
    is_block.x, is_block.y = 2, 1

    victor = None
    for ac3 in game.get_actors():
        if isinstance(ac3, actor.Attribute) and ac3.word == ATTRIBUTES["L"]:
            victor = ac3
    victor.x, victor.y = 3, 1

    game._update()
    assert "Rock isLose" in game.get_rules()


def test_create_meepo_is_lose():
    """
    Check if player creates the rule of "Meepo isLose" correctly
    """
    game = setup_map("student_map5.txt")

    meepo = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Subject) and ac.word == SUBJECTS["M"]:
            meepo = ac
    meepo.x, meepo.y = 1, 1

    is_list = []
    for ac2 in game.get_actors():
        if isinstance(ac2, actor.Is):
            is_list.append(ac2)
    is_block = is_list[0]
    is_block.x, is_block.y = 2, 1

    victor = None
    for ac3 in game.get_actors():
        if isinstance(ac3, actor.Attribute) and ac3.word == ATTRIBUTES["L"]:
            victor = ac3
    victor.x, victor.y = 3, 1

    game._update()
    assert "Meepo isLose" in game.get_rules()


def test_4_follow_rule_wall_is_push():
    """
    Check if player follows rules correctly
    """
    game = setup_map("student_map3.txt")
    set_keys(0, 0, 0, 1)
    wall_object = game._actors[game._actors.index(game.player) + 1]
    result = game.player.player_move(game)
    assert game.player.x == 2
    assert wall_object.x == 3
    assert result == True


def test_follow_rule_rock_is_stop():
    """
    Check if player is stopped because of the unmovable Rock
    """
    game = setup_map("student_map5.txt")
    game.player.y = 3
    set_keys(0, 1, 0, 0)
    rock_object = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Rock):
            rock_object = ac
    result = game.player.player_move(game)
    assert game.player.y == 3
    assert rock_object.y == 4


def test_follow_rule_meepo_is_you():
    """
    Check if the player is set to Meepo correctly
    """
    game = setup_map("student_map5.txt")
    curr_player = None
    for ac in game.get_actors():
        if isinstance(ac, actor.Meepo):
            curr_player = ac
    assert game.player == curr_player


def test_5_no_push():
    """
    Check if player is not able to push because of rule not existing
    """
    game = setup_map("student_map4.txt")
    set_keys(0, 0, 0, 1)
    wall_object = game._actors[game._actors.index(game.player) + 1]
    result = game.player.player_move(game)
    assert game.player.x == 2
    assert wall_object.x == 2


def test_undo():
    """
    Check if undo works correctly
    """
    game = setup_map("student_map4.txt")
    game2 = setup_map("student_map5.txt")
    game._history.push(game2)
    game._undo()
    assert game._history.is_empty() == True


def test_after_undo():
    """
    Check if everything still works after undo
    """
    game = setup_map("student_map5.txt")
    game2 = setup_map("student_map4.txt")
    game._history.push(game2)
    game._undo()
    test_create_flag_is_win()
    test_create_flag_is_lose()
    test_create_flag_is_you()
    test_create_wall_is_win()
    test_create_wall_is_lose()
    test_create_wall_is_you()
    test_create_rock_is_win()
    test_create_rock_is_lose()
    test_create_rock_is_you()
    test_create_meepo_is_win()
    test_create_meepo_is_lose()
    test_follow_rule_meepo_is_you()


if __name__ == "__main__":
    import pytest

    pytest.main(['student_tests.py'])
