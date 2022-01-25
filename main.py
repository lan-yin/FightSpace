
from doctest import Example
import pygame
import random
import os


# 通常設定好不會改的變數，就會用大寫
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 150, 180)
RED = (255, 60, 60)
YELLOW = (255, 255, 0)

WIDTH = 500
HEIGHT = 600

# 遊戲初始化 and 創建視窗
pygame.init()
pygame.mixer.init() # 音效模組初始化
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("小蜜蜂")
clock = pygame.time.Clock()

# 載入圖片，一定要先初始化
background_img = pygame.image.load(os.path.join("background.png")).convert()
player_img = pygame.image.load(os.path.join("player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)
bullet_img = pygame.image.load(os.path.join("bullet.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join(f"rock{i}.png")).convert())
expl_anim = {}
expl_anim["large"] = []
expl_anim["small"] = []
expl_anim["player"] = []
for i in range(9):
    expl_img = pygame.image.load(os.path.join(f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim["large"].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim["small"].append(pygame.transform.scale(expl_img, (40, 40)))
    player_expl_img = pygame.image.load(os.path.join(f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim["player"].append(player_expl_img)
power_imgs = {}
power_imgs["shield"] = pygame.image.load(os.path.join("shield.png")).convert()
power_imgs["gun"] = pygame.image.load(os.path.join("gun.png")).convert()




# 載入音樂
shoot_sound = pygame.mixer.Sound(os.path.join("shoot.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("pow0.wav"))
die_sound = pygame.mixer.Sound(os.path.join("rumble.ogg"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join("expl0.wav")),
    pygame.mixer.Sound(os.path.join("expl1.wav"))
]
pygame.mixer.music.load(os.path.join("background.ogg")) # 記得加load() music用在背景音控制
pygame.mixer.music.set_volume(0.4) #背景小聲一點爆炸聲才清楚


#font_name = pygame.font.match_font("arial") # 直接從系統找字體 arial這個是大部分電腦有的字體，比較通用，可運行在大部分電腦，但是不支援中文
font_name = os.path.join("font.ttf")

def draw_txt(surf, text, size, x, y, color=WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color) # 用True是指用antialias（反鋸齒）字看起來比較滑順
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def new_rock():  # 用太多次了，乾脆弄一個函式
    r = Rock()
    all_sprites.add(r)  
    rocks.add(r)

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2) # 2是指外匡寬度，第四個參數沒寫代表填滿

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30*i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init():
    screen.blit(background_img, (0, 0 ))
    draw_txt(screen, "小蜜蜂", 64, WIDTH/2, HEIGHT/4, YELLOW)
    draw_txt(screen, "← → 移動飛船  空白鍵 : 發射子彈 ", 22, WIDTH/2, HEIGHT/2)
    draw_txt(screen, "按任意間開始遊戲!", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)  # 一秒鐘更新()次，同步大家遊戲的速度，每個人電腦好壞程度不一
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:  # KEYUP是整個按鍵按下去鬆開上來才算
                waiting = False
                return False

# 操控sprite 
class Player(pygame.sprite.Sprite):   # 繼承sprite到我們的class Player裡
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))   # 換成自己的圖片
        self.image.set_colorkey(BLACK)
        #self.image = pygame.Surface((50, 40))  # 設定一個色塊圖片
        #self.image.fill(GREEN)
        self.rect = self.image.get_rect()      # 把圖片匡起來，給他座標（左上角）
        self.radius = 20
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius) # 可以檢視有沒有包好
        self.rect.centerx = WIDTH/2  # 圖片放中間或指定位置
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100 #生命條
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0
       

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now
        if self.hidden and now - self.hide_time > 1000: # 1000毫秒 = 1秒
           self.hidden = False
           self.rect.centerx = WIDTH/2  # 定位回來
           self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed()  # 鍵盤按鍵有沒有被按的函式
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx   #本來是2，但是太慢
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0


    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)  
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play() 
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery) 
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()    

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

# 石頭sprite 直接複製操sprite來修改
class Rock(pygame.sprite.Sprite):   
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs)   # 因為石頭的圖(FPS=60)會一直生產出來也就是一直疊加角度上去，最後會變的形狀很怪，所以ori讓每次旋轉是轉原始的圖
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        #self.image = pygame.Surface((30, 40))  # 設定一個色塊圖片
        #self.image.fill(RED)
        self.rect = self.image.get_rect() 
        self.radius = self.rect.width * 0.85 / 2
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius) # 可以檢視有沒有包好
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)  # 圖片設定上方隨機位置位置
        self.rect.y = random.randrange(-180, -100)  # 從上面看不到的地方隨機掉下來，看石頭大小決定掉下來座標
        self.speedy = random.randrange(2, 6)  # 掉下來的速度
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3) 
       
    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect() # 轉完之後中心點要重新定位
        self.rect.center = center


    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)  
            self.rect.y = random.randrange(-100, -40)  
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)

# 子彈sprite ＆ 碰撞處理
class Bullet(pygame.sprite.Sprite): 
    def __init__(self, x, y): # ！！！！為什麼這邊呼叫的 x, y 就是飛船的？ 這是呼叫時要輸入的參數，上面shoot()裡面有設定呼叫Bullet時要輸入 x, y 是誰
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()  
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        
    def update(self):
       self.rect.y += self.speedy
       if self.rect.bottom < 0 :
           self.kill() # 把所有有這個子彈的sprite群組的這個子彈刪掉

# 爆炸sprite
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size): 
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()   
        self.rect.center = center 
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 40
        
    def update(self):
       now = pygame.time.get_ticks()
       if now - self.last_update > self.frame_rate:
           self.last_update = now
           self.frame += 1
           if self.frame == len(expl_anim[self.size]):
               self.kill()
           else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

# 寶物sprites
class Power(pygame.sprite.Sprite): 
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield", "gun"])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()  
        self.rect.center = center
        self.speedy = 3
        
    def update(self):
       self.rect.y += self.speedy
       if self.rect.top > HEIGHT :
           self.kill()


pygame.mixer.music.play(-1)  # 輸入重複播放次數，-1為無限重複播放的意思
 

# 遊戲迴圈 #
show_init = True
running = True
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        # 以下這些東西都是遊戲重新開始時要歸零的
        all_sprites = pygame.sprite.Group()  # 創建一個sprite群組，放很多sprite物件
        rocks = pygame.sprite.Group()   # 創建子彈和石頭的另外群組，Sprite()有內建的判斷兩物體是否碰撞的函式，然後記得下面for迴圈石頭加入群組，子彈去shoot()加，然後就可以去all_sprites.update()更新
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()  

        player = Player()
        all_sprites.add(player)
        for i in range(8):
            new_rock()
        score = 0
        # 以上這些東西都是遊戲重新開始時要歸零的

    clock.tick(FPS)  # 一秒鐘更新()次，同步大家遊戲的速度，每個人電腦好壞程度不一
    # 取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()  # 這個函式要自己寫在player裡
    


    # 更新遊戲（動起來）
    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)  # 但是他們消掉後，石頭就沒有了！！！！太酷了，我以為我程式有錯，，groupcollide會回傳字典，撞到的{rock:bullet}
    for hit in hits:    # 所以消掉一顆石頭這邊要再加一顆石頭，還有記得加回石頭群組
        random.choice(expl_sounds).play()
        score += int(hit.radius)  # 教學是在class Rock那邊的radius改成int()，但我不想影響碰撞的半徑判斷，所以我改成這邊用int()
        expl = Explosion(hit.rect.center, "large")
        all_sprites.add(expl)
        if random.random() > 0.9: # 代表有1成的機率會掉寶物
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()

# 加強碰撞判斷：collide_circle為圓形碰撞，必須要給物件radius的屬性才能使用
    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)   # True是把rock刪掉（要加回來），但遊戲要關掉所以寫True意義不大 !!!!!!為什麼這邊 hits 這個變數可以重複？？！！！！！！
    for hit in hits:                                                          # spritecollide 預設是矩形碰撞，但是這樣不精準，所以改成圓形
        new_rock()
        player.health -= int(hit.radius)
        expl = Explosion(hit.rect.center, "small")
        all_sprites.add(expl)
        if player.health <= 0:
            death_expl = Explosion(player.rect.center, "player")
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()
            
# 判斷寶物和飛船碰撞
    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == "shield":
            player.health += 20
            if player.health > 100:
                player.health = 100
            shield_sound.play()
        if hit.type == "gun":
            player.gunup()
            gun_sound.play()

    if player.lives == 0 and not(death_expl.alive()):  # alive()判斷death_expl還有沒有存在
        show_init = True
        


    # 畫面顯示
    screen.fill(BLACK) # (R, G, B) 0-255 用變數代替之後修改方便
    screen.blit(background_img, (0, 0 ))
    all_sprites.draw(screen)  # 把sprites畫出來
    draw_txt(screen, str(score), 18, WIDTH / 2, 10)
    draw_health(screen, player.health, 10, 20)
    draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 20)
    pygame.display.update()

pygame.quit()
