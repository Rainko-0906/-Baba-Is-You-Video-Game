"""
Assignment 1: Meepo is You

=== CSC148 Winter 2021 ===
Department of Mathematical and Computational Sciences,
University of Toronto Mississauga

=== Module Description ===
This module contains the Game class and the main game application.
"""

from typing import Any, Type, Tuple, List, Sequence, Optional
import pygame
from settings import *
from stack import Stack
import actor


class Game:
    """
    Class representing the game.
    """
    size: Tuple[int, int]
    width: int
    height: int
    screen: Optional[pygame.Surface]
    x_tiles: int
    y_tiles: int
    tiles_number: Tuple[int, int]
    background: Optional[pygame.Surface]

    _actors: List[actor.Actor]
    _is: List[actor.Is]
    _running: bool
    _rules: List[str]
    _history: Stack()

    player: Optional[actor.Actor]
    map_data: List[str]
    keys_pressed: Optional[Sequence[bool]]

    def __init__(self) -> None:
        """
        Initialize variables for this Class.
        """
        self.width, self.height = 0, 0
        self.size = (self.width, self.height)
        self.screen = None
        self.x_tiles, self.y_tiles = (0, 0)
        self.tiles_number = (self.x_tiles, self.y_tiles)
        self.background = None

        self._actors = []
        self._is = []
        self._rules = []
        self._running = True
        self._history = Stack()

        self.player = None
        self.map_data = []
        self.keys_pressed = None

    def load_map(self, path: str) -> None:
        """
        Reads a .txt file representing the map
        """
        with open(path, 'rt') as f:
            for line in f:
                self.map_data.append(line.strip())

        self.width = (len(self.map_data[0])) * TILESIZE
        self.height = len(self.map_data) * TILESIZE
        self.size = (self.width, self.height)
        self.x_tiles, self.y_tiles = len(self.map_data[0]), len(self.map_data)

        # center the window on the screen
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def new(self) -> None:
        """
        Initialize variables to be object on screen.
        """
        self.screen = pygame.display.set_mode(self.size)
        self.background = pygame.image.load(
            "{}/backgroundBig.png".format(SPRITES_DIR)).convert_alpha()
        for col, tiles in enumerate(self.map_data):
            for row, tile in enumerate(tiles):
                if tile.isnumeric():
                    self._actors.append(
                        Game.get_character(CHARACTERS[tile])(row, col))
                elif tile in SUBJECTS:
                    self._actors.append(
                        actor.Subject(row, col, SUBJECTS[tile]))
                elif tile in ATTRIBUTES:
                    self._actors.append(
                        actor.Attribute(row, col, ATTRIBUTES[tile]))
                elif tile == 'I':
                    is_tile = actor.Is(row, col)
                    self._is.append(is_tile)
                    self._actors.append(is_tile)

    def get_actors(self) -> List[actor.Actor]:
        """
        Getter for the list of actors
        """
        return self._actors

    def get_running(self) -> bool:
        """
        Getter for _running
        """
        return self._running

    def get_rules(self) -> List[str]:
        """
        Getter for _rules
        """
        return self._rules

    def _draw(self) -> None:
        """
        Draws the screen, grid, and objects/players on the screen
        """
        self.screen.blit(self.background,
                         (((0.5 * self.width) - (0.5 * 1920),
                           (0.5 * self.height) - (0.5 * 1080))))
        for actor_ in self._actors:
            rect = pygame.Rect(actor_.x * TILESIZE,
                               actor_.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(actor_.image, rect)

        # Blit the player at the end to make it above all other objects
        if self.player:
            rect = pygame.Rect(self.player.x * TILESIZE,
                               self.player.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(self.player.image, rect)

        pygame.display.flip()

    def _events(self) -> None:
        """
        Event handling of the game window
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            # Allows us to make each press count as 1 movement.
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed = pygame.key.get_pressed()
                ctrl_held = self.keys_pressed[pygame.K_LCTRL]

                # handle undo button and player movement here
                if event.key == pygame.K_z and ctrl_held:  # Ctrl-Z
                    self._undo()
                else:
                    if self.player is not None:
                        assert isinstance(self.player, actor.Character)
                        save = self._copy()
                        if self.player.player_move(self) \
                                and not self.win_or_lose():
                            self._history.push(save)
        return

    def win_or_lose(self) -> bool:
        """
        Check if the game has won or lost
        Returns True if the game is won or lost; otherwise return False
        """
        assert isinstance(self.player, actor.Character)
        for ac in self._actors:
            if isinstance(ac, actor.Character) \
                    and ac.x == self.player.x and ac.y == self.player.y:
                if ac.is_win():
                    self.win()
                    return True
                elif ac.is_lose():
                    self.lose(self.player)
                    return True
        return False

    def run(self) -> None:
        """
        Run the Game until it ends or player quits.
        """
        while self._running:
            pygame.time.wait(1000 // FPS)
            self._events()
            self._update()
            self._draw()

    def set_player(self, actor_: Optional[actor.Actor]) -> None:
        """
        Takes an actor and sets that actor to be the player
        """
        self.player = actor_

    def remove_player(self, actor_: actor.Actor) -> None:
        """
        Remove the given <actor> from the game's list of actors.
        """
        self._actors.remove(actor_)
        self.player = None

    def _update(self) -> None:
        """
        Check each "Is" tile to find what rules are added and which are removed
        if any, and handle them accordingly.
        """
        new_rules = []
        for is_block in self._is:
            up, down, left, right = self.get_surround_ac(is_block)
            horizontal, vertical = is_block.update(up, down, left, right)
            for rule in [horizontal, vertical]:
                if rule and new_rules.count(rule) == 0:
                    new_rules.append(rule)

        for rule in self._rules:
            if rule not in new_rules:
                self.apply_removal_rule(rule)

        for rule in new_rules:
            if rule not in self._rules:
                self.apply_additional_rule(rule)

        self._rules = new_rules

    @staticmethod
    def get_character(subject: str) -> Optional[Type[Any]]:
        """
        Takes a string, returns appropriate class representing that string
        """
        if subject == "Meepo":
            return actor.Meepo
        elif subject == "Wall":
            return actor.Wall
        elif subject == "Rock":
            return actor.Rock
        elif subject == "Flag":
            return actor.Flag
        elif subject == "Bush":
            return actor.Bush
        return None

    def _undo(self) -> None:
        """
        Returns the game to a previous state based on what is at the top of the
        _history stack.
        """
        if not self._history.is_empty():
            game_copy = self._history.pop()
            self._actors = game_copy.get_actors()
            self._is = []
            for is_is in self._actors:
                if isinstance(is_is, actor.Is):
                    self._is.append(is_is)
            self._rules = game_copy.get_rules()
            self._running = game_copy.get_running()
            self.player = game_copy.player
            self.map_data = game_copy.map_data
            self.keys_pressed = game_copy.keys_pressed
            old_player = self.player
            self.player = None
            for ac in self._actors:
                if isinstance(ac, type(old_player)):
                    self.player = ac
                    break
            assert isinstance(self.player, actor.Character)
        return

    def _copy(self) -> 'Game':
        """
        Copies relevant attributes of the game onto a new instance of Game.
        Return new instance of game
        """
        game_copy = Game()
        for ac in self._actors:
            game_copy._actors.append(ac.copy())
        for is_block in self._is:
            game_copy._is.append(is_block.copy())
        for rule in self._rules:
            game_copy._rules.append(rule[:])
        game_copy._running = self._running
        game_copy.player = self.player.copy()
        game_copy.map_data = self.map_data
        game_copy.keys_pressed = self.keys_pressed

        return game_copy

    def get_actor(self, x: int, y: int) -> Optional[actor.Actor]:
        """
        Return the actor at the position x,y. If the slot is empty, Return None
        """
        for ac in self._actors:
            if ac.x == x and ac.y == y:
                return ac
        return None

    def win(self) -> None:
        """
        End the game and print win message.
        """
        self._running = False
        print("Congratulations, you won!")

    def lose(self, char: actor.Character) -> None:
        """
        Lose the game and print lose message
        """
        self.remove_player(char)
        print("You lost! But you can have it undone if undo is done :)")

    def get_surround_ac(self, curr_actor: actor.Actor) -> List:
        """
        Return the surrounding actors of given actor.
        if actor not exists, return None.
        """
        up = self.get_actor(curr_actor.x, curr_actor.y - 1)
        down = self.get_actor(curr_actor.x, curr_actor.y + 1)
        left = self.get_actor(curr_actor.x - 1, curr_actor.y)
        right = self.get_actor(curr_actor.x + 1, curr_actor.y)
        return [up, down, left, right]

    def apply_removal_rule(self, rule) -> None:
        """
        Remove the given rule from the game.
        """
        subject, attribute = rule.split()
        for ac in self.get_actors():
            if isinstance(ac, self.get_character(subject)):
                if attribute[2:] == ATTRIBUTES["P"]:
                    ac.unset_push()
                elif attribute[2:] == ATTRIBUTES["S"]:
                    ac.unset_stop()
                elif attribute[2:] == ATTRIBUTES["V"]:
                    ac.unset_win()
                elif attribute[2:] == ATTRIBUTES["L"]:
                    ac.unset_lose()
                elif attribute[2:] == ATTRIBUTES["Y"]:
                    if ac.is_player():
                        ac.unset_player()
                        self.player = None

    def apply_additional_rule(self, rule) -> None:
        """
        Apply the given rules to the game.
        """
        subject, attribute = rule.split()
        for ac in self.get_actors():
            if isinstance(ac, self.get_character(subject)):
                if attribute[2:] == ATTRIBUTES["P"]:
                    ac.set_push()
                elif attribute[2:] == ATTRIBUTES["S"]:
                    ac.set_stop()
                elif attribute[2:] == ATTRIBUTES["V"]:
                    ac.set_win()
                elif attribute[2:] == ATTRIBUTES["L"]:
                    ac.set_lose()
                elif attribute[2:] == ATTRIBUTES["Y"]:
                    ac.set_player()
                    self.set_player(ac)


if __name__ == "__main__":
    game = Game()
    # load_map public function
    game.load_map(MAP_PATH)
    game.new()
    game.run()

    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ['settings', 'stack', 'actor', 'pygame']
    # })
