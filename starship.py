import random
import time
import math
import threading
import arcade

SCREEN_WIDTH = 600
SCREEN_HEHGHT = 600

class Starship(arcade.Sprite):
    def __init__(self):
        super().__init__(":resources:images/space_shooter/playerShip1_blue.png")
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = 32
        self.width = 48
        self.height = 48
        self.angle = 0
        self.change_angle = 0
        self.speed = 20
        self.bullet_list = []
        self.score = 0
        self.heart = 3
        self.heart_image = arcade.load_texture("heart.png")
        self.fire_sound = arcade.load_sound(":resources:sounds/hit2.wav")

    def fire(self):
        self.bullet_list.append(Bullet(self))
        arcade.play_sound(self.fire_sound)

    def move(self, direction):
        if direction == "L":
            self.center_x -= self.speed
        else:
            self.center_x += self.speed
    
    def turn(self, direction):
        if direction == "L":
            self.angle += self.speed
        else:
            self.angle -= self.speed

class Enemy(arcade.Sprite):
    def __init__(self):
        super().__init__(":resources:images/space_shooter/playerShip1_orange.png ")
        self.center_x = random.randint(10, SCREEN_WIDTH-10)
        self.center_y = SCREEN_HEHGHT + 24
        self.width = 48
        self.height = 48
        self.speed = 4
        self.angle = 180
        self.bullet_list = []

    def move(self):
        self.center_y -= self.speed

class Bullet(arcade.Sprite):
    def __init__(self, host):
        super().__init__(":resources:images/space_shooter/laserRed01.png")
        self.center_x = host.center_x
        self.center_y = host.center_y
        self.speed = 10
        self.angle = host.angle

    def move(self):
        a = math.radians(self.angle)
        self.center_x -= self.speed * math.sin(a)
        self.center_y += self.speed * math.cos(a)

class Explosion(arcade.Sprite):
    def __init__(self, x, y, st):
        super().__init__("explosion.png")
        self.width = 58
        self.height = 58
        self.center_x = x
        self.center_y = y
        self.show_time = 5
        self.start_time = st

class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEHGHT, "Interstelar Game")
        arcade.set_background_color(arcade.color.DARK_BLUE)
        self.background_image = arcade.load_texture(":resources:images/backgrounds/stars.png")
        self.gameover_image = arcade.load_texture("gameover.jpg")
        self.me = Starship()
        self.enemy_list = []
        self.difficulty = 0.15
        self.game_status = True
        self.destroy_sound = arcade.load_sound(":resources:sounds/gameover4.wav")
        self.explosion_list = []
        self.explosion_flags = []
        self.my_thread = threading.Thread(target=self.add_enemy)
        self.my_thread.start()
        self.my_thread_is_stop = False

    def remove_explosion(self, explosion):
        time.sleep(5)
        self.explosion_flags.pop(self.explosion_list.index(explosion))
        self.explosion_list.pop(self.explosion_list.index(explosion))

    def add_enemy(self):
        while True:
            self.enemy_list.append(Enemy())
            for enemy in self.enemy_list:
                enemy.speed += self.difficulty
            self.difficulty += 0.2
            time.sleep(3)
            if self.my_thread_is_stop == True:
                break

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEHGHT, self.background_image)
        self.me.draw()
        for enemy in self.enemy_list:
            enemy.draw()
        for bullet in self.me.bullet_list:
            bullet.draw()
        arcade.draw_text(f"Score: {self.me.score}", 510, 20, arcade.color.LEMON, 14)
        for i in range(self.me.heart):
            arcade.draw_lrwh_rectangle_textured(30 * i, 10, 30, 30, self.me.heart_image)
        for ex in self.explosion_list:
            ex.draw()
        if self.game_status == False:
            arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEHGHT, self.gameover_image)
            self.my_thread_is_stop = True

    def on_update(self, delta_time: float):
        for enemy in self.enemy_list:
            enemy.move()
            if enemy.center_y < 0:
                self.enemy_list.remove(enemy)
                self.me.heart -= 1

        if self.me.heart < 1:
            self.game_status = False
            return

        for bullet in self.me.bullet_list:
            bullet.move()
            if bullet.center_y > SCREEN_HEHGHT or bullet.center_y < 0 or bullet.center_x > SCREEN_WIDTH or bullet.center_x < 0:
                self.me.bullet_list.remove(bullet)

        for enemy in self.enemy_list:
            for bullet in self.me.bullet_list:
                if arcade.check_for_collision(enemy, bullet):
                    arcade.play_sound(self.destroy_sound)
                    self.explosion_list.append(Explosion(enemy.center_x, enemy.center_y, time.time()))
                    self.explosion_flags.append(False)
                    self.me.bullet_list.remove(bullet)
                    self.enemy_list.remove(enemy)
                    self.me.score += 1

        for explosion in self.explosion_list:
            if  self.explosion_flags[self.explosion_list.index(explosion)] == False:
                self.explosion_thread = threading.Thread(target=self.remove_explosion, args=(explosion,))
                self.explosion_flags[self.explosion_list.index(explosion)] = True
                self.explosion_thread.start()
        
    def on_close(self):
        self.my_thread_is_stop = True
        print("Closing........................")
        return super().on_close()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.me.fire()
        if symbol == arcade.key.LEFT:
            self.me.turn("L")
        if symbol == arcade.key.RIGHT:
            self.me.turn("R")
        if symbol == 97: # left
            self.me.move("L")
        elif symbol == 100: #right
            self.me.move("R")

game = Game()
arcade.run()