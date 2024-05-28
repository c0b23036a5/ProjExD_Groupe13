import math
import os
import random
import sys
import time
import pygame as pg

import json
import time

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore



WIDTH, HEIGHT = 1600, 900  # ゲームウィンドウの幅，高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def m_play1():
    """
    炎の挑戦：通常時流すBGM
    load:音楽ファイルの読み込み
    play:ループ再生
    """

     
    pg.mixer.init()
    pg.mixer.music.load("fig/audio/炎の挑戦.mp3")
    pg.mixer.music.play(-1)

def m_play2():
    #ゲームオーバーBGM
    pg.mixer.music.stop()
    pg.mixer.init()
    pg.mixer.music.load("fig/audio/絶望の淵から.mp3")
    pg.mixer.music.play(1)
FLG_Hard=False  #ハードモードフラグ

def check_bound(obj_rct:pg.Rect) -> tuple[bool, bool]:
    """
    Rectの画面内外判定用の関数
    引数：こうかとんRect，または，爆弾Rect，またはビームRect
    戻り値：横方向判定結果，縦方向判定結果（True：画面内／False：画面外）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:  # 横方向のはみ出し判定
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm

'''
class MusicPlayer:
    """
    音楽を再生するクラス
    """
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.paused = False

    def play_music(self, file_path):
        try:
            pg.mixer.music.load(file_path)
            pg.mixer.music.play(loops = -1)
        except Exception as e:
            print("Error:", e)

    def stop_music(self):
        pg.mixer.music.stop()
    
    def pause_music(self):
        pg.mixer.music.pause()
        self.paused = True

    def unpause_music(self):
        pg.mixer.music.unpause()
        self.paused = False
'''



class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }
    state="normal"  #こうかとんの状態の変数
    hyper_life=500  #無敵時間(単位:frame)

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]

        if self.state == "hyper":     #無敵状態の場合
            if self.hyper_life <= 0:  #時間が0の場合
                self.state="normal"     #ノーマルモードにする
            else:
                self.hyper_life -= 1    #時間を1フレームごとに減らす
                self.image = pg.transform.laplacian(self.image) #特殊状態にする

        screen.blit(self.image, self.rect)

class Life(pg.sprite.Sprite):
    """
    こうかとんの残機に関するクラス
    """
    def __init__(self, initial_lives: int):
        """
        こうかとん画像Surfaceを生成する
        引数1 initial_lives:初期値
        """
        self.lives = initial_lives #初期ライフというだけ
        self.life_image = pg.image.load("fig/koukaton_life.png") #赤いハート画像
        self.lost_life_image=pg.image.load("fig/lost_life.png") #輝きを失ったハート画像
        self.neta_life=pg.image.load("fig/koukaton_buti.png") #こうかとんカットイン画像

    def lose_life(self): #こうかとんのライフ減少を行う関数
        if self.lives > 0:
            self.lives -= 1
    
    def draw(self, screen: pg.Surface): #こうかとんのライフを表示する関数
        for i in range(3):
            if i < self.lives:
                screen.blit(self.life_image, (10 + i * (self.life_image.get_width() + 10), 10))
            else:
                screen.blit(self.lost_life_image, (10 + i * (self.life_image.get_width() + 10), 10))
    """
    def huzake(self, screen: pg.Surface): #こうかとんのカットインを表示する関数
        screen.blit(self.neta_life, (-300, 0))
    """


class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height/2
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True) :
            self.kill()
            


class Beam(pg.sprite.Sprite):
    """
    ビームに関すeるクラス
    """
    def __init__(self, bird: Bird, angle0 =0):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        angle= math.degrees(math.atan2(-self.vy, self.vx)+angle0)  #こうかとんの角度にangle0を追加        
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()
        pg.mixer.Sound("fig/audio/ビーム発射音.mp3").play() #ビーム発射音の再生
        

'''
Beamを複数つくる弾幕クラス
class NeoBeam():

    def __init__(self):
        self.b_lst = []
    
    def gen_beams(self):
        for i in range(10):
            self.b_lst.append(-50+i*10)
        return self.b_lst
'''        



class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy|BossEnemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンスまたはボス敵インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        
        if type(obj) == BossEnemy:  #引数がボスの場合は爆発サイズをボスのサイズに合わせる
            img=pg.transform.rotozoom(img,1,2.5)

        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()

        pg.mixer.Sound("fig/audio/爆発4.mp3").play() #爆発音の追加


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vy = random.randint(6,15)
        #self.bound = random.randint(50, int(HEIGHT/2))  # 停止位置
        self.bound = random.randint(50, int(HEIGHT/2))  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy

class BossEnemy(pg.sprite.Sprite):
    """
    ボスエネミーを追加するクラス
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.image = pg.transform.rotozoom(self.image,0,2.5) #サイズ変更
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vy = +6
        #self.bound = random.randint(50, int(HEIGHT/2))  # 停止位置
        self.bound = random.randint(50, int(HEIGHT/2))  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(10, 30)  # 爆弾投下インターバル
    
    def update(self):
        """
        ボスエネミーを速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy

class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    ボス:50点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 50
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)

class Gravity(pg.sprite.Sprite):
    """
    エンターキーを押すと画面内の敵を倒す
    """
    def __init__(self, life):
        super().__init__()
        self.image = pg.Surface((1600,900))
        pg.draw.rect(self.image, (0, 0, 0), (0, 0, 1600, 900))
        self.image.set_alpha(200)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)
        self.life = life     #発動時間の定義
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()

class Sheeld(pg.sprite.Sprite):
    """
    こうかとんの向いている向きに長方形のシールドを表示するクラス
    """
    is_not_shield = True
    def __init__(self, bird: Bird,life: int):
        #シールドが展開中はFalseのクラス変数
        

        """
        長方形の壁を生成する
        """
        super().__init__()
        # 壁　幅20 高さ　こうかとんの半分の高さ
        self.image = pg.Surface((20, bird.rect.height*2)) 
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.center = bird.rect.center
        pg.draw.rect(self.image, (0, 0, 255), self.rect)

        # birdの向いている方向に合わせて回転
        vx , vy = bird.dire
        angle = math.degrees(math.atan2(-vy, vx))
        self.image = pg.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # シールドをBirdの向いている先に設置
        self.rect.centerx += bird.rect.width*vx
        self.rect.centery += bird.rect.height*vy

        # シールドの耐久値
        self.life = life

        # シールド展開中はFalse
        __class__.is_not_shield = False

    def update(self):
        #print(self.life)
        self.life -= 1
        if self.life < 0:
            __class__.is_not_shield = True
            self.kill()


class Bonus(pg.sprite.Sprite):
    """
    ボーナスアイテムを出現させるクラス
    アイテムに触れるとスコア+100
    """

    def __init__(self,x:tuple):
        super().__init__()
        self.image = pg.image.load(f"fig/small_star7_yellow.png")    #画像Surfaceの定義
        self.image=pg.transform.rotozoom(self.image,0,0.18)   #画像の大きさ調整
        self.rect = self.image.get_rect()
        self.rect.center = x
        

def get_cloud_hi_score(cred):
    db = firestore.client()
    doc_ref = db.collection('score').get()
    #print(doc_ref)
    return int(doc_ref[0].to_dict()['score'])

def firebase_upload(cred, score,name):
    db = firestore.client()
    doc_ref = db.collection('score').document("hi_score")

    #すでに存在しているドキュメントを削除
    db.collection("score").document("hi_score").delete()
    doc_ref.set({
        'score': score,
        'user': name
    })
    print("アップロードしました")


    

def main():
    m_play1()
    #firebaseの初期化
    cred = credentials.Certificate("firebase.json")
    firebase_admin.initialize_app(cred)


    global FLG_Hard #ハードモードフラグへのアクセス
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    score = Score()
    #score.value =900000000

    bird = Bird(3, (900, 400))
    life = Life(3)  # こうかとんの残機を3に設定
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    gravity = pg.sprite.Group()
    sheelds = pg.sprite.Group()
    bosses = pg.sprite.Group()
    bonus = pg.sprite.Group()

    tmr = 0
    clock = pg.time.Clock()
    Boss_count = 0 #ボスの出現回数
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            
            #もし左シフトキーおよびスペースキーが押されたら五個のビームを生成
            if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT and pg.K_SPACE: 
                for i in range(5):
                    if i != 2:
                    #l = neobeam.gen_beams()
                        beams.add(Beam(bird,-50+i*25))

            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.add(Beam(bird))
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN and score.value >= 200:
                gravity.add(Gravity(400))
                score.value -= 200


            if (event.type == pg.KEYDOWN) and (event.key == pg.K_RSHIFT) and (score.value >= 100) and not (bird.state=="hyper"):   #Rshiftキーが押されたかつスコアが１００以上の場合
                bird.state = "hyper"    #無敵状態にする
                score.value -= 100      #スコアを減らして５００フレーム分無敵にする
                bird.hyper_life = 500
        
        screen.blit(bg_img, [0, 0])

        if key_lst[pg.K_LSHIFT]:
            bird.speed = 20
        else:
            bird.speed = 10

        if tmr%100 == 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy())
        if FLG_Hard or tmr > 20000: #ハードモードか20000フレーム経過したら
            if tmr%200 == 0:    #ボスの出現率を早くする
                bosses.add(BossEnemy())
                Boss_count += 1    
        else:
            if tmr%1200 == 0 and Boss_count != 0:    # 1200フレームに１回、ボスを出現させる。さらに0フレーム時にボスを出現させないようにする
                Boss_count += 0
                bosses.add(BossEnemy())
            elif Boss_count == 0:
                Boss_count += 1

        for emy in emys:
            if emy.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                bombs.add(Bomb(emy, bird))
        for boss in bosses:
            if tmr%boss.interval == 0:
                #停止状態になったらintervalに応じて爆弾投下
                bombs.add(Bomb(boss,bird))
        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            if random.randint(0,10) == 5:        # 10分1の確率で
                bonus.add(Bonus(emy.rect.center))    #ボーナスアイテムを描画する
            else:
                exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ
            
            bird.change_img(6, screen)  # こうかとん喜びエフェクト

        for boss in pg.sprite.groupcollide(bosses, beams, True, True).keys():
            exps.add(Explosion(boss, 100))  # 爆発エフェクト
            score.value += 50  # 50点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト

        for boss in pg.sprite.groupcollide(bosses, beams, True, True).keys():
            exps.add(Explosion(boss, 100))  # 爆発エフェクト
            score.value += 50  # 50点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト

        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ

        for emy in pg.sprite.groupcollide(emys, gravity, True, False).keys():
            exps.add(Explosion(emy, 100))
            score.value += 10
            bird.change_img(6, screen)

        for bomb in pg.sprite.groupcollide(bombs, gravity, True, False).keys():
            exps.add(Explosion(bomb, 50))
            score.value += 1
        bonus_item=pg.sprite.spritecollide(bird,bonus, False)

        if len(bonus_item) != 0 :    # ボーナスアイテムとこうかとんが衝突したら
            score.value += 100       # スコア+100
            bonus_item[0].kill()     # ボーナスアイテムを消す
        
        #print(tmr)
        
        # Cボタンを押すとシールドを展開
        #if key_lst[pg.K_c] & score.value >= 50:
        if key_lst[pg.K_c] & Sheeld.is_not_shield & (score.value >= 50):
        #if key_lst[pg.K_c]:
            print(score.value >= 50)
            print(Sheeld.is_not_shield)
            #score.value -= 50
            print("シールド展開")
            # スコアが50減る
            score.value -= 50
            sheelds.add(Sheeld(bird, 400))
        
        # 壁と爆弾が衝突したら爆発
        for bomb in pg.sprite.groupcollide(bombs, sheelds, True, False).keys():
            exps.add(Explosion(bomb, 50))
            score.value += 1
        
        touch_bomb=pg.sprite.spritecollide(bird, bombs, False)
        if len(touch_bomb) != 0:
            if (bird.state == "hyper"):
                exps.add(Explosion(touch_bomb[0], 50))  # 爆発エフェクト
                score.value += 1  # 1点アップ
                touch_bomb[0].kill()
            else:
                touch_bomb[0].kill()    
                bird.change_img(8, screen) # こうかとん悲しみエフェクト
                score.update(screen)
                pg.display.update()
                


                time.sleep(0.4)
                life.lose_life() #こうかとんのライフが一つ減る
                pg.mixer.Sound("fig/audio/nc301497_ガラス割れた音.mp3").play() #ハートが割れる音の再生
                if life.lives == 0: #こうかとんのライフが0ならば
                    m_play2()
                    time.sleep(2) #2秒待つ
                

                    #ゲーむオーバー画面を実装
                    screen.fill((0, 0, 0))
                    font = pg.font.Font(None, 100)
                    text = font.render("Game Over", True, (255, 255, 255))
                    screen.blit(text, (WIDTH/2-200, HEIGHT/2-50))

                    #score.jsonを読み込み　hi_scoreよりscore.valueが大きい場合はhi_scoreを更新
                    with open("score.json", "r") as f:
                        hi_score = json.load(f)
                        world_hi_score = get_cloud_hi_score(cred)
                        

                        if world_hi_score < score.value:
                            with open("score.json","w") as f:
                                hi_score["local-hi-score"] = score.value
                                hi_score["world-hi-score"] = score.value
                                json.dump(hi_score, f)
                                print("hi_scoreを更新しました")
                                #ハイスコアの更新をお知らせ
                                font = pg.font.Font(None, 50)
                                text2 = font.render(f"This is World Record!  Score:{hi_score['local-hi-score']}", True, (255, 255, 255))
                                screen.blit(text2, (WIDTH/2-200, HEIGHT/2+50))
                                pg.display.update()
                                time.sleep(5)

                                #firebaseにスコアをアップロード
                                firebase_upload(cred, score.value,hi_score["player-name"])


                        elif hi_score["local-hi-score"] < score.value:
                            with open("score.json", "w") as f:
                                hi_score["local-hi-score"] = score.value
                                json.dump(hi_score, f)
                                print("hi_scoreを更新しました")
                                #ハイスコアの更新をお知らせ
                                font = pg.font.Font(None, 50)
                                text2 = font.render(f"New High Score!  Score:{hi_score['local-hi-score']} World-Score:{world_hi_score}", True, (255, 255, 255))
                                screen.blit(text2, (WIDTH/2-200, HEIGHT/2+50))
                                pg.display.update()
                                time.sleep(5)

                        else:
                            print("hi_scoreを更新しませんでした")
                            #ハイスコアを表示する。
                            font = pg.font.Font(None, 50)
                            text3 = font.render(f"Hi-Score: {hi_score['local-hi-score']}World-Score:{world_hi_score}  Your-Score: {score.value}", True, (255, 255, 255))
                            screen.blit(text3, (WIDTH/2-200, HEIGHT/2+50))
                            #world_hi_scoreをjsonファイルに保存
                            with open("score.json", "w") as f:
                                hi_score["world-hi-score"] = world_hi_score
                                json.dump(hi_score, f)
                                print("world_hi_scoreを更新しました")

                            pg.display.update()
                            time.sleep(5)

                    return

        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        bosses.update()
        bosses.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        gravity.draw(screen)
        gravity.update()
        life.draw(screen)  # 残機を画面に表示

        if len(bonus) != 0:
            bonus.draw(screen)   # ボーナスアイテムの描画

        if not Sheeld.is_not_shield:
            sheelds.update()
            sheelds.draw(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()