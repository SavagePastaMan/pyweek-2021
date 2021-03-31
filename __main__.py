import time
from typing import Optional

import utils

from constants import *

import arcade
from pyglet.gl import GL_NEAREST

from entity.cabinet import Cabinet
from entity.enemy import Enemy
from entity.player import Player

from item.key import Key

from music_player import MusicPlayer


class GameView(arcade.View):
    def __init__(self, window):
        super().__init__(window)
        self.wall_list: Optional[arcade.SpriteList] = None
        self.floor_list: Optional[arcade.SpriteList] = None
        self.interactable_list: Optional[arcade.SpriteList] = None
        self.enemy_list: Optional[arcade.SpriteList] = None
        self.player: Optional[Player] = None

        self.music_player = MusicPlayer()

    def setup(self):
        self.load_map()

        # Set up the player
        self.player = Player()

        # Starting position of the player
        self.player.center_x, self.player.center_y = utils.center_of_tile(530, 700)

        cabinet = Cabinet(content=Key())
        cabinet.center_x, cabinet.center_y = utils.center_of_tile(135, 300)
        self.interactable_list = arcade.SpriteList()
        self.interactable_list.append(cabinet)

        self.set_viewport_on_player()

    def load_map(self):

        # Process Tile Map
        tile_map = arcade.tilemap.read_tmx(f"assets/tilemaps/TestLevel.tmx")
        utils.map_height = tile_map.map_size[1]

        # Tile Layers
        self.wall_list = arcade.tilemap.process_layer(
            tile_map, "walls", TILE_SPRITE_SCALING, use_spatial_hash=True
        )

        self.floor_list = arcade.tilemap.process_layer(
            tile_map, "floor", TILE_SPRITE_SCALING, use_spatial_hash=True
        )

        # Object Layers
        self.object_layers = utils.process_objects(f"assets/tilemaps/TestLevel.tmx")

        self.enemy_list = arcade.SpriteList()
        for object_layer in self.object_layers:
            guard_location = utils.extract_guard_locations(object_layer)
            self.enemy_list.append(Enemy(self.wall_list, guard_location))


    def on_key_press(self, key: int, modifiers: int):
        if key in [arcade.key.UP, arcade.key.LEFT, arcade.key.RIGHT, arcade.key.DOWN]:
            # Record Original Pos so if collision with wall is detected, we return the
            # player to that spot before rendering, making it impassable.
            original_pos = (self.player.center_x, self.player.center_y)
            self.player.handle_user_input(key, modifiers)
            if arcade.check_for_collision_with_list(self.player, self.wall_list):
                self.player.center_x, self.player.center_y = original_pos
            else:
                self.enemy_list.update()

            self.set_viewport_on_player()

    def set_viewport_on_player(self):
        """
        Set the viewport to be over the player. If the Viewport would display the outside blackness,
        it is clamped with the game map.
        :return:
        """
        clamped_x = min(
            SCREEN_WIDTH, max(0, self.player.center_x - HORIZONTAL_VIEWPORT_MARGIN),
        )
        clamped_y = min(
            SCREEN_HEIGHT, max(0, self.player.center_y - VERTICAL_VIEWPORT_MARGIN),
        )
        arcade.set_viewport(
            clamped_x, SCREEN_WIDTH + clamped_x, clamped_y, SCREEN_HEIGHT + clamped_y
        )

    def on_update(self, delta_time: float):
        for interactable in arcade.check_for_collision_with_list(
            self.player, self.interactable_list
        ):
            interactable.interact(self.player)

        self.player.update()

        self.music_player.update()

    def on_draw(self):
        arcade.start_render()

        # GL_NEAREST makes scaled Pixel art look cleaner
        self.wall_list.draw(filter=GL_NEAREST)
        self.floor_list.draw(filter=GL_NEAREST)
        self.interactable_list.draw(filter=GL_NEAREST)

        self.enemy_list.draw(filter=GL_NEAREST)
        for enemy in self.enemy_list:
            enemy.draw_path()
        self.player.draw()


def main():
    main_window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    game_view = GameView(main_window)
    game_view.setup()

    main_window.show_view(game_view)

    arcade.run()


if __name__ == "__main__":
    main()
