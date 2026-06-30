import pyxel
from game_core import run


def move_player(game):
    # Mission1: プレイヤーを動かそう
    pass


def shoot_bullet(game):
    # Mission2: 弾を撃てるようにしよう
    pass


def move_bullets(game):
    # Mission3: 弾を上に飛ばそう
    pass


def move_enemy(game, enemy):
    # Mission4: 敵を動かそう
    pass


def bullet_hits_enemy(game, bullet, enemy):
    # Mission5: 弾が敵に当たるようにしよう
    return False


run(
    {
        "move_player": move_player,
        "shoot_bullet": shoot_bullet,
        "move_bullets": move_bullets,
        "move_enemy": move_enemy,
        "bullet_hits_enemy": bullet_hits_enemy,
    }
)
