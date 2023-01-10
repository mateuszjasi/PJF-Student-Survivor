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


def play_sound(name):
    sound = pygame.mixer.Sound(sounds[name]["name"])
    sound.set_volume(sounds[name]["volume"])
    pygame.mixer.Sound.play(sound)


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
    file = open("save.txt", "w")
    file.write(str(global_money) + '\n')
    for i in bought_upgrades:
        file.write(str(bought_upgrades[i][0]) + '\n')
    file.close()
    pygame.quit()
    exit()


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


def show_player_stats():
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
        player_stats_label_text_rect = player_stats_label_text.get_rect(
            topleft=(20, 35 + player_stats_label_text.get_height() * (x + 1)))
        player_stats_surface.blit(player_stats_label_text, player_stats_label_text_rect)

    screen.blit(player_stats_surface, player_stats_rect)


def show_run_results(player_money, player_level):
    run_results_rect = pygame.rect.Rect(0, 0, 375, 250)
    run_results_rect.midtop = (screen.get_width() / 2, 50)

    run_results_text = "Run results: "
    run_results_label_text = fonts["progress_bar"].render(run_results_text, True, 'white')
    run_results_surface = pygame.transform.scale(pygame.image.load("graphics/tile.png").convert_alpha(),
                                                  (run_results_rect.width, run_results_rect.height))
    run_results_text_rect = run_results_label_text.get_rect(topleft=(20, 25))
    run_results_surface.blit(run_results_label_text, run_results_text_rect)

    for i in range(1, 6):
        if i == 1:
            run_results_text = "Survived: " + "{:02}:{:02}".format(minutes, seconds)
        elif i == 2:
            run_results_text = "Level reached: " + str(player_level)
        elif i == 3:
            run_results_text = "Enemies killed: " + str(kill_count)
        elif i == 4:
            run_results_text = "Money gained: " + str(player_money)
        elif i == 5:
            run_results_text = "Better luck next time" if minutes < 10 else "Death was here"
        run_results_label_text = fonts["pause_menu_player_stats"].render(
            run_results_text, True, 'black' if i == 5 and minutes >= 10 else 'white')
        run_results_text_rect = run_results_label_text.get_rect(topleft=(20, 35 + i * run_results_label_text.get_height()))
        run_results_surface.blit(run_results_label_text, run_results_text_rect)

    screen.blit(run_results_surface, run_results_rect)


def show_grave(xy):
    grave = pygame.image.load("graphics/grave.png")
    grave_rect = grave.get_rect(center=xy)
    screen.blit(grave, grave_rect)


def player_level_up():
    global block_button, level_up
    block_button = 60
    level_up = True


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


def player_died(player_money, player_level, xy):
    global death_screen, global_money
    death_screen = True
    global_money += player_money
    play_music(music["game_over"])
    screen.blit(backgrounds["death_screen"], (0, 0))
    show_grave(xy)
    show_player_stats()
    show_run_results(player_money, player_level)


def end_game():
    global game_active, game_pause, death_screen
    enemies.empty()
    bullets.empty()
    drops.empty()
    player.remove()
    game_active, game_pause, death_screen = False, False, False
    play_music(music["main_menu"], 3)
    fade_to(main_menu)


def main_menu():
    screen.blit(backgrounds["main_menu"], (0, 0))
    buttons["start_game"].process()
    buttons["open_shop"].process()
    buttons["close_up"].process()
    title_text = fonts["main_menu_title"].render("College", True, (200, 0, 0))
    title_rect = title_text.get_rect(midtop=(screen.get_width() / 2, 100))
    screen.blit(title_text, title_rect)
    title_text = fonts["main_menu_title"].render("Survivors", True, (200, 0, 0))
    title_rect = title_text.get_rect(midtop=(screen.get_width() / 2, 50 + title_text.get_height()))
    screen.blit(title_text, title_rect)


def shop():
    screen.blit(backgrounds["shop"], (0, 0))
    for tile in range(0, len(shop_tiles)):
        shop_tiles[tile].process()
    buttons["close_shop"].process()
    money_text = fonts["in_game_money"].render("Money: " + str(global_money), True, (255, 255, 255))
    money_rect = money_text.get_rect(bottomleft=(10, screen.get_height() - 10))
    screen.blit(money_text, money_rect)


def pause_menu():
    buttons["unpause_game"].process()
    buttons["end_game"].process()


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
    buttons["death_screen"].process()


def game_update():
    screen.blit(backgrounds["game"], (0, 0))
    drops.draw(screen)
    enemies.draw(screen)
    enemies.update()
    bullets.draw(screen)
    bullets.update()
    clock_update()
    player.draw(screen)
    player.update()


def start_game():
    global game_active, max_enemies, kill_count, minutes, seconds
    max_enemies = 20
    kill_count = 0
    minutes, seconds = 0, 0
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
    show_player_stats()
    pygame.mixer.music.pause()


def unpause_game():
    global game_pause
    game_pause = False
    pygame.mixer.music.unpause()


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
                        play_sound("click")
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
        play_sound("shoot")
        bullets.add(PlayerBullet(self.curr_stats["Bullet damage"], self.curr_stats["Bullet speed"],
                                 self.curr_stats["Bullet range"]))
        self.shoot_cooldown_tracker = self.curr_stats["Fire rate"]

    def check_hit(self):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect) and enemy.alive and not self.damage_cooldown_tracker:
                play_sound("player_got_hit")
                self.damage_cooldown_tracker = self.damage_cooldown
                self.health -= 1
        if self.health <= 0:
            play_sound("game_over")
            player_died(self.money, self.level, (self.rect.centerx, self.rect.centery))

    def check_drop(self):
        for drop in drops:
            if math.hypot(self.rect.x - drop.rect.x, self.rect.y - drop.rect.y) <= self.curr_stats["Pickup range"]:
                drop.update()
            if self.rect.colliderect(drop.rect):
                if drop.type == 'exp':
                    play_sound("pick_up")
                    self.exp += drop.value
                elif drop.type == 'money':
                    play_sound("pick_up_money")
                    self.money += drop.value
                drop.kill()

    def check_level_up(self):
        if self.exp >= self.max_exp:
            play_sound("level_up")
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
        self.check_drop()
        self.check_level_up()
        self.show_stats()
        self.check_hit()


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
                play_sound("enemy_got_hit")
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
            global kill_count
            kill_count += 1

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
pygame.display.set_caption('College Survivors')
clock = pygame.time.Clock()

player = pygame.sprite.GroupSingle()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
drops = pygame.sprite.Group()

minutes, seconds = 0, 0
game_active, game_pause, upgrade_shop, death_screen, level_up = False, False, False, False, False
max_enemies = 0
kill_count, global_money = 0, 0
block_button = 0
option1, option2, option3 = 0, 0, 0
choose_options = True

fading, fading_in = True, False
fade_out_to = main_menu
fading_alpha = 100
alphaSurface = pygame.surface.Surface((screen.get_width(), screen.get_height()))
alphaSurface.fill((0, 0, 0))
alphaSurface.set_alpha(fading_alpha)

buttons = {
    "start_game": Button(screen.get_width() / 2, screen.get_height() / 2 + 50, 300, 100, "Start", start_game),
    "open_shop": Button(screen.get_width() / 2, screen.get_height() / 2 + 175, 300, 100, "Upgrades", open_shop),
    "close_up": Button(screen.get_width() / 2, screen.get_height() / 2 + 300, 300, 100, "Exit", close_app),
    "close_shop": Button(screen.get_width() / 2, screen.get_height() / 2 + 400, 300, 100, "Return", close_shop),
    "unpause_game": Button(screen.get_width() / 2, screen.get_height() / 2 + 50, 250, 100, "Resume", unpause_game),
    "end_game": Button(screen.get_width() / 2, screen.get_height() / 2 + 175, 250, 100, "End", end_game),
    "death_screen": Button(screen.get_width() / 2, screen.get_height() / 2, 250, 100, "Menu", end_game)
}

with open('json/taken_upgrades.json') as json_file:
    taken_upgrades = json.load(json_file)
with open('json/player.json') as json_file:
    player_stats = json.load(json_file)
with open('json/enemies.json') as json_file:
    enemy_stats = json.load(json_file)
with open('json/music.json') as json_file:
    music = json.load(json_file)
with open('json/sounds.json') as json_file:
    sounds = json.load(json_file)
with open('json/backgrounds.json') as json_file:
    backgrounds = json.load(json_file)
for temp in backgrounds:
    backgrounds[temp] = pygame.image.load(backgrounds[temp]).convert()
with open('json/fonts.json') as json_file:
    fonts = json.load(json_file)
for temp in fonts:
    fonts[temp] = pygame.font.Font(fonts[temp][0], fonts[temp][1])
with open('json/bought_upgrades.json') as json_file:
    bought_upgrades = json.load(json_file)
if os.path.exists("save.txt"):
    file_read = open("save.txt", 'r')
    global_money = int(file_read.readline())
    for temp in bought_upgrades:
        bought_upgrades[temp][0] = int(file_read.readline())
        if bought_upgrades[temp][0] > bought_upgrades[temp][1]:
            bought_upgrades[temp][0] = bought_upgrades[temp][1]
        elif bought_upgrades[temp][0] < 0:
            bought_upgrades[temp][0] = 0
    file_read.close()

shop_tiles = []
generate_shop_tiles()
upgrade_tiles = []
generate_upgrade_tiles()

clock_timer = pygame.USEREVENT + 1
pygame.time.set_timer(clock_timer, 1000)

spawn_timer = pygame.USEREVENT + 2
pygame.time.set_timer(spawn_timer, 500)

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
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not fading and not level_up:
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
