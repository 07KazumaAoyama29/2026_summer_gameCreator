import pyxel
from pathlib import Path
from random import randint


WIDTH = 320
HEIGHT = 240

CHARACTER_SIZE = 32
EFFECT_SIZE = 16
LIFE_SIZE = 16

PLAYER_W = CHARACTER_SIZE
PLAYER_H = CHARACTER_SIZE
PLAYER_SPEED = 4

BULLET_W = 6
BULLET_H = 12
BULLET_DRAW_W = 8
BULLET_DRAW_H = 16
BULLET_SPEED = 8

ENEMY_W = CHARACTER_SIZE
ENEMY_H = CHARACTER_SIZE
BOSS_W = 128
BOSS_H = 128
BOSS_SCORE = 300
BOSS_HP = 24
BOSS_TIME_LIMIT = 60 * 30

PLAYER_U = 0
PLAYER_V = 0
ENEMY_U = [32, 64, 96]
ENEMY_V = 0
BULLET_U = 128
BULLET_V = 0
SPARK_U = 144
SPARK_V = 0
LIFE_U = 160
LIFE_V = 0
BURST_U = 176
BURST_V = 0
BOSS_BULLET_U = 192
BOSS_BULLET_V = 0
BOSS_U = 0
BOSS_V = 64
TRANSPARENT_COLOR = 0

BOSS_BULLET_W = 10
BOSS_BULLET_H = 14
BOSS_BULLET_DRAW_W = 16
BOSS_BULLET_DRAW_H = 16

DIGITS = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
}


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Pyxel Shooting")
        pyxel.load(str(Path(__file__).with_name("shooting.pyxres")))

        self.high_score = 0
        self.reset_game()

        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.player_x = WIDTH // 2 - PLAYER_W // 2
        self.player_y = HEIGHT - PLAYER_H - 8
        self.shot_cooldown = 0
        self.damage_flash = 0
        self.boss = None
        self.boss_time = 0
        self.boss_defeated = False
        self.game_clear = False
        self.game_over = False
        self.game_over_text = "GAME OVER"

        self.bullets = []
        self.boss_bullets = []
        self.enemies = []
        self.sparks = []
        self.stars = [
            {"x": randint(0, WIDTH - 1), "y": randint(0, HEIGHT - 1), "speed": randint(1, 3)}
            for _ in range(80)
        ]

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.update_stars()

        if self.game_over or self.game_clear:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
            return

        self.update_player()
        self.update_bullets()
        self.update_boss_bullets()
        self.update_enemies()
        self.update_boss()
        self.update_sparks()
        self.update_damage_flash()
        self.check_collisions()

    def update_player(self):
        if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT):
            self.player_x = max(self.player_x - PLAYER_SPEED, 0)
        if pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x = min(self.player_x + PLAYER_SPEED, WIDTH - PLAYER_W)
        if pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_UP):
            self.player_y = max(self.player_y - PLAYER_SPEED, 16)
        if pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN):
            self.player_y = min(self.player_y + PLAYER_SPEED, HEIGHT - PLAYER_H)

        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1

        if pyxel.btn(pyxel.KEY_SPACE) and self.shot_cooldown == 0:
            self.add_bullet(self.player_x + PLAYER_W // 2 - BULLET_W // 2, self.player_y - 6)
            self.shot_cooldown = 6

    def update_bullets(self):
        for bullet in self.bullets:
            bullet["y"] -= BULLET_SPEED

        self.bullets = [bullet for bullet in self.bullets if bullet["y"] > -BULLET_H]

    def update_boss_bullets(self):
        for bullet in self.boss_bullets:
            bullet["x"] += bullet["vx"]
            bullet["y"] += bullet["vy"]

        self.boss_bullets = [
            bullet
            for bullet in self.boss_bullets
            if -BOSS_BULLET_DRAW_W < bullet["x"] < WIDTH
            and bullet["y"] < HEIGHT + BOSS_BULLET_DRAW_H
        ]

    def update_enemies(self):
        if self.boss is not None:
            return

        if self.score >= BOSS_SCORE and not self.boss_defeated:
            self.spawn_boss()
            return

        if pyxel.frame_count % self.enemy_interval() == 0:
            self.add_enemy()

        for enemy in self.enemies:
            enemy["y"] += enemy["speed"]
            enemy["x"] += enemy["vx"]

            if enemy["x"] <= 0 or enemy["x"] >= WIDTH - ENEMY_W:
                enemy["vx"] *= -1

        escaped = []
        for enemy in self.enemies:
            if enemy["y"] > HEIGHT:
                escaped.append(enemy)

        for enemy in escaped:
            self.enemies.remove(enemy)
            self.take_damage()

    def update_stars(self):
        for star in self.stars:
            star["y"] += star["speed"]
            if star["y"] >= HEIGHT:
                star["x"] = randint(0, WIDTH - 1)
                star["y"] = 0
                star["speed"] = randint(1, 3)

    def update_sparks(self):
        for spark in self.sparks:
            spark["x"] += spark["vx"]
            spark["y"] += spark["vy"]
            spark["life"] -= 1

        self.sparks = [spark for spark in self.sparks if spark["life"] > 0]

    def update_damage_flash(self):
        if self.damage_flash > 0:
            self.damage_flash -= 1

    def update_boss(self):
        if self.boss is None:
            return

        self.boss_time -= 1
        if self.boss_time <= 0:
            self.finish_game("TIME UP")
            return

        self.boss["x"] += self.boss["vx"]
        if self.boss["x"] <= 0 or self.boss["x"] >= WIDTH - BOSS_W:
            self.boss["vx"] *= -1

        if self.boss["y"] < 18:
            self.boss["y"] += 1

        if self.boss["y"] >= 18 and pyxel.frame_count % 24 == 0:
            self.add_boss_attack()

    def check_collisions(self):
        hit_bullets = []
        hit_enemies = []

        for bullet in self.bullets:
            if self.boss is not None and self.hit_box(
                bullet["x"], bullet["y"], BULLET_W, BULLET_H,
                self.boss["x"] + 10, self.boss["y"] + 8, BOSS_W - 20, BOSS_H - 28,
            ):
                hit_bullets.append(bullet)
                self.boss["hp"] -= 1

                boss_cx = self.boss["x"] + BOSS_W // 2
                boss_cy = self.boss["y"] + BOSS_H // 2
                if self.boss["hp"] <= 0:
                    self.score += self.boss["point"]
                    self.add_boss_burst(boss_cx, boss_cy)
                    self.boss = None
                    self.boss_defeated = True
                    self.boss_bullets = []
                    self.finish_clear()
                else:
                    self.add_sparks(bullet["x"], bullet["y"])
                continue

            for enemy in self.enemies:
                if self.hit_box(
                    bullet["x"], bullet["y"], BULLET_W, BULLET_H,
                    enemy["x"], enemy["y"], ENEMY_W, ENEMY_H,
                ):
                    hit_bullets.append(bullet)
                    enemy["hp"] -= 1
                    enemy_cx = enemy["x"] + ENEMY_W // 2
                    enemy_cy = enemy["y"] + ENEMY_H // 2
                    if enemy["hp"] <= 0:
                        hit_enemies.append(enemy)
                        self.score += enemy["point"]
                        self.add_burst(enemy_cx, enemy_cy)
                    else:
                        self.add_sparks(enemy_cx, enemy_cy)
                    break

        for bullet in hit_bullets:
            if bullet in self.bullets:
                self.bullets.remove(bullet)

        for enemy in hit_enemies:
            if enemy in self.enemies:
                self.enemies.remove(enemy)

        if self.boss is not None and self.hit_box(
            self.player_x, self.player_y, PLAYER_W, PLAYER_H,
            self.boss["x"] + 14, self.boss["y"] + 12, BOSS_W - 28, BOSS_H - 36,
        ):
            self.add_burst(self.player_x + PLAYER_W // 2, self.player_y + PLAYER_H // 2)
            self.take_damage()

        hit_boss_bullets = []
        for bullet in self.boss_bullets:
            if self.hit_box(
                self.player_x, self.player_y, PLAYER_W, PLAYER_H,
                bullet["x"] + 3, bullet["y"] + 1, BOSS_BULLET_W, BOSS_BULLET_H,
            ):
                hit_boss_bullets.append(bullet)
                self.add_burst(self.player_x + PLAYER_W // 2, self.player_y + PLAYER_H // 2)
                self.take_damage()

        for bullet in hit_boss_bullets:
            if bullet in self.boss_bullets:
                self.boss_bullets.remove(bullet)

        for enemy in self.enemies:
            if self.hit_box(
                self.player_x, self.player_y, PLAYER_W, PLAYER_H,
                enemy["x"], enemy["y"], ENEMY_W, ENEMY_H,
            ):
                self.enemies.remove(enemy)
                self.add_burst(self.player_x + PLAYER_W // 2, self.player_y + PLAYER_H // 2)
                self.take_damage()
                break

    def add_bullet(self, x, y):
        self.bullets.append({"x": x, "y": y})

    def add_enemy(self):
        kind = randint(0, 2)

        if kind == 0:
            hp = 1
            speed = 2
            vx = 0
            point = 10
        elif kind == 1:
            hp = 1
            speed = 2
            vx = randint(0, 1) * 4 - 2
            point = 20
        else:
            hp = 2
            speed = 2
            vx = 0
            point = 30

        self.enemies.append({
            "x": randint(0, WIDTH - ENEMY_W),
            "y": -ENEMY_H,
            "kind": kind,
            "hp": hp,
            "speed": speed,
            "vx": vx,
            "point": point,
        })

    def spawn_boss(self):
        self.enemies = []
        self.boss_bullets = []
        self.boss_time = BOSS_TIME_LIMIT
        self.boss = {
            "x": WIDTH // 2 - BOSS_W // 2,
            "y": -BOSS_H,
            "vx": 2,
            "hp": BOSS_HP,
            "point": 500,
        }

    def add_boss_attack(self):
        x = self.boss["x"] + BOSS_W // 2 - BOSS_BULLET_DRAW_W // 2
        y = self.boss["y"] + 82
        self.boss_bullets.append({"x": x, "y": y, "vx": 0, "vy": 4})
        self.boss_bullets.append({"x": x - 30, "y": y - 8, "vx": -1, "vy": 4})
        self.boss_bullets.append({"x": x + 30, "y": y - 8, "vx": 1, "vy": 4})

    def add_sparks(self, x, y):
        for _ in range(4):
            self.sparks.append({
                "x": x - EFFECT_SIZE // 2,
                "y": y - EFFECT_SIZE // 2,
                "vx": randint(-1, 1),
                "vy": randint(-1, 1),
                "life": randint(6, 10),
                "kind": "spark",
            })

    def add_burst(self, x, y):
        for _ in range(9):
            self.sparks.append({
                "x": x - EFFECT_SIZE // 2,
                "y": y - EFFECT_SIZE // 2,
                "vx": randint(-2, 2),
                "vy": randint(-2, 2),
                "life": randint(9, 16),
                "kind": "burst",
            })

    def add_boss_burst(self, x, y):
        for _ in range(24):
            self.sparks.append({
                "x": x - EFFECT_SIZE // 2 + randint(-48, 48),
                "y": y - EFFECT_SIZE // 2 + randint(-36, 36),
                "vx": randint(-3, 3),
                "vy": randint(-3, 3),
                "life": randint(14, 24),
                "kind": "burst",
            })

    def take_damage(self):
        if self.game_over or self.damage_flash > 0:
            return

        self.lives -= 1
        self.damage_flash = 12
        if self.lives <= 0:
            self.finish_game()

    def enemy_interval(self):
        interval = 36 - self.score // 100
        return max(interval, 16)

    def finish_game(self, text="GAME OVER"):
        self.game_over = True
        self.game_over_text = text
        self.high_score = max(self.high_score, self.score)

    def finish_clear(self):
        self.game_clear = True
        self.high_score = max(self.high_score, self.score)

    def hit_box(self, ax, ay, aw, ah, bx, by, bw, bh):
        return (
            ax < bx + bw
            and ax + aw > bx
            and ay < by + bh
            and ay + ah > by
        )

    def draw(self):
        pyxel.cls(0)
        self.draw_stars()
        self.draw_boss()
        self.draw_enemies()
        self.draw_player()
        self.draw_bullets()
        self.draw_boss_bullets()
        self.draw_sparks()
        self.draw_ui()
        self.draw_damage_flash()

        if self.game_over:
            self.draw_game_over()
        elif self.game_clear:
            self.draw_game_clear()

    def draw_stars(self):
        for star in self.stars:
            pyxel.pset(star["x"], star["y"], 5 + star["speed"])

    def draw_player(self):
        pyxel.blt(
            self.player_x,
            self.player_y,
            0,
            PLAYER_U,
            PLAYER_V,
            PLAYER_W,
            PLAYER_H,
            TRANSPARENT_COLOR,
        )

    def draw_bullets(self):
        for bullet in self.bullets:
            pyxel.blt(
                bullet["x"] - 1,
                bullet["y"] - 2,
                0,
                BULLET_U,
                BULLET_V,
                BULLET_DRAW_W,
                BULLET_DRAW_H,
                TRANSPARENT_COLOR,
            )

    def draw_boss_bullets(self):
        for bullet in self.boss_bullets:
            pyxel.blt(
                bullet["x"],
                bullet["y"],
                0,
                BOSS_BULLET_U,
                BOSS_BULLET_V,
                BOSS_BULLET_DRAW_W,
                BOSS_BULLET_DRAW_H,
                TRANSPARENT_COLOR,
            )

    def draw_enemies(self):
        for enemy in self.enemies:
            pyxel.blt(
                enemy["x"],
                enemy["y"],
                0,
                ENEMY_U[enemy["kind"]],
                ENEMY_V,
                ENEMY_W,
                ENEMY_H,
                TRANSPARENT_COLOR,
            )

    def draw_boss(self):
        if self.boss is None:
            return

        pyxel.blt(
            self.boss["x"],
            self.boss["y"],
            0,
            BOSS_U,
            BOSS_V,
            BOSS_W,
            BOSS_H,
            TRANSPARENT_COLOR,
        )
        hp_w = BOSS_W * self.boss["hp"] // BOSS_HP
        bar_x = self.boss["x"]
        bar_y = max(self.boss["y"] - 8, 18)
        pyxel.rect(bar_x, bar_y, BOSS_W, 4, 1)
        pyxel.rect(bar_x, bar_y, hp_w, 4, 8)
        pyxel.rectb(bar_x, bar_y, BOSS_W, 4, 7)

    def draw_sparks(self):
        for spark in self.sparks:
            u = SPARK_U
            v = SPARK_V
            if spark["kind"] == "burst":
                u = BURST_U
                v = BURST_V

            pyxel.blt(
                spark["x"],
                spark["y"],
                0,
                u,
                v,
                EFFECT_SIZE,
                EFFECT_SIZE,
                TRANSPARENT_COLOR,
            )

    def draw_damage_flash(self):
        if self.damage_flash == 0:
            return

        for y in range(0, HEIGHT, 4):
            pyxel.rect(0, y, WIDTH, 1, 8)
        pyxel.rectb(0, 0, WIDTH, HEIGHT, 8)

    def draw_ui(self):
        pyxel.text(4, 4, "SCORE", 7)
        self.draw_big_number(4, 13, self.score, 10, 2)
        pyxel.text(4, 32, "HIGH {:>4}".format(self.high_score), 6)
        if self.boss is not None:
            seconds = max(0, (self.boss_time + 29) // 30)
            pyxel.text(WIDTH // 2 - 14, 4, "TIME", 7)
            self.draw_big_number(WIDTH // 2 - 10, 13, seconds, 8, 2)
        elif not self.boss_defeated:
            self.draw_boss_progress()
        pyxel.text(WIDTH - 55, 4, "LIFE", 7)
        for i in range(self.lives):
            pyxel.blt(
                WIDTH - 30 + i * 9,
                1,
                0,
                LIFE_U,
                LIFE_V,
                LIFE_SIZE,
                LIFE_SIZE,
                TRANSPARENT_COLOR,
            )

    def draw_boss_progress(self):
        bar_w = 120
        bar_h = 6
        x = WIDTH // 2 - bar_w // 2
        y = 8
        progress = min(self.score, BOSS_SCORE)
        fill_w = bar_w * progress // BOSS_SCORE
        rest_score = max(BOSS_SCORE - self.score, 0)

        pyxel.text(x, y - 7, "BOSS", 8)
        pyxel.rect(x, y, bar_w, bar_h, 1)
        pyxel.rect(x, y, fill_w, bar_h, 8)
        pyxel.rectb(x, y, bar_w, bar_h, 7)
        pyxel.text(x + bar_w + 6, y - 1, "あと{:>3}".format(rest_score), 7)

    def draw_big_number(self, x, y, value, color, scale):
        text = str(value)
        for i, char in enumerate(text):
            pattern = DIGITS[char]
            ox = x + i * 4 * scale
            for row, line in enumerate(pattern):
                for col, bit in enumerate(line):
                    if bit == "1":
                        pyxel.rect(ox + col * scale, y + row * scale, scale, scale, color)

    def draw_game_over(self):
        x = WIDTH // 2 - 52
        y = HEIGHT // 2 - 19
        pyxel.rect(x, y, 104, 38, 1)
        pyxel.rectb(x, y, 104, 38, 7)
        pyxel.text(x + 34, y + 7, self.game_over_text, 8)
        pyxel.text(x + 18, y + 19, "R:RESTART  Q:QUIT", 7)
        pyxel.text(x + 25, y + 29, "SCORE {:>4}".format(self.score), 10)

    def draw_game_clear(self):
        x = WIDTH // 2 - 60
        y = HEIGHT // 2 - 24
        pyxel.rect(x, y, 120, 48, 1)
        pyxel.rectb(x, y, 120, 48, 10)
        pyxel.text(x + 35, y + 8, "GAME CLEAR", 10)
        pyxel.text(x + 19, y + 22, "R:RESTART  Q:QUIT", 7)
        pyxel.text(x + 33, y + 34, "SCORE {:>4}".format(self.score), 10)


App()
