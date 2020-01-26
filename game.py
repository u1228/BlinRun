import pygame
from math import sqrt
import random
import os
import sqlite3


#----------Классы-----------#
class Player(pygame.sprite.Sprite):
    def __init__(self, skin, money=0):
        pygame.sprite.Sprite.__init__(self)
        self.skin = skin
        self.pRun = [pygame.image.load(f"images/sprites/{self.skin}_run{i}.png") for i in range(0, 11) if os.path.isfile(f"images/sprites/{self.skin}_run{i}.png")]
        self.pRtJump = pygame.image.load(f"images/sprites/{self.skin}_jump_down.png")
        self.pJump = pygame.image.load(f"images/sprites/{self.skin}_jump_up.png")
        self.image = self.pRun[0]
        self.rect = self.image.get_rect()
        self.i = 0
        self.v = 5
        self.up = True
        self.isJumping = False
        self.JH = 0
        self.FC = 0
        self.fuel = 100
        self.money = money
        self.maxi = len(self.pRun)
        self.x = -self.image.get_width()
        self.y = win_height - self.image.get_height() - 10
        
    def get_bullet_pos(self):
        if self.skin == "track":
            return (self.x + self.image.get_width() - 30, self.y + 60)
        if self.skin == "monster":
            return (self.x + self.image.get_width(), self.y + 34)
        if self.skin == "car":
            return (self.x + self.image.get_width(), self.y + self.rect.w - 16)
        
    def update(self):
        if self.isJumping:
            if self.up:
                self.image = self.pJump
            else:
                self.image = self.pRtJump
        else:
            self.image = self.pRun[self.i]


    def getJumpHeight(self, maxH=80, speed=2, inAir=30):
        if self.isJumping:
            if self.JH < maxH and self.up:
                self.JH += speed
            elif self.JH == maxH:
                if self.FC < inAir:
                    self.FC += 1
                else:
                    self.up = False
                    self.FC = 0
            elif self.JH - speed <= 0 and not(self.up):
                self.isJumping = False
                self.up = True
                self.JH = 0
            if (not self.up) and self.isJumping and self.JH > 0:
                self.JH -= speed
        return self.JH

    def set_bonus(self, bonus):
        if isinstance(bonus, Money):
            self.money += bonus.power
            coinSound.play()
        elif isinstance(bonus, Fuel):
            self.fuel += bonus.power
            bonusSound.play()
        elif isinstance(bonus, FirstBossBullet) or isinstance(bonus, SecondBossBullet):
            self.fuel -= bonus.power
            hitSound.play()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, whose="player"):
        self.whose = whose
        self.x = x
        self.y = y

    def get_x(self, bullet_speed):
        if self.whose == "player":
            self.x += bullet_speed
        else:
            self.x -= bullet_speed
        return self.x

class Boss(pygame.sprite.Sprite):
    def __init__(self, life):
        pygame.sprite.Sprite.__init__(self)
        self.i = 0
        self.up = 1
        self.j = 0
        self.ready = False
        self.hp = life
        self.next_music = "music/synthwave.mp3"
        self.next_bg = 2

    def get_y(self, a):
        if self.ready:
            self.y += 8 * self.up
            self.j += 1 * self.up
            if self.j == a or self.j == -a:
                self.up = -self.up
        return self.y

    def appears(self):
        pygame.mixer.music.load("music/metal.mp3")
        pygame.mixer.music.play(-1)
        self.ready = True

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            self.ready = False
            pygame.mixer.music.load(self.next_music)
            pygame.mixer.music.play(-1)
            change_bg(self.next_bg)
        
        
class FirstBoss(Boss):
    def __init__(self):
        super().__init__(100)
        self.x = win_width
        self.y = int(win_height * 0.25)
        self.idle = pygame.image.load(f"images/sprites/fBoss.png")
        self.image = self.idle
        
    def reset(self):
        self.__init__()


class SecondBoss(Boss):
    def __init__(self):
        super().__init__(200)
        self.x = win_width
        self.y = win_height - player.image.get_height() - 10
        self.idle = [pygame.image.load(f"images/sprites/sBoss_run{i}.png") for i in range(4)]
        self.image = self.idle[0]
        self.iC = 0
        self.v = 5
        self.next_music = "music/postPunk.mp3"
        self.next_bg = 3
        
    def reset(self):
        self.__init__()
    
    def update(self):
        self.image = self.idle[int(self.iC) % 3]


class Bonus(pygame.sprite.Sprite):
    def __init__(self, power):
        pygame.sprite.Sprite.__init__(self)
        self.power = power
        self.x = win_width
        self.y = random.randint(int(win_height * 0.25), int(win_height * 0.75))
    
    def use(self, character):
        character.set_bonus(self)



class Fuel(Bonus):
    def __init__(self):
        super().__init__(5)
        self.image = pygame.image.load("images/sprites/fuel.png")

class Money(Bonus):
    def __init__(self):
        if bg_index == 3:
            super().__init__(50)
        else:
            super().__init__(10)
        self.image = pygame.image.load("images/sprites/coin.png")


class FirstBossBullet(Bonus):
    def __init__(self):
        super().__init__(10)
        self.image = pygame.image.load("images/sprites/fBossBullet.png")


class SecondBossBullet(Bonus):
    def __init__(self):
        super().__init__(20)
        self.image = pygame.image.load("images/sprites/sBossBullet.png")
        self.y = player.y + player.rect.h // 2


class Button:
    def __init__(self, x, y, width, height, color, label, label_color, function, clickable=True):
        self.rect = pygame.rect.Rect((x, y, width, height))
        self.action = function
        self.label = buttonFont.render(label, True, label_color)
        self.color = color
        r, g, b = color
        r += 50 if r + 50 <= 255 else 255 - r
        g += 50 if g + 50 <= 255 else 255 - g
        b += 50 if b + 50 <= 255 else 255 - b
        self.highColor = (r, g, b)
        self.normalColor = color
        self.clickable = clickable

    def check_Press(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and self.clickable:
            self.action()
            buttonSound.play()
            
    def highlight(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and self.clickable:
            self.color = self.highColor
        elif not self.clickable:
            self.color = (128, 128, 128)
        else:
            self.color = self.normalColor

    def draw(self):
        pygame.draw.rect(win, self.color, self.rect)
        text_rect = self.label.get_rect(center=self.rect.center)
        win.blit(self.label, text_rect)
    
    def setColor(self, color):
        self.color = color
        
    def setText(self, text, text_color=(0, 0, 0)):
        self.label = buttonFont.render(text, True, text_color)
        
    def setClickable(self, state):
        self.clickable = state


#----------Функции-----------#
def drawWin():
    if road_bg:
        win.blit(bg2, (0, 0))
    win.blit(bg, (bgX2, 0))
    win.blit(bg, (bgX1, 0))
    if startAll:
        win.blit(dis, (10, 10))
        win.blit(fuel, (10, 34))
        win.blit(font.render(f"Money: {player.money}", False, (0, 0, 0)), (10, 58))
    if not (game_over or in_menu or in_shop):
        win.blit(player.image, (player.x, player.y))
    for bullet in bullets:
        if bullet.whose == "player":
            win.blit(pBull, (bullet.x, bullet.y))
    for bonus in bonuses:
        win.blit(bonus.image, (bonus.x, bonus.y))
    if FirstBoss.ready:
        win.blit(FirstBoss.image, (FirstBoss.x, FirstBoss.get_y(4)))
        win.blit(fBhp, (FirstBoss.x, 10))
    elif SecondBoss.ready:
        win.blit(SecondBoss.image, (SecondBoss.x, SecondBoss.y))
        win.blit(sBhp, (SecondBoss.x, 10))
    if paused:
        win.blit(pause, (0, 0))
        restartButton.draw()
        menuButton.draw()
        text = titleFont.render("PAUSED", 1, (255, 255, 255))
        text_x = win_width // 2 - text.get_width() // 2
        text_y = win_height // 2 - text.get_height() // 2 - 50
        win.blit(text, (text_x, text_y))
    elif in_menu:
        win.blit(logo, (0, 0))
        playButton.draw()
        exitButton.draw()
        shopButton.draw()
        text = gameTitleFont.render("BlinRun", 1, (200, 73, 0))
        text_x = win_width // 2 - text.get_width() // 2 - 3
        text_y = win_height // 2 - text.get_height() // 2 - 70
        win.blit(text, (text_x, text_y))
        text = gameTitleFont.render("BlinRun", 1, (255, 128, 0))
        text_x = win_width // 2 - text.get_width() // 2
        text_y = win_height // 2 - text.get_height() // 2 - 70
        win.blit(text, (text_x, text_y))
        win.blit(player.image, (win_width // 2 - player.rect.w // 2, win_height - player.image.get_height() - 10))
    elif game_over:
        restartButton.draw()
        menuButton.draw()
        text = titleFont.render("Game Over", 1, (255, 0, 0))
        text_x = win_width // 2 - text.get_width() // 2
        text_y = 10
        win.blit(text, (text_x, text_y))
        text = font.render(f"Score: {metres}", 1, (0, 0, 0))
        text_x = win_width // 2 - text.get_width() // 2
        text_y = win_height // 2 - text.get_height() // 2 - 50
        win.blit(text, (text_x, text_y))
        best = cur.execute('select score from records').fetchone()[0]
        if best < metres:
            cur.execute(f'update records set score = {metres} where id = 1')
            con.commit()
            best = metres + 0
        text = font.render(f"Best score: {best}", 1, (0, 0, 0))
        text_x = win_width // 2 - text.get_width() // 2
        text_y = win_height // 2 - text.get_height() // 2 - 25
        win.blit(text, (text_x, text_y))
    elif in_shop:
        shopMenuButton.draw()
        shopTrackButton.draw()
        shopCarButton.draw()
        shopMonsterButton.draw()
        win.blit(trackSprite, (win_width // 2 - 228, win_height // 2 + 76))
        win.blit(carSprite, (win_width // 2 - 76, win_height // 2 + 76))
        win.blit(monsterSprite, (win_width // 2 + 76, win_height // 2 + 76))
        if player.skin == 'track':
            win.blit(sold, (win_width // 2 - 228, win_height // 2 + 76))
        elif player.skin == 'car':
            win.blit(sold, (win_width // 2 - 76, win_height // 2 + 76))
        elif player.skin == 'monster':
            win.blit(sold, (win_width // 2 + 76, win_height // 2 + 76))
        text = titleFont.render("Shop", 1, (255, 255, 0))
        text_x = win_width // 2 - text.get_width() // 2
        text_y = 10
        win.blit(text, (text_x, text_y))
        win.blit(shopText, (20, win_height - 180))
    color = (255 - int(clock.get_fps() / fps * 255) % 256, int(clock.get_fps() / fps * 255) % 256, 0)
    fpsd = smallFont.render(f"fps: {int(clock.get_fps())}", True, color)
    win.blit(fpsd, (win_width - 100, 10))
    pygame.display.flip()

    
def checkBonuses(bonuses):
    i = 0
    while i < len(bonuses):
        bonus = bonuses[i]
        if bonus.x + bonus.image.get_width() < 0:
            del bonuses[i]
        elif player.x < bonus.x + bonus.image.get_width() and bonus.x < player.x + player.image.get_width() and\
            bonus.y > player.y and bonus.y + bonus.image.get_height() < player.y + player.image.get_height():
                bonuses[i].use(player)
                del bonuses[i]
        else:
            if not (isinstance(bonuses[i], FirstBossBullet) or isinstance(bonuses[i], SecondBossBullet)):
                bonuses[i].x -= v / fps
            else:
                bonuses[i].x -= 2 * v / fps
        i += 1


def checkBullet(bullets):
    global fBhp, sBhp
    i = 0
    a = FirstBoss.x
    b = FirstBoss.x + FirstBoss.idle.get_width()
    c = FirstBoss.ready
    d = FirstBoss.y
    e = FirstBoss.y + int(FirstBoss.idle.get_height() * 0.75)
    while i < len(bullets):
        bullets[i].get_x(8)
        if bullets[i].x > win_width:
            del bullets[i]
        elif bullets[i].x > a and bullets[i].x < b and c:
            if bullets[i].y > d and bullets[i].y < e:
                FirstBoss.damage(10)
                del bullets[i]
                fBhp = font.render(f'HP: {FirstBoss.hp}', False, (0, 0, 0))
        i += 1
    i = 0
    a = SecondBoss.x
    b = SecondBoss.x + SecondBoss.idle[0].get_width()
    c = SecondBoss.ready
    d = SecondBoss.y
    e = SecondBoss.y + int(SecondBoss.idle[0].get_height() * 0.75)
    while i < len(bullets):
        bullets[i].get_x(8)
        if bullets[i].x > win_width:
            del bullets[i]
        elif bullets[i].x > a and bullets[i].x < b and c:
            if bullets[i].y > d and bullets[i].y < e:
                SecondBoss.damage(10)
                del bullets[i]
                sBhp = font.render(f'HP: {SecondBoss.hp}', False, (0, 0, 0))
        i += 1
       

def startGame():
    global frC, player, startAll, v, in_menu, game_over, bullets, bonuses, js1, paused, in_shop, music, bg_index
    bg_index = 1
    music = "music/8bit.mp3"
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(-1)
    
    change_bg(1)
    FirstBoss.reset()
    SecondBoss.reset()
    
    frC = 1
    result = cur.execute("select skin, money from player").fetchone()
    player = Player(*result)
    startAll = True
    v = 500
    in_menu = False
    in_shop = False
    game_over = False
    bullets = []
    bonuses = []
    js1 = jumpSpeed - 0
    paused = False
    
    result = cur.execute("select * from recent;").fetchone()
    if result is not None:
        change_bg(result[0])
        
        frC = result[1]
        player.fuel = result[2]
        
        cur.execute("delete from recent;")
        con.commit()
   
def endGame():
    global WinRun
    WinRun = False
    
def toMenu():
    global in_menu, paused, game_over, y, bonuses, bullets, in_shop
    in_menu = True
    in_shop = False
    paused = False
    game_over = False
    bonuses = []
    bullets = []
    music = "music/menu.mp3"
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(-1)
    FirstBoss.reset()
    SecondBoss.reset()

def toShop():
    global in_menu, in_shop
    in_menu = False
    in_shop = True
    music = "music/shop.mp3"
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(-1)
    result = cur.execute('select track, car, monster from shop').fetchone()
    if result[0] == 1:
        shopTrackButton.setColor((128, 128, 128))
        shopTrackButton.setText("Sold")
        shopTrackButton.setClickable(False)
    else:
        shopTrackButton.setColor((255, 255, 128))
        shopTrackButton.setText("1000$")
    if result[1] == 1:
        shopCarButton.setColor((128, 128, 128))
        shopCarButton.setText("Sold")
        shopCarButton.setClickable(False)
    else:
        shopCarButton.setColor((255, 255, 128))
        shopCarButton.setText("5000$")
    if result[2] == 1:
        shopMonsterButton.setColor((128, 128, 128))
        shopMonsterButton.setText("Sold")
        shopMonsterButton.setClickable(False)
    else:
        shopMonsterButton.setColor((255, 255, 128))
        shopMonsterButton.setText("10000$")

def nothing():
    pass

def buyCar():
    global player, shopText
    if player.money >= 5000:
        player = Player('car', player.money - 5000)
        shopText = smallFont.render("Purchase completed successfully", False, (0, 255, 0))
        cur.execute(f'update player set skin = "car", money = {player.money} where id = 1;')
        cur.execute('update shop set car = 1 where id = 1;')
        con.commit()
        shopCarButton.setColor((128, 128, 128))
        shopCarButton.setText("Sold")
        shopCarButton.setClickable(False)
    else:
        shopText = smallFont.render("You haven't got enought money", False, (255, 0, 0))

def buyMonster():
    global player, shopText
    if player.money >= 10000:
        player = Player('monster', player.money - 10000)
        shopText = smallFont.render("Purchase completed successfully", False, (0, 255, 0))
        cur.execute(f'update player set skin = "monster", money = {player.money} where id = 1;')
        cur.execute('update shop set monster = 1 where id = 1;')
        con.commit()
        shopMonsterButton.setColor((128, 128, 128))
        shopMonsterButton.setText("Sold")
        shopMonsterButton.setClickable(False)
    else:
        shopText = smallFont.render("You haven't got enought money", False, (255, 0, 0))
        

def setSkinTo(skin, fuel):
    global player
    result = cur.execute(f'select {skin} from shop').fetchone()
    if result[0] == 1:
        player = Player(skin, player.money)
        cur.execute(f'update player set skin = "{skin}" where id = 1;')
        con.commit()
        
def change_bg(index):
    global bg, bg_name, bgX2, bgX1, road_bg, bg2, bg_index
    bg_index = index + 0
    if index == 1:
        bg_name = "images/BG/pixelbg.png"
        bg = pygame.image.load(bg_name)
        bgX2 = bg.get_width()
        bgX1 = 0
        road_bg = False
    elif index == 2:
        bg_name = "images/BG/road.png"
        bg = pygame.image.load(bg_name)
        road_bg = True
        bg2 = pygame.image.load("images/BG/bg.jpg")
        bg2 = pygame.transform.scale(bg2, (win_width, win_height - 64))
        bgX2 = bg.get_width()
        bgX1 = 0
    elif index == 3:
        bg_name = "images/BG/road.png"
        bg = pygame.image.load(bg_name)
        road_bg = True
        bg2 = pygame.image.load("images/BG/sunset.jpg")
        bg2 = pygame.transform.scale(bg2, (win_width, win_height - 64))
        bgX2 = bg.get_width()
        bgX1 = 0

#----------Окно-----------#
win_height = 512
win_width = int(((1+sqrt(5)) / 2) * win_height) # - "Золотое сечение".
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("BlinRun")
WinRun = True

#----------pygame----------#
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

bg_name = "images/BG/pixelbg.png"
bg = pygame.image.load(bg_name)
if 'road' in bg_name:
    road_bg = True
    bg2 = pygame.image.load("images/BG/sunset.jpg")
    bg2 = pygame.transform.scale(bg2, (win_width, win_height - 64))
else:
    road_bg = False
    bg2 = None
bgX2 = bg.get_width()
bg_index = 1
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 24)
titleFont = pygame.font.SysFont('Book Antiqua', 40)
gameTitleFont = pygame.font.Font('other/titleFont.ttf', 72)
buttonFont = pygame.font.SysFont('Impact', 18)
smallFont = pygame.font.SysFont('Courier New', 14)
pBull = pygame.image.load("images/sprites/P_bullet.png")
music = "music/menu.mp3"
pause = pygame.image.load("images/BG/pause.png")
pause = pygame.transform.scale(pause, (win_width, win_height))
carSprite = pygame.image.load("images/sprites/car_run0.png")
monsterSprite = pygame.image.load("images/sprites/monster_run0.png")
trackSprite = pygame.image.load("images/sprites/track_run0.png")
sold = pygame.image.load("images/sprites/have.png")
sold = pygame.transform.scale(sold, (50, 50))
logo = pygame.image.load("images/sprites/logo.png")
logo = pygame.transform.scale(logo, (102, 76))

bonusSound = pygame.mixer.Sound("sounds/bonus.wav")
coinSound = pygame.mixer.Sound("sounds/coin.wav")
gameOverSound = pygame.mixer.Sound("sounds/game_over.wav")
jumpSound = pygame.mixer.Sound("sounds/jump.wav")
shotSound = pygame.mixer.Sound("sounds/shot.wav")
buttonSound = pygame.mixer.Sound("sounds/button.wav")
hitSound = pygame.mixer.Sound("sounds/hit.wav")
pygame.mixer.music.load(music)
pygame.mixer.music.play(-1)

#----Дополнительные подготовки-----#

con = sqlite3.connect("other/main.db")
cur = con.cursor()

if os.path.isfile("other/first.txt"):
    os.remove("other/first.txt")
    cur.execute("delete from player;")
    cur.execute('insert into player values ("track", 0, 1);')
    cur.execute("delete from records;")
    cur.execute('insert into records values (1, 0);')
    cur.execute("delete from recent;")
    cur.execute('delete from shop;')
    cur.execute('insert into shop values (1, 1, 0, 0);')
    con.commit()

#----------Переменные-----------#
fps = 60

i = 0
v = 500

bgX1 = 0
WinRun = True
jumpSpeed = 20                  # максимальная скорость прыжка
js1 = jumpSpeed - 0             # Скорость прыжка
bullets = []
bullet_delay = 20               # Максимальное время между вылетами пуль
bonuses = []
bC = 0                          # Время между вылетами пуль
startAll = False
paused = False
in_menu = True
in_shop = False
game_over = False
frC = 1                         # На самом деле, это и есть расстояние.
fbdeadC = 0                     # Сколько прошло с того момента, как первый босс умер
metres = 0
result = cur.execute("select skin, money from player;").fetchone()
player = Player(*result)
y1 = player.y * 1
FirstBoss = FirstBoss()
SecondBoss = SecondBoss()
dis = font.render(f'Distance: {metres} m.', False, (0, 0, 0))
fuel = font.render(f'HP: {player.fuel}', False, (0, 0, 0))
fBhp = font.render(f'HP: {FirstBoss.hp}', False, (0, 0, 0))
sBhp = font.render(f'HP: {SecondBoss.hp}', False, (0, 0, 0))
clock = pygame.time.Clock()
playButton = Button(win_width // 2 + 5, win_height // 2 - 25, 50, 50, (128, 255, 128), 'Play', (0, 0, 0), startGame)
exitButton = Button(win_width - 50, win_height - 50, 50, 50, (255, 128, 128), 'Exit', (0, 0, 0), endGame)
restartButton = Button(win_width // 2 - 50, win_height // 2 + 25, 100, 50, (128, 255, 128), 'Restart', (0, 0, 0), startGame)
menuButton = Button(win_width // 2 - 50, win_height // 2 + 85, 100, 50, (255, 128, 128), 'Menu', (0, 0, 0), toMenu)
shopButton = Button(win_width // 2 - 55, win_height // 2 - 25, 50, 50, (255, 255, 128), 'Shop', (0, 0, 0), toShop)
shopMenuButton = Button(win_width - 50, win_height - 50, 50, 50, (255, 128, 128), 'Menu', (0, 0, 0), toMenu)
shopTrackButton = Button(win_width // 2 - 228, win_height // 2 - 76, 150, 50, (128, 128, 128), 'Sold', (0, 0, 0), nothing)
shopCarButton = Button(win_width // 2 - 76, win_height // 2 - 76, 150, 50, (255, 255, 128), '5000$', (0, 0, 0), buyCar)
shopMonsterButton = Button(win_width // 2 + 76, win_height // 2 - 76, 150, 50, (255, 255, 128), '10000$', (0, 0, 0), buyMonster)
shopText = smallFont.render("", False, (0, 0, 0))

#----------Основной цикл-----------#

while WinRun:
    keys = pygame.key.get_pressed()
    drawWin()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            WinRun = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not (in_menu or game_over or in_shop):
                startAll = not startAll
                paused = not paused
                if paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
        elif event.type == pygame.MOUSEBUTTONDOWN: # Обеспечение работы кнопок
            if in_menu:
                playButton.check_Press(event.pos)
                exitButton.check_Press(event.pos)
                shopButton.check_Press(event.pos)
            elif game_over or paused:
                restartButton.check_Press(event.pos)
                menuButton.check_Press(event.pos)
            elif in_shop:
                shopMenuButton.check_Press(event.pos)
                shopTrackButton.check_Press(event.pos)
                shopCarButton.check_Press(event.pos)
                shopMonsterButton.check_Press(event.pos)
                if pygame.Rect(win_width // 2 - 228, win_height // 2 + 76, 152, 152).collidepoint(event.pos):
                    setSkinTo("track", 100)
                if pygame.Rect(win_width // 2 - 76, win_height // 2 + 76, 152, 152).collidepoint(event.pos):
                    setSkinTo("car", 250)
                if pygame.Rect(win_width // 2 + 76, win_height // 2 + 76, 152, 152).collidepoint(event.pos):
                    setSkinTo("monster", 500)
        elif event.type == pygame.MOUSEMOTION:
            if in_menu:
                playButton.highlight(event.pos)
                exitButton.highlight(event.pos)
                shopButton.highlight(event.pos)
            elif game_over or paused:
                restartButton.highlight(event.pos)
                menuButton.highlight(event.pos)
            elif in_shop:
                shopMenuButton.highlight(event.pos)
                shopTrackButton.highlight(event.pos)
                shopCarButton.highlight(event.pos)
                shopMonsterButton.highlight(event.pos)

    if startAll: # Игровой процесс
        
        
        i += player.v / fps
        player.i = int(i) % player.maxi
        player.update()
        SecondBoss.iC += SecondBoss.v / fps
        SecondBoss.update()

        metres_was = metres + 0
        frC += 1 / fps
        metres = int(frC)
        
        if metres == 20 and not FirstBoss.ready:
            FirstBoss.appears()
        if metres > 20 and not FirstBoss.ready and fbdeadC == 0:
            fbdeadC = 1
            
        if fbdeadC == 20 and not SecondBoss.ready:
            SecondBoss.appears()
            fbdeadC = -1

        if metres != metres_was:
            if metres % random.randint(2, 10) == 0:
                bonuses.append(Fuel())
            elif FirstBoss.ready:
                bonuses.append(FirstBossBullet())
            elif SecondBoss.ready:
                bonuses.append(SecondBossBullet())
            elif not metres % random.randint(3, 10) == 0:
                bonuses.append(Money())
            player.fuel -= 2
            if fbdeadC > 0:
                fbdeadC += 1

        dis = font.render(f'Distance: {metres} m.', False, (0, 0, 0))
        fuel = font.render(f'Fuel: {player.fuel}', False, (0, 0, 0))


        bgX1 -= v / fps
        bgX2 -= v / fps
        if bgX1 < bg.get_width() * -1:
            bgX1 = bg.get_width()
        if bgX2 < bg.get_width() * -1:
            bgX2 = bg.get_width()
        start = False
        if player.x < 10:
            player.x += 3
        else:
            start = True
        if FirstBoss.ready:
            if FirstBoss.x > win_width - FirstBoss.idle.get_width() - 10:
                FirstBoss.x -= 8
        elif SecondBoss.ready:
            if SecondBoss.x > win_width - SecondBoss.idle[0].get_width() - 10:
                SecondBoss.x -= 8
        if start:
            if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and not player.isJumping: # Начало прыжка
                player.isJumping = True
                jumpSound.play()
            elif player.isJumping: # Продолжение прыжка
                player.y = y1 - player.getJumpHeight(320, js1, 10)
                if js1 > 5 and player.up:
                    js1 -= 1
                elif js1 < jumpSpeed and not(player.up):
                    js1 += 1
            if keys[pygame.K_z]: # выстрел
                if bC == 0:
                    bC = bullet_delay
                    pBullet = Bullet(*player.get_bullet_pos())
                    bullets.append(pBullet)
                    shotSound.play()
            if bC != 0:
                bC -= 1
            checkBullet(bullets)
            checkBonuses(bonuses)
        if player.fuel <= 0: # Проигрыш
            startAll = False
            game_over = True
            pygame.mixer.music.stop()
            gameOverSound.play()
            cur.execute(f'update player set skin = "{player.skin}", money = {player.money} where id = 1;')
            con.commit()
    clock.tick(fps)

#--------------Конец---------------#

if not in_menu and not game_over and not in_shop: # Сохранение при непредвиденном выходе
    cur.execute(f'insert into recent values ({bg_index}, {metres}, {player.fuel});')
    con.commit()