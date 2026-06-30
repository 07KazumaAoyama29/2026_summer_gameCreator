import pyxel
from game_core import run


def move_player(game):
    if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT):
        game.player_x = max(game.player_x - game.PLAYER_SPEED, 0)
    if pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT):
        game.player_x = min(game.player_x + game.PLAYER_SPEED, game.WIDTH - game.PLAYER_W)
    if pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_UP):
        game.player_y = max(game.player_y - game.PLAYER_SPEED, 16)
    if pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN):
        game.player_y = min(game.player_y + game.PLAYER_SPEED, game.HEIGHT - game.PLAYER_H)


def shoot_bullet(game):
    if game.shot_cooldown > 0:
        game.shot_cooldown -= 1

    if pyxel.btn(pyxel.KEY_SPACE) and game.shot_cooldown == 0:
        game.add_bullet(
            game.player_x + game.PLAYER_W // 2 - game.BULLET_W // 2,
            game.player_y - 6,
        )
        game.shot_cooldown = 6


def move_bullets(game):
    for bullet in game.bullets:
        bullet["y"] -= game.BULLET_SPEED


def move_enemy(game, enemy):
    enemy["y"] += enemy["speed"]
    enemy["x"] += enemy["vx"]

    if enemy["x"] <= 0 or enemy["x"] >= game.WIDTH - game.ENEMY_W:
        enemy["vx"] *= -1


def bullet_hits_enemy(game, bullet, enemy):
    return game.hit_box(
        bullet["x"], bullet["y"], game.BULLET_W, game.BULLET_H,
        enemy["x"], enemy["y"], game.ENEMY_W, game.ENEMY_H,
    )


run(
    {
        "move_player": move_player,
        "shoot_bullet": shoot_bullet,
        "move_bullets": move_bullets,
        "move_enemy": move_enemy,
        "bullet_hits_enemy": bullet_hits_enemy,
    }
)
