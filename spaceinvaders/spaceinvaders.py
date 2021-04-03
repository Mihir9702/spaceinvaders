import pygame, os, time, random

pygame.init()
pygame.font.init()

# Screen
width, height = 750, 750
win = pygame.display.set_mode((width, height))
pygame.display.set_caption('Space Invaders')

# Images
red_ss = pygame.image.load('spaceinvaders/assets/ps_redsmall.png')
green_ss = pygame.image.load('spaceinvaders/assets/ps_greensmall.png')
blue_ss = pygame.image.load('spaceinvaders/assets/ps_bluesmall.png')

# Player Ship
yellow_ss = pygame.image.load('spaceinvaders/assets/ps_yellow.png')

# Lasers
red_laser = pygame.image.load('spaceinvaders/assets/pl_red.png')
green_laser = pygame.image.load('spaceinvaders/assets/pl_green.png')
blue_laser = pygame.image.load('spaceinvaders/assets/pl_blue.png')
yellow_laser = pygame.image.load('spaceinvaders/assets/pl_yellow.png')

# Background
bg = pygame.transform.scale((pygame.image.load('spaceinvaders/assets/background.png')), (width,height))


class SHIP:
    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x,self.y))
        for laser in self.lasers:
            laser.draw(win)
    
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = LASER(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()

class ENEMY(SHIP):
    color_map = {
                'red' : (red_ss, red_laser),
                'green' : (green_ss, green_laser),
                'blue' : (blue_ss, blue_laser)
                }
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.color_map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = LASER(self.x - 15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class LASER:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, vel):
        self.y += vel
    
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)
    

class PLAYER(SHIP):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = yellow_ss
        self.laser_img = yellow_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height): 
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x,self.y + self.ship_img.get_height() + 10,self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x,self.y + self.ship_img.get_height() + 10,self.ship_img.get_width() * (self.health / self.max_health), 10))

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    fps = 60
    level = 0
    lives = 5
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('comicsans', 50)
    lost_font = pygame.font.SysFont('comicsans', 60)
    player = PLAYER(300, 650)
    player_vel = 5

    laser_vel = 4

    enemies = []
    wave_length = 5
    enemy_vel = 1

    lost = False
    lost_count = 0

    def redraw():
        win.blit(bg, (0,0))
        # Draw Text
        lives_label = font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = font.render(f"Level: {level}", 1, (255,255,255))
        win.blit(lives_label, (10,10))
        win.blit(level_label, (width - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(win)

        if lost:
            lost_label = lost_font.render('You Lost!', 1, (255,255,255))
            win.blit(lost_label, (width/2 - lost_label.get_width/2, 350))
        player.draw(win)
        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost += 1
        
        if lost:
            if lost_count > fps * 3:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = ENEMY(random.randrange(50, width-100), random.randrange(-1500, -100), random.choice(['red', 'blue', 'green']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < width:
            player.x += player_vel
        if keys[pygame.K_a] and player.x + player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < height:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if random.randrange(0,120) == 1:
                enemy.shoot()
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)
        player.move_lasers(-laser_vel - 5, enemies)

def main_menu():
    title_font = pygame.font.SysFont('comicsans', 70)
    run = True
    while run:
        win.blit(bg, (0,0))
        title_label = title_font.render('Press the mouse to begin...', 1, (255,255,255))
        win.blit(title_label, (width/2 - title_label.get_width()/2, 350))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()
main_menu()