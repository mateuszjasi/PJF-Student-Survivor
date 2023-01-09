import os
import random
import pygame
import math
import json
from sys import exit
from random import randint


def play_music(song, time=0):
    pygame.mixer.music.unload()
    pygame.mixer.music.load(song["name"])
    pygame.mixer.music.set_volume(song["volume"])
    pygame.mixer.music.play(-1, time)


def fade_to(function):
    global fading, fading_alpha, fading_in, fade_out_to
    fading = True
    fading_alpha = 0
    fading_in = True
    fade_out_to = function


def fading_effect():
    global fading, fading_in, fading_alpha, fade_out_to
    alphaSurface.set_alpha(fading_alpha)
    if not fading_in:
        fade_out_to()
    screen.blit(alphaSurface, (0, 0))
    if fading_in:
        fading_alpha += 5
    else:
        fading_alpha -= 5
    if fading_alpha > 100:
        fading_alpha = 100
        fading_in = False
    elif fading_alpha < 0:
        fading = False


def close_app():
    file = open("data.txt", "w")
    file.write(str(global_money) + '\n')
    for i in bought_upgrades:
        file.write(str(bought_upgrades[i][0]) + '\n')
    file.close()
    pygame.quit()
    exit()


def main_menu():
    screen.blit(main_menu_background, (0, 0))
    buttons["start_game"].process()
    buttons["open_shop"].process()
    buttons["close_up"].process()


def shop():
    screen.blit(shop_background, (0, 0))
    for tile in range(0, len(shop_tiles)):
        shop_tiles[tile].process()
    buttons["close_shop"].process()
    money_text = fonts["in_game_money"].render("Money: " + str(global_money), True, (255, 255, 255))
    money_rect = money_text.get_rect(bottomleft=(10, screen.get_height() - 10))
    screen.blit(money_text, money_rect)


def buy_upgrade(arguments):
    global bought_upgrades, global_money
    if global_money >= bought_upgrades[arguments[0]][3] * (bought_upgrades[arguments[0]][0] + 1):
        global_money -= bought_upgrades[arguments[0]][3] * (bought_upgrades[arguments[0]][0] + 1)
        bought_upgrades[arguments[0]][0] += 1


def take_upgrade(arguments):
    global level_up, choose_options
    taken_upgrades[arguments[0]][0] += 1
    player.sprite.curr_stats[arguments[0]] = \
        player.sprite.base_stats[arguments[0]] + taken_upgrades[arguments[0]][0] * taken_upgrades[arguments[0]][2]
    if arguments[0] == "Health":
        player.sprite.curr_stats[arguments[0]] += bought_upgrades[arguments[0]][0] * bought_upgrades[arguments[0]][4]
        player.sprite.health += 1
    else:
        player.sprite.curr_stats[arguments[0]] = \
            round(player.sprite.curr_stats[arguments[0]] + player.sprite.curr_stats[arguments[0]]
                  * bought_upgrades[arguments[0]][0] * bought_upgrades[arguments[0]][4], 2)
    level_up = False
    choose_options = True


def pause_menu():
    buttons["unpause_game"].process()
    buttons["end_game"].process()


def player_level_up():
    global block_button, level_up
    block_button = 60
    level_up = True


def level_up_menu():
    global choose_options, option1, option2, option3, block_button
    if block_button > 0:
        block_button -= 1
    if choose_options:
        option1, option2, option3 = random.sample(range(0, len(upgrade_tiles)), 3)
        choose_options = False
    upgrade_tiles[option1].process(screen.get_width() / 2 - 350, screen.get_height() / 2)
    upgrade_tiles[option2].process(screen.get_width() / 2, screen.get_height() / 2)
    upgrade_tiles[option3].process(screen.get_width() / 2 + 350, screen.get_height() / 2)


def death_screen_menu():
    screen.blit(death_background, (0, 0))
    buttons["death_screen"].process()


def end_game():
    global global_money, game_active, game_pause, death_screen, minutes, seconds
    enemies.empty()
    bullets.empty()
    drops.empty()
    global_money += player.sprite.money
    player.remove()
    minutes, seconds = 0, 0
    game_active, game_pause, death_screen = False, False, False
    play_music(music["main_menu"], 3)
    fade_to(main_menu)


def clock_update():
    global minutes, seconds
    if seconds >= 60:
        minutes += 1
        seconds = 0
        if minutes % 2 == 0:
            spawn_boss()
    if minutes >= 10 and len(enemies) == 0:
        for i in range(0, max_enemies):
            enemies.add(Enemy(enemy_stats['death']))
    time_label = fonts["progress_bar"].render("{:02}:{:02}".format(minutes, seconds), True, 'white')
    time_label_rect = time_label.get_rect(center=(screen.get_width() / 2, 50))
    screen.blit(time_label, time_label_rect)


def game_update():
    screen.blit(game_background, (0, 0))
    drops.draw(screen)
    enemies.draw(screen)
    enemies.update()
    bullets.draw(screen)
    bullets.update()
    player.draw(screen)
    player.update()
    clock_update()


def start_game():
    global game_active, max_enemies
    max_enemies = 20
    for i in taken_upgrades:
        taken_upgrades[i][0] = 0
    game_active = True
    player.add(Player(player_stats))
    play_music(music["game_background"])
    fade_to(game_update)


def open_shop():
    global upgrade_shop
    upgrade_shop = True
    fade_to(shop)


def close_shop():
    global upgrade_shop
    upgrade_shop = False
    fade_to(main_menu)


def pause_game():
    global game_pause
    game_pause = True
    screen.fill((50, 50, 50), special_flags=pygame.BLEND_RGB_SUB)
    player_stats_text = "Player statistics: "
    player_stats_label_text = fonts["progress_bar"].render(player_stats_text, True, 'white')
    max_width = player_stats_label_text.get_width()
    for i in player.sprite.curr_stats:
        player_stats_text = i + ": " + str(player.sprite.curr_stats[i] if i != "Fire rate"
                                           else round(1 / (player.sprite.curr_stats[i] / 60), 2))
        player_stats_label_text = fonts["pause_menu_player_stats"].render(player_stats_text, True, 'white')
        if max_width < player_stats_label_text.get_width():
            max_width = player_stats_label_text.get_width()
    player_stats_rect = pygame.rect.Rect(0, 0, max_width + 40,
                                         25 + player_stats_label_text.get_height() * (
                                                 len(player.sprite.curr_stats) + 2))
    player_stats_rect.topright = (screen.get_width() - 100, 50)
    player_stats_surface = pygame.transform.scale(pygame.image.load("graphics/tile.png").convert_alpha(),
                                                  (player_stats_rect.width, player_stats_rect.height))
    player_stats_text = "Player statistics: "
    player_stats_label_text = fonts["progress_bar"].render(player_stats_text, True, 'white')
    player_stats_label_text_rect = player_stats_label_text.get_rect(topleft=(20, 25))
    player_stats_surface.blit(player_stats_label_text, player_stats_label_text_rect)
    for x, i in enumerate(player.sprite.curr_stats):
        player_stats_text = i + ": " + str(player.sprite.curr_stats[i] if i != "Fire rate"
                                           else round(1 / (player.sprite.curr_stats[i] / 60), 2))
        player_stats_label_text = fonts["pause_menu_player_stats"].render(player_stats_text, True, 'white')
        if max_width < player_stats_label_text.get_width():
            max_width = player_stats_label_text.get_width()
        player_stats_label_text_rect = player_stats_label_text.get_rect(
            topleft=(20, 35 + player_stats_label_text.get_height() * (x + 1)))
        player_stats_surface.blit(player_stats_label_text, player_stats_label_text_rect)
    screen.blit(player_stats_surface, player_stats_rect)
    pygame.mixer.music.pause()


def unpause_game():
    global game_pause
    game_pause = False
    pygame.mixer.music.unpause()


def player_died(player_money):
    global death_screen, global_money
    death_screen = True
    global_money += player_money
    screen.fill('darkgrey')
    play_music(music["game_over"])


def spawn_enemy():
    enemy_chance = randint(1, 10)
    if minutes == 0:
        enemies.add(Enemy(enemy_stats["wisp"]))
    elif minutes == 1:
        if enemy_chance == 2:
            enemies.add(Enemy(enemy_stats["book"]))
        else:
            enemies.add(Enemy(enemy_stats["wisp"]))
    elif minutes == 2:
        if enemy_chance <= 6:
            enemies.add(Enemy(enemy_stats["book"]))
        else:
            enemies.add(Enemy(enemy_stats["wisp"]))
    elif minutes == 3:
        if enemy_chance == 2:
            enemies.add(Enemy(enemy_stats["bite"]))
        elif enemy_chance <= 8:
            enemies.add(Enemy(enemy_stats["book"]))
        else:
            enemies.add(Enemy(enemy_stats["wisp"]))
    elif minutes == 4:
        if enemy_chance <= 5:
            enemies.add(Enemy(enemy_stats["bite"]))
        else:
            enemies.add(Enemy(enemy_stats["book"]))
    elif minutes == 5:
        if enemy_chance <= 1:
            enemies.add(Enemy(enemy_stats["wisp_hard"]))
        else:
            enemies.add(Enemy(enemy_stats["bite"]))
    elif minutes == 6:
        if enemy_chance <= 8:
            enemies.add(Enemy(enemy_stats["wisp_hard"]))
        else:
            enemies.add(Enemy(enemy_stats["wisp"]))
    elif minutes == 7:
        if enemy_chance <= 2:
            enemies.add(Enemy(enemy_stats["bite_hard"]))
        elif enemy_chance <= 8:
            enemies.add(Enemy(enemy_stats["wisp_hard"]))
        else:
            enemies.add(Enemy(enemy_stats["book"]))
    elif minutes == 8:
        if enemy_chance == 1:
            enemies.add(Enemy(enemy_stats["shadow"]))
        elif enemy_chance <= 7:
            enemies.add(Enemy(enemy_stats["bite_hard"]))
        else:
            enemies.add(Enemy(enemy_stats["bite"]))
    elif minutes == 9:
        if enemy_chance <= 3:
            enemies.add(Enemy(enemy_stats["shadow_hard"]))
        else:
            enemies.add(Enemy(enemy_stats["golem"]))


def spawn_boss():
    global max_enemies
    if minutes == 2:
        max_enemies = 30
        enemies.add(Enemy(enemy_stats["shadow_boss"]))
    if minutes == 4:
        max_enemies = 40
        enemies.add(Enemy(enemy_stats["golem_boss"]))
    if minutes == 6:
        max_enemies = 50
        enemies.add(Enemy(enemy_stats["shadow_hard_boss"]))
    if minutes == 8:
        max_enemies = 60
        enemies.add(Enemy(enemy_stats["golem_boss"]))
        enemies.add(Enemy(enemy_stats["golem_boss"]))
        enemies.add(Enemy(enemy_stats["shadow_boss"]))
        enemies.add(Enemy(enemy_stats["shadow_boss"]))
        enemies.add(Enemy(enemy_stats["shadow_hard_boss"]))
    if minutes == 10:
        enemies.empty()
        enemies.add(Enemy(enemy_stats["death"]))


def generate_shop_tiles():
    global shop_tiles
    height, width = 300, 300
    x, y = 30, 20
    for i in bought_upgrades:
        shop_tiles.append(ShopTile(x, y, width, height, i))
        x += width + 10
        if x + width + 10 >= screen.get_width():
            x = 30
            y += height + 20


def generate_upgrade_tiles():
    global upgrade_tiles
    height, width = 300, 300
    for i in taken_upgrades:
        upgrade_tiles.append(UpgradeTile(width, height, i))


class Button:
    def __init__(self, x, y, width, height, buttonText='Button',
                 onclickFunction=None, arguments=None, active=True, shop_button=False):
        self.x = x
        self.y = y
        self.shop_button = shop_button
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.arguments = arguments
        self.active = active
        self.alreadyPressed = False
        self.fillColors = {
            'normal': (0, 0, 0, 0),
            'hover': (75, 75, 75, 0),
            'pressed': (150, 150, 150, 0),
        }
        self.image = pygame.transform.scale(pygame.image.load("graphics/button.png").convert_alpha(),
                                            (self.width, self.height))
        self.buttonSurface = self.image.copy()
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.buttonRect.center = (self.x, self.y)
        self.buttonText = buttonText
        self.alreadyPressed = False

    def process(self):
        if self.shop_button:
            button_surf = fonts["shop_button"].render(self.buttonText, True, (255, 255, 255))
        else:
            button_surf = fonts["button"].render(self.buttonText, True, (255, 255, 255))
        mouse_position = pygame.mouse.get_pos()
        self.buttonSurface = self.image.copy()
        if self.active:
            self.buttonSurface.fill(self.fillColors['normal'], special_flags=pygame.BLEND_RGBA_SUB)
            if self.buttonRect.collidepoint(mouse_position):
                if pygame.mouse.get_pressed()[0]:
                    self.buttonSurface.fill(self.fillColors['pressed'], special_flags=pygame.BLEND_RGBA_SUB)
                    if not self.alreadyPressed:
                        pygame.mixer.Sound.play(click_sound)
                        if self.arguments:
                            self.onclickFunction(self.arguments)
                        else:
                            self.onclickFunction()
                        self.alreadyPressed = True
                else:
                    self.buttonSurface.fill(self.fillColors['hover'], special_flags=pygame.BLEND_RGBA_SUB)
                    self.alreadyPressed = False
        else:
            self.buttonSurface.fill(self.fillColors['pressed'], special_flags=pygame.BLEND_RGBA_SUB)
            button_surf = fonts["button"].render(self.buttonText, True, (0, 0, 0))
        self.buttonSurface.blit(button_surf, [
            self.buttonRect.width / 2 - button_surf.get_rect().width / 2,
            self.buttonRect.height / 2 - button_surf.get_rect().height / 2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)


class ShopTile:
    def __init__(self, x, y, width, height, upgrade_name="Tile"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.upgrade_name = upgrade_name
        self.image = pygame.transform.scale(pygame.image.load("graphics/tile.png").convert_alpha(),
                                            (self.width, self.height))
        self.tileSurface = self.image
        self.tileRect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.tileName = fonts["shop_tile_name"].render(upgrade_name, True, (255, 255, 255))
        self.fillColors = {
            'normal': (0, 0, 0, 0),
            'fully_upgraded': (150, 150, 150, 0)
        }
        self.buy_button = Button(self.tileRect.centerx, self.tileRect.bottom - 45, 150, 60,
                                 str((bought_upgrades[self.upgrade_name][0] + 1)
                                     * bought_upgrades[self.upgrade_name][3]), buy_upgrade, [self.upgrade_name],
                                 True if bought_upgrades[self.upgrade_name][0]
                                         < bought_upgrades[self.upgrade_name][1] else False, True)

    def process(self):
        self.tileSurface = self.image.copy()
        if bought_upgrades[self.upgrade_name][0] < bought_upgrades[self.upgrade_name][1]:
            self.tileSurface.fill(self.fillColors['normal'], special_flags=pygame.BLEND_RGBA_SUB)
        else:
            self.tileSurface.fill(self.fillColors['fully_upgraded'], special_flags=pygame.BLEND_RGBA_SUB)
        self.tileSurface.blit(self.tileName, [self.tileRect.width / 2 - self.tileName.get_rect().width / 2, 15])
        tile_lvl = fonts["shop_tile_name"].render("Lvl " + str(bought_upgrades[self.upgrade_name][0]) + " / " +
                                                  str(bought_upgrades[self.upgrade_name][1]), True, (255, 255, 255))
        self.tileSurface.blit(tile_lvl, [self.tileRect.width / 2 - tile_lvl.get_rect().width / 2, 15 + self.tileName.get_height()])
        word_x, word_y = 15, 75
        word_height = 0
        for lines in [word.split(' ') for word in bought_upgrades[self.upgrade_name][2].splitlines()]:
            for words in lines:
                word_surface = fonts["shop_tile_text"].render(words, True, (255, 255, 255))
                word_width, word_height = word_surface.get_size()
                if word_x + word_width >= self.width - 5:
                    word_x = 15
                    word_y += word_height
                self.tileSurface.blit(word_surface, (word_x, word_y))
                word_x += word_width + fonts["shop_tile_text"].size(' ')[0]
            word_x = 15
            word_y += word_height
        screen.blit(self.tileSurface, self.tileRect)
        self.buy_button.process()
        if bought_upgrades[self.upgrade_name][0] < bought_upgrades[self.upgrade_name][1]:
            self.buy_button.active = True
            self.buy_button.buttonText = str((bought_upgrades[self.upgrade_name][0] + 1)
                                             * bought_upgrades[self.upgrade_name][3])
        else:
            self.buy_button.active = False
            self.buy_button.buttonText = '---'


class UpgradeTile:
    def __init__(self, width, height, upgrade_name="Tile"):
        self.width = width
        self.height = height
        self.upgrade_name = upgrade_name
        self.tileSurface = pygame.transform.scale(pygame.image.load("graphics/tile.png").convert_alpha(),
                                                  (self.width, self.height))
        self.tileRect = pygame.Rect(0, 0, self.width, self.height)
        self.tileName = fonts["upgrade_tile_name"].render(upgrade_name, True, (255, 255, 255))

    def process(self, x, y):
        self.tileRect.center = (x, y)
        take_button = Button(self.tileRect.centerx, self.tileRect.bottom - 45, 150, 60,
                                  "Take", take_upgrade, [self.upgrade_name], False if block_button else True)
        self.tileSurface.blit(self.tileName, [self.tileRect.width / 2 - self.tileName.get_rect().width / 2, 20])
        word_x, word_y = 15, 75
        word_height = 0
        for lines in [word.split(' ') for word in taken_upgrades[self.upgrade_name][1].splitlines()]:
            for words in lines:
                word_surface = fonts["upgrade_tile_text"].render(words, True, (255, 255, 255))
                word_width, word_height = word_surface.get_size()
                if word_x + word_width >= self.width - 5:
                    word_x = 15
                    word_y += word_height
                self.tileSurface.blit(word_surface, (word_x, word_y))
                word_x += word_width + fonts["upgrade_tile_text"].size(' ')[0]
            word_x = 15
            word_y += word_height
        screen.blit(self.tileSurface, self.tileRect)
        take_button.process()


class Drop(pygame.sprite.Sprite):
    def __init__(self, x, y, drop_type, value):
        super().__init__()
        self.value = value
        self.type = drop_type
        scale = 1.0 + value / 200
        if self.type == 'exp':
            self.image = pygame.image.load("graphics/exp.png").convert_alpha()
        elif self.type == 'money':
            self.image = pygame.image.load("graphics/money.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.image, scale)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move_to_player(self):
        dx, dy = player.sprite.rect.centerx - self.rect.centerx, player.sprite.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist:
            dx, dy = dx / dist, dy / dist
            self.rect.x += dx * 5
            self.rect.y += dy * 5

    def update(self):
        self.move_to_player()


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, bullet_damage, bullet_speed, bullet_range):
        super().__init__()
        self.damage = bullet_damage
        self.range = bullet_range
        self.traveled = 0
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.x = player.sprite.rect.x
        self.y = player.sprite.rect.y
        angle = math.atan2(self.y - mouse_y, self.x - mouse_x)
        self.x_vel = math.cos(angle) * bullet_speed
        self.y_vel = math.sin(angle) * bullet_speed
        self.distance = math.hypot(self.x_vel, self.y_vel)
        self.image = pygame.transform.rotate(pygame.image.load("graphics/bullet.png").convert_alpha(), -math.degrees(angle % (2 * math.pi)))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def move(self):
        self.rect.x -= self.x_vel
        self.rect.y -= self.y_vel
        self.traveled += self.distance
        if self.traveled >= self.range:
            self.kill()

    def check_outside(self):
        if self.rect.left > screen.get_width() or self.rect.right < 0:
            self.kill()
        if self.rect.top > screen.get_height() or self.rect.bottom < 0:
            self.kill()

    def update(self):
        self.move()
        self.check_outside()


class Player(pygame.sprite.Sprite):
    def __init__(self, base_stats):
        super().__init__()
        self.base_stats = base_stats
        self.curr_stats = {}
        for i in base_stats:
            if i == "Health":
                self.curr_stats[i] = self.base_stats[i] + bought_upgrades[i][0] * bought_upgrades[i][4]
            else:
                self.curr_stats[i] = round(self.base_stats[i] + self.base_stats[i]
                                           * bought_upgrades[i][0] * bought_upgrades[i][4], 2)
        self.health = self.curr_stats["Health"]
        self.level = 1
        self.max_exp = 10
        self.exp = 0
        self.money = 0
        self.damage_cooldown = 30
        self.shoot_cooldown_tracker = 10
        self.damage_cooldown_tracker = 0
        self.walking_direction = "down"
        self.facing_direction = "down"
        self.walking_animation_down = [pygame.image.load("graphics/player_walk_down_0.png"),
                                       pygame.image.load("graphics/player_walk_down_1.png"),
                                       pygame.image.load("graphics/player_walk_down_2.png"),
                                       pygame.image.load("graphics/player_walk_down_3.png")]
        self.walking_animation_right = [pygame.image.load("graphics/player_walk_right_0.png"),
                                        pygame.image.load("graphics/player_walk_right_1.png"),
                                        pygame.image.load("graphics/player_walk_right_2.png"),
                                        pygame.image.load("graphics/player_walk_right_3.png")]
        self.walking_animation_up = [pygame.image.load("graphics/player_walk_up_0.png"),
                                     pygame.image.load("graphics/player_walk_up_1.png"),
                                     pygame.image.load("graphics/player_walk_up_2.png"),
                                     pygame.image.load("graphics/player_walk_up_3.png")]
        for i in range(4):
            self.walking_animation_right[i] = pygame.transform.scale_by(self.walking_animation_right[i], 1.5)
            self.walking_animation_down[i] = pygame.transform.scale_by(self.walking_animation_down[i], 1.5)
            self.walking_animation_up[i] = pygame.transform.scale_by(self.walking_animation_up[i], 1.5)
        self.player_weapon = pygame.image.load("graphics/weapon.png").convert_alpha()
        self.rect = self.walking_animation_right[0].get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
        self.image = self.walking_animation_down[0]
        self.animation_count = 0

    def show_stats(self):
        width = 200
        height = 40

        # Health bar
        pygame.draw.rect(screen, (0, 0, 0), (10, 10, width + 10, height + 10), 5)
        health_bar = pygame.draw.rect(screen, (128, 128, 128), (15, 15, width, height))
        pygame.draw.rect(screen, (255, 0, 0), (15, 15, width * self.health / self.curr_stats["Health"], height))
        health_text = fonts["progress_bar"].render(str(self.health) + " / " + str(self.curr_stats["Health"]), True, (0, 0, 0))
        health_text_rect = health_text.get_rect(center=health_bar.center)
        screen.blit(health_text, health_text_rect)

        # Experience Bar
        pygame.draw.rect(screen, (0, 0, 0), (10, height + 25, width + 10, height + 10), 5)
        exp_bar = pygame.draw.rect(screen, (128, 128, 128), (15, height + 30, width, height))
        green_bar = self.exp if self.max_exp >= self.exp else self.max_exp
        pygame.draw.rect(screen, (0, 255, 0), (15, height + 30, width * green_bar / self.max_exp, height))
        exp_text = fonts["progress_bar"].render("Lv: " + str(self.level), True, (0, 0, 0))
        exp_text_rect = exp_text.get_rect(center=exp_bar.center)
        screen.blit(exp_text, exp_text_rect)

        money_text = fonts["in_game_money"].render("Money: " + str(self.money), True, 'white')
        money_rect = money_text.get_rect(topleft=(10, exp_bar.bottom + 20))
        screen.blit(money_text, money_rect)

    def handle_weapon(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.rect.centerx, mouse_y - self.rect.centery
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        if mouse_x < self.rect.centerx:
            player_weapon_copy = pygame.transform.flip(self.player_weapon, False, True)
        else:
            player_weapon_copy = self.player_weapon
        player_weapon_copy = pygame.transform.rotate(player_weapon_copy, angle)
        screen.blit(player_weapon_copy, (self.rect.centerx - int(player_weapon_copy.get_width() / 2),
                                         self.rect.centery + 5 - int(player_weapon_copy.get_height() / 2)))

    def walking(self):
        if self.animation_count + 1 < 16:
            self.animation_count += 1
        else:
            self.animation_count = 0
        if self.walking_direction == 'right':
            self.image = self.walking_animation_right[self.animation_count // 4].copy()
            self.walking_direction = ''
        elif self.walking_direction == 'left':
            self.image = pygame.transform.flip(self.walking_animation_right[self.animation_count // 4].copy(), True, False)
            self.walking_direction = ''
        elif self.walking_direction == 'down':
            self.image = self.walking_animation_down[self.animation_count // 4].copy()
            self.walking_direction = ''
        elif self.walking_direction == 'up':
            self.image = self.walking_animation_up[self.animation_count // 4].copy()
            self.walking_direction = ''

        elif self.facing_direction == 'right':
            self.image = self.walking_animation_right[0].copy()
        elif self.facing_direction == 'left':
            self.image = pygame.transform.flip(self.walking_animation_right[0].copy(), True, False)
        elif self.facing_direction == 'down':
            self.image = self.walking_animation_down[0].copy()
        elif self.facing_direction == 'up':
            self.image = self.walking_animation_up[0].copy()
        else:
            self.image = self.walking_animation_down[0].copy()

        if self.damage_cooldown_tracker:
            self.image.fill((100, 0, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.rect.top > 0:
                self.rect.top -= self.curr_stats["Movement speed"]
                self.walking_direction = 'up'
                self.facing_direction = 'up'
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if self.rect.bottom < screen.get_height():
                self.walking_direction = 'down'
                self.facing_direction = 'down'
                self.rect.bottom += self.curr_stats["Movement speed"]
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.rect.right < screen.get_width():
                self.walking_direction = 'right'
                self.facing_direction = 'right'
                self.rect.right += self.curr_stats["Movement speed"]
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.rect.left > 0:
                self.walking_direction = 'left'
                self.facing_direction = 'left'
                self.rect.left -= self.curr_stats["Movement speed"]
        if pygame.mouse.get_pressed()[0] and not self.shoot_cooldown_tracker:
            self.shoot()

    def shoot(self):
        pygame.mixer.Sound.play(shoot_sound)
        bullets.add(PlayerBullet(self.curr_stats["Bullet damage"], self.curr_stats["Bullet speed"],
                                 self.curr_stats["Bullet range"]))
        self.shoot_cooldown_tracker = self.curr_stats["Fire rate"]

    def check_hit(self):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect) and enemy.alive and not self.damage_cooldown_tracker:
                pygame.mixer.Sound.play(player_got_hit_sound)
                self.damage_cooldown_tracker = self.damage_cooldown
                self.health -= 1
        if self.health <= 0:
            pygame.mixer.Sound.play(game_over_sound)
            player_died(self.money)

    def check_drop(self):
        for drop in drops:
            if math.hypot(self.rect.x - drop.rect.x, self.rect.y - drop.rect.y) <= self.curr_stats["Pickup range"]:
                drop.update()
            if self.rect.colliderect(drop.rect):
                if drop.type == 'exp':
                    pygame.mixer.Sound.play(pick_up_sound)
                    self.exp += drop.value
                elif drop.type == 'money':
                    pygame.mixer.Sound.play(pick_up_money_sound)
                    self.money += drop.value
                drop.kill()

    def check_level_up(self):
        if self.exp >= self.max_exp:
            pygame.mixer.Sound.play(level_up_sound)
            self.exp -= self.max_exp
            self.level += 1
            self.max_exp = self.level * 10
            if self.health < self.curr_stats["Health"]:
                self.health += 1
            player_level_up()

    def update_trackers(self):
        if self.shoot_cooldown_tracker < 1:
            self.shoot_cooldown_tracker = 0
        elif self.shoot_cooldown_tracker:
            self.shoot_cooldown_tracker -= 1
        if self.damage_cooldown_tracker:
            self.damage_cooldown_tracker -= 1

    def update(self):
        self.update_trackers()
        self.player_input()
        self.walking()
        self.handle_weapon()
        self.check_hit()
        self.check_drop()
        self.check_level_up()
        self.show_stats()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, stats):
        super().__init__()
        self.type = stats['enemy_type']
        self.health = stats['health']
        self.speed = stats['speed']
        self.value = stats['value']
        self.boss = stats['boss']
        self.alive = True
        self.alpha = 100
        self.got_hit = 0
        self.walking_animation = [pygame.image.load("graphics/" + self.type + "_0.png"),
                                  pygame.image.load("graphics/" + self.type + "_1.png"),
                                  pygame.image.load("graphics/" + self.type + "_2.png"),
                                  pygame.image.load("graphics/" + self.type + "_3.png")]
        if self.boss:
            for i in range(4):
                self.walking_animation[i] = pygame.transform.scale_by(self.walking_animation[i], 1.5)
        for i in range(4):
            self.walking_animation[i].fill(stats['color'], special_flags=pygame.BLEND_RGBA_ADD)
        self.image = self.walking_animation[0]
        self.animation_count = 0
        if randint(0, 2):
            self.rect = self.image.get_rect(
                center=(random.choice([-50, screen.get_width() + 50]), randint(0, screen.get_height())))
        else:
            self.rect = self.image.get_rect(
                center=(randint(0, screen.get_width()), random.choice([-50, screen.get_height() + 50])))

    def move_toward_player(self):
        if self.animation_count + 1 < 32:
            self.animation_count += 1
        else:
            self.animation_count = 0
        dx, dy = player.sprite.rect.centerx - self.rect.centerx, player.sprite.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx, dy = dx / dist, dy / dist
            self.rect.x += round(dx * self.speed)
            self.rect.y += round(dy * self.speed)
        if dx >= 0:
            self.image = self.walking_animation[self.animation_count // 8].copy()
        else:
            self.image = pygame.transform.flip(self.walking_animation[self.animation_count // 8].copy(), True, False)
        if self.got_hit > 0:
            self.image.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def prevent_overlap(self):
        for enemy in enemies:
            if self != enemy and enemy.alive:
                if self.rect.colliderect(enemy.rect) and self.speed <= enemy.speed:
                    dx, dy = enemy.rect.centerx - self.rect.centerx, enemy.rect.centery - self.rect.centery
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        dx, dy = dx / dist, dy / dist
                        self.rect.x -= round(dx)
                        self.rect.y -= round(dy)

    def check_hit(self):
        for bullet in bullets:
            if self.rect.colliderect(bullet.rect):
                pygame.mixer.Sound.play(enemy_got_hit_sound)
                bullet.kill()
                self.health -= bullet.damage
                self.got_hit = 4
        if self.health <= 0:
            drops.add(Drop(self.rect.x + randint(0, self.rect.width), self.rect.y + randint(0, self.rect.height),
                           'exp', self.value))
            if randint(0, 99) < 5 or self.boss:
                drops.add(Drop(self.rect.x + randint(0, self.rect.width), self.rect.y + randint(0, self.rect.height),
                               'money', randint(math.ceil(self.value / 2), self.value * 2)))
            self.alive = False

    def update_tracers(self):
        if self.got_hit > 0:
            self.got_hit -= 1

    def im_dying_help_me(self):
        self.alpha -= 5
        if self.alpha < 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)

    def update(self):
        if self.alive:
            self.move_toward_player()
            self.prevent_overlap()
            self.check_hit()
            self.update_tracers()
        else:
            self.im_dying_help_me()


pygame.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption('Computer survivors')
clock = pygame.time.Clock()

click_sound = pygame.mixer.Sound("audio/click.wav")
click_sound.set_volume(0.2)
enemy_got_hit_sound = pygame.mixer.Sound("audio/enemy_got_hit.wav")
enemy_got_hit_sound.set_volume(0.05)
game_over_sound = pygame.mixer.Sound("audio/game_over.wav")
game_over_sound.set_volume(0.5)
level_up_sound = pygame.mixer.Sound("audio/level_up.wav")
level_up_sound.set_volume(0.3)
pick_up_sound = pygame.mixer.Sound("audio/pick_up.wav")
pick_up_sound.set_volume(0.05)
pick_up_money_sound = pygame.mixer.Sound("audio/pick_up_money.wav")
pick_up_money_sound.set_volume(0.2)
player_got_hit_sound = pygame.mixer.Sound("audio/player_got_hit.wav")
player_got_hit_sound.set_volume(0.25)
shoot_sound = pygame.mixer.Sound("audio/shoot.wav")
shoot_sound.set_volume(0.03)

music = {
    "main_menu": {
        "name": "audio/main_menu_music.ogg",
        "volume": 0.1
    },
    "game_background": {
        "name": "audio/game_background_music.ogg",
        "volume": 0.05
    },
    "game_over": {
        "name": "audio/game_over_music.ogg",
        "volume": 0.1
    },
}


game_background = pygame.image.load('graphics/game_background.jpg').convert()
main_menu_background = pygame.image.load('graphics/main_menu_background.jpg').convert()
shop_background = pygame.image.load('graphics/shop_background.jpg').convert()
death_background = pygame.image.load('graphics/death_background.jpg').convert()

fonts = {
    "button": pygame.font.Font("Retro Gaming.ttf", 35),
    "shop_button": pygame.font.Font("Paskowy.ttf", 45),
    "shop_tile_name": pygame.font.Font("Retro Gaming.ttf", 25),
    "shop_tile_text": pygame.font.Font("Retro Gaming.ttf", 20),
    "upgrade_tile_name": pygame.font.Font("Retro Gaming.ttf", 25),
    "upgrade_tile_text": pygame.font.Font("Retro Gaming.ttf", 20),
    "progress_bar": pygame.font.Font("Retro Gaming.ttf", 30),
    "in_game_money": pygame.font.Font("Retro Gaming.ttf", 25),
    "pause_menu_player_stats": pygame.font.Font("Retro Gaming.ttf", 25)
}


global_money = 0
bought_upgrades = {
    "Bullet damage": [0, 20, "Increases bullet damage by 5% per level", 300, 0.05],
    "Fire rate": [0, 5, "Increases rate of fire cooldown by 5% per level", 1000, -0.05],
    "Bullet speed": [0, 5, "Increases bullet speed by 10% per level", 200, 0.05],
    "Bullet range": [0, 10, "Increases bullet range by 5% per level", 350, 0.05],
    "Health": [0, 7, "Increases health by 1 per level", 3000, 1],
    "Movement speed": [0, 2, "Increases movement speed by 1 per level", 5000, 1],
    "Pickup range": [0, 10, "Increases pickup range by 10% per level", 250, 0.1]
}

if os.path.exists("data.txt"):
    file_read = open("data.txt", 'r')
    global_money = int(file_read.readline())
    for upgrade in bought_upgrades:
        bought_upgrades[upgrade][0] = int(file_read.readline())
        if bought_upgrades[upgrade][0] > bought_upgrades[upgrade][1]:
            bought_upgrades[upgrade][0] = bought_upgrades[upgrade][1]
        elif bought_upgrades[upgrade][0] < 0:
            bought_upgrades[upgrade][0] = 0
    file_read.close()

taken_upgrades = {
    "Bullet damage": [0, "Increases base bullet damage by 1 per level", 1],
    "Fire rate": [0, "Increases base rate of fire cooldown by 1 per level", -2],
    "Bullet speed": [0, "Increases base bullet speed by 1 per level", 1],
    "Bullet range": [0, "Increases base bullet range by 25 per level", 25],
    "Health": [0, "Increases health by 1 per level", 1],
    "Pickup range": [0, "Increases base pickup range by 25 per level", 25]
}

player = pygame.sprite.GroupSingle()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
drops = pygame.sprite.Group()

with open('player.json') as json_file:
    player_stats = json.load(json_file)

with open('enemies.json') as json_file:
    enemy_stats = json.load(json_file)

block_button = 0

with open('buttons.json') as json_file:
    buttons = json.load(json_file)
"""buttons = {
    "start_game": Button(screen.get_width() / 2, screen.get_height() / 2 + 50, 300, 100, "Start", start_game),
    "open_shop": Button(screen.get_width() / 2, screen.get_height() / 2 + 175, 300, 100, "Upgrades", open_shop),
    "close_up": Button(screen.get_width() / 2, screen.get_height() / 2 + 300, 300, 100, "Exit", close_app),
    "close_shop": Button(screen.get_width() / 2, screen.get_height() / 2 + 400, 300, 100, "Return", close_shop),
    "unpause_game": Button(screen.get_width() / 2, screen.get_height() / 2 + 50, 250, 100, "Resume", unpause_game),
    "end_game": Button(screen.get_width() / 2, screen.get_height() / 2 + 175, 250, 100, "End", end_game),
    "death_screen": Button(screen.get_width() / 2, screen.get_height() / 2, 250, 100, "Menu", end_game)
}"""

shop_tiles = []
generate_shop_tiles()
upgrade_tiles = []
generate_upgrade_tiles()

clock_timer = pygame.USEREVENT + 1
pygame.time.set_timer(clock_timer, 1000)

spawn_timer = pygame.USEREVENT + 2
pygame.time.set_timer(spawn_timer, 500)

minutes, seconds = 0, 0
game_active, game_pause, upgrade_shop, death_screen, level_up = False, False, False, False, False
max_enemies = 0

option1, option2, option3 = 0, 0, 0
choose_options = True

fading = True
fading_in = False
fade_out_to = main_menu
fading_alpha = 100
alphaSurface = pygame.surface.Surface((screen.get_width(), screen.get_height()))
alphaSurface.fill((0, 0, 0))
alphaSurface.set_alpha(fading_alpha)

play_music(music["main_menu"], 3)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            close_app()
        if game_active:
            if game_pause:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    unpause_game()
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not fading:
                    pause_game()
                if event.type == clock_timer:
                    seconds += 1
                if event.type == spawn_timer and len(enemies) < max_enemies:
                    spawn_enemy()
    if fading:
        fading_effect()
    elif game_active:
        if death_screen:
            death_screen_menu()
        elif game_pause:
            pause_menu()
        elif level_up:
            level_up_menu()
        else:
            game_update()
    elif upgrade_shop:
        shop()
    else:
        main_menu()
    pygame.display.update()
    clock.tick(60)
