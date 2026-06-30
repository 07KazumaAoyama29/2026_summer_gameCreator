# Pyxelでシューティングゲームを作ろう

# 目的
PythonとPyxelを使って、シューティングゲームを作ります。<br>
最初から全部を作るのではなく、プログラムを少しずつ書き足して、ゲームの欠点を直していきます。

今日のゴールは、次のようなゲームです。

- プレイヤーを動かせる
- スペースキーで弾を撃てる
- 敵が動く
- 弾が敵に当たる
- スコアをためるとボス戦になる

# 内容目標
- Pythonでキャラクターの動きを作る
- リストの中にある弾や敵を動かす
- `if` を使って条件分岐を書く
- 当たり判定の考え方を知る
- 自分でゲームを改造できるようになる

# 今日使うファイル
- `main.py`: 今日プログラムを書くファイル
- `game_core.py`: ゲーム全体を動かすファイル。今日は編集しません。
- `main_sample.py`: 答えが入っている見本ファイル
- `my_resource.pyxres`: キャラクターや弾の絵が入っているファイル

# 実行方法
ターミナルで次のコマンドを実行します。

```bash
python main.py
```

ゲームを終了するときは `Q` キーを押します。<br>
ゲームオーバーやゲームクリアの後は `R` キーでリスタートできます。

# 操作方法
- `A` / `←`: 左に動く
- `D` / `→`: 右に動く
- `W` / `↑`: 上に動く
- `S` / `↓`: 下に動く
- `SPACE`: 弾を撃つ

# プログラム全体図
ゲームは大きく分けると、次の2つを何度もくり返しています。

## update
ゲームの中身を動かすところです。

- プレイヤーを動かす
- 弾を動かす
- 敵を動かす
- 弾と敵が当たったか調べる

## draw
画面に絵を描くところです。

- 背景を描く
- プレイヤーを描く
- 弾を描く
- 敵を描く
- スコアを描く

# 座標について
Pyxelの画面では、左上が `(0, 0)` です。

- `x` は横の位置です。右に行くほど大きくなります。
- `y` は縦の位置です。下に行くほど大きくなります。

つまり、キャラクターを右に動かしたいときは `x` を大きくします。<br>
上に動かしたいときは `y` を小さくします。

# Mission1 プレイヤーを動かそう
最初の欠点は、プレイヤーが動かないことです。<br>
`main.py` の `move_player(game)` の中に、プレイヤーを動かすプログラムを書きます。

## 左右に動かす
`A` キーまたは `←` キーを押したら左へ、`D` キーまたは `→` キーを押したら右へ動かします。

```python
if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT):
    game.player_x = max(game.player_x - game.PLAYER_SPEED, 0)

if pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT):
    game.player_x = min(game.player_x + game.PLAYER_SPEED, game.WIDTH - game.PLAYER_W)
```

## 上下に動かす
`W` キーまたは `↑` キーを押したら上へ、`S` キーまたは `↓` キーを押したら下へ動かします。

```python
if pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_UP):
    game.player_y = max(game.player_y - game.PLAYER_SPEED, 16)

if pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN):
    game.player_y = min(game.player_y + game.PLAYER_SPEED, game.HEIGHT - game.PLAYER_H)
```

## ポイント
`max()` と `min()` は、画面の外に出ないようにするために使っています。

- `max(値, 0)`: 0より小さくならないようにする
- `min(値, 最大値)`: 最大値より大きくならないようにする

<details><summary>Mission1の答え</summary>

```python
def move_player(game):
    if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT):
        game.player_x = max(game.player_x - game.PLAYER_SPEED, 0)
    if pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT):
        game.player_x = min(game.player_x + game.PLAYER_SPEED, game.WIDTH - game.PLAYER_W)
    if pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_UP):
        game.player_y = max(game.player_y - game.PLAYER_SPEED, 16)
    if pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN):
        game.player_y = min(game.player_y + game.PLAYER_SPEED, game.HEIGHT - game.PLAYER_H)
```

</details>

# Mission2 弾を撃てるようにしよう
次の欠点は、敵を攻撃できないことです。<br>
`SPACE` キーを押したら弾を出すようにします。

弾を出すためには、`add_bullet(x, y)` という命令を使います。

```python
game.add_bullet(x座標, y座標)
```

プレイヤーの真ん中から弾を出したいので、x座標は次のようにします。

```python
game.player_x + game.PLAYER_W // 2 - game.BULLET_W // 2
```

## 書くプログラム
`main.py` の `shoot_bullet(game)` の中に、次のプログラムを書きます。

```python
if game.shot_cooldown > 0:
    game.shot_cooldown -= 1

if pyxel.btn(pyxel.KEY_SPACE) and game.shot_cooldown == 0:
    game.add_bullet(game.player_x + game.PLAYER_W // 2 - game.BULLET_W // 2, game.player_y - 6)
    game.shot_cooldown = 6
```

## ポイント
`shot_cooldown` は、弾を連射しすぎないようにするための数字です。<br>
弾を撃ったら `6` にして、毎フレーム `1` ずつ減らします。`0` になったらまた撃てます。

<details><summary>Mission2の答え</summary>

```python
if game.shot_cooldown > 0:
    game.shot_cooldown -= 1

if pyxel.btn(pyxel.KEY_SPACE) and game.shot_cooldown == 0:
    game.add_bullet(game.player_x + game.PLAYER_W // 2 - game.BULLET_W // 2, game.player_y - 6)
    game.shot_cooldown = 6
```

</details>

# Mission3 弾を上に飛ばそう
弾を出せるようになっても、弾が止まったままだと攻撃になりません。<br>
次は、出した弾を上に動かします。

弾は `game.bullets` というリストに入っています。<br>
1つ1つの弾は、次のようなデータです。

```python
{"x": 100, "y": 200}
```

`y` を小さくすると、弾は上に動きます。

## 書くプログラム
`main.py` の `move_bullets(game)` の中に書きます。

```python
for bullet in game.bullets:
    bullet["y"] -= game.BULLET_SPEED
```

画面の外に出た弾は、`game_core.py` が自動で消してくれます。

## ポイント
`for bullet in game.bullets:` は、弾を1つずつ取り出して処理する書き方です。

<details><summary>Mission3の答え</summary>

```python
def move_bullets(game):
    for bullet in game.bullets:
        bullet["y"] -= game.BULLET_SPEED
```

</details>

# Mission4 敵を動かそう
次の欠点は、敵が動かないことです。<br>
敵も弾と同じように、リストの中に入っています。

敵は `game_core.py` の中で作られ、`main.py` の `move_enemy(game, enemy)` に1体ずつ渡されます。<br>
1つ1つの敵は、次のようなデータです。

```python
{
    "x": 120,
    "y": 0,
    "speed": 2,
    "vx": 0,
}
```

- `speed`: 下に進む速さ
- `vx`: 横に進む速さ

## 書くプログラム
`main.py` の `move_enemy(game, enemy)` の中に書きます。

```python
enemy["y"] += enemy["speed"]
enemy["x"] += enemy["vx"]
```

横に動く敵が画面の端まで来たら、向きを反対にします。

```python
if enemy["x"] <= 0 or enemy["x"] >= game.WIDTH - game.ENEMY_W:
    enemy["vx"] *= -1
```

## ポイント
`enemy["vx"] *= -1` は、横方向の速さを反対向きにする命令です。<br>
たとえば `2` なら `-2` に、`-2` なら `2` になります。

<details><summary>Mission4の答え</summary>

```python
enemy["y"] += enemy["speed"]
enemy["x"] += enemy["vx"]

if enemy["x"] <= 0 or enemy["x"] >= game.WIDTH - game.ENEMY_W:
    enemy["vx"] *= -1
```

</details>

# Mission5 弾が敵に当たるようにしよう
最後の大きな欠点は、弾が敵をすりぬけてしまうことです。<br>
弾と敵が重なったかどうかを調べることを、**当たり判定** といいます。

このゲームには、当たり判定を調べるための関数が用意されています。

```python
game.hit_box(ax, ay, aw, ah, bx, by, bw, bh)
```

これは、Aの四角形とBの四角形が重なっていたら `True`、重なっていなければ `False` になります。

## 弾と敵の四角形
弾の四角形は、次の4つです。

- `bullet["x"]`
- `bullet["y"]`
- `game.BULLET_W`
- `game.BULLET_H`

敵の四角形は、次の4つです。

- `enemy["x"]`
- `enemy["y"]`
- `game.ENEMY_W`
- `game.ENEMY_H`

## 書くプログラム
`main.py` の `bullet_hits_enemy(game, bullet, enemy)` の中に書きます。<br>
当たっていたら `True`、当たっていなければ `False` を返します。

```python
return game.hit_box(
    bullet["x"], bullet["y"], game.BULLET_W, game.BULLET_H,
    enemy["x"], enemy["y"], game.ENEMY_W, game.ENEMY_H,
)
```

## ポイント
敵のHPを減らす処理、スコア加算、爆発、ボス出現は `game_core.py` にあらかじめ入っています。<br>
ここでは「当たったかどうか」を返すだけでOKです。

<details><summary>Mission5の答え</summary>

```python
def bullet_hits_enemy(game, bullet, enemy):
    return game.hit_box(
        bullet["x"], bullet["y"], game.BULLET_W, game.BULLET_H,
        enemy["x"], enemy["y"], game.ENEMY_W, game.ENEMY_H,
    )
```

</details>

# ここから先は完成済みのしくみ
今日の `game_core.py` には、次のしくみがあらかじめ入っています。

## スコアと爆発
敵を倒すとスコアが増えます。<br>
敵にダメージを与えたときは小さいエフェクト、敵を倒したときは赤い爆発が出ます。

## ボスまでのバー
画面上部に、ボス戦まであと何点必要かを表すバーが出ます。<br>
スコアが `BOSS_SCORE` 以上になると、ボス戦が始まります。

## ボス戦
ボス戦では、ボスが弾を撃ってきます。<br>
制限時間は60秒です。時間内に倒せばゲームクリア、時間切れなら `TIME UP` です。

# 改造してみよう
時間が余ったら、次の改造にチャレンジしてみましょう。

## 改造1 プレイヤーの速さを変える
```python
PLAYER_SPEED = 4
```

数字を大きくすると速くなります。

## 改造2 弾の速さを変える
```python
BULLET_SPEED = 8
```

数字を大きくすると弾が速くなります。

## 改造3 ボスが出るスコアを変える
```python
BOSS_SCORE = 300
```

数字を小さくすると、早くボスが出ます。

## 改造4 ボスのHPを変える
```python
BOSS_HP = 24
```

数字を大きくすると、ボスが強くなります。

## 改造5 絵を変える
`my_resource.pyxres` をPyxel Editorで開くと、プレイヤー、敵、弾、ボスの絵を変えられます。

# まとめ
今日作ったシューティングゲームでは、次のプログラムを書きました。

- キー入力でプレイヤーを動かす
- `SPACE` キーで弾を作る
- リストの中の弾を動かす
- リストの中の敵を動かす
- `if` と当たり判定で、弾が敵に当たったか調べる

プログラムは、少し書くだけでもゲームの動きが変わります。<br>
自分だけのルールや見た目に改造して、オリジナルのシューティングゲームにしてみましょう。
