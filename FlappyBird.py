import pygame
import os
import random

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','pipe.png')))
FLOOR_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','base.png')))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bg.png')))
BIRD_IMAGES =[
 pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird1.png'))),
 pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird2.png'))),
 pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird3.png'))),
]

pygame.font.init()
POINTS_SIZETEXT = pygame.font.SysFont('arial', 50)


class Bird:
    IMGS = BIRD_IMAGES
    # rotation animations
    MAXIMUM_ROTATION = 25
    ROTATION_SPEED = 20
    ANIMATION_TIMING = 5

    def __init__(self, x, y ):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.image_counting = 0
        self.image = self.IMGS[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        # calculate displacement
        self.time += 1
        displacement = 1.5 * (self.time**2) + self.speed * self.time

        # restringir o displacement
        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2

        self.y += displacement

        # angle  bird
        if displacement < 0 or self.y < (self.height +50):
            if self.angle < self.MAXIMUM_ROTATION:
                self.angle = self.MAXIMUM_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_SPEED

    def draw(self, screen):
        # defining image of the bird
        self.image_counting += 1

        if self.image_counting < self.ANIMATION_TIMING:
            self.image = self.IMGS[0]
        elif self.image_counting < self.ANIMATION_TIMING*2:
            self.image = self.IMGS[1]
        elif self.image_counting < self.ANIMATION_TIMING*3:
            self.image = self.IMGS[2]
        elif self.image_counting < self.ANIMATION_TIMING*4:
            self.image = self.IMGS[1]
        elif self.image_counting < self.ANIMATION_TIMING * 4 + 1:
            self.image = self.IMGS[0]
            self.image_counting = 0


        #if bird is falling do not flap
        if self.angle <= -80:
            self.image = self.IMGS[1]
            self.image_counting = self.ANIMATION_TIMING*2

        # draw image
        rotate_image = pygame.transform.rotate(self.image, self.angle)
        image_center_position = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotate_image.get_rect(center=image_center_position)
        screen.blit(rotate_image, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 320
    SPEED = 5
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_position = 0
        self.base_position = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BASE = PIPE_IMAGE
        self.passed = False
        self.def_height()

    def def_height(self):
        self.height = random.randrange(50,450)
        self.top_position = self.height - self.PIPE_TOP.get_height()
        self.base_position = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    def draw(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.top_position))
        screen.blit(self.PIPE_BASE, (self.x, self.base_position))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        mask_top = pygame.mask.from_surface(self.PIPE_TOP)
        mask_base = pygame.mask.from_surface(self.PIPE_BASE)

        distance_top = (self.x -bird.x, self.top_position - round(bird.y))
        distance_base = (self.x -bird.x, self.base_position - round(bird.y))

        point_top = bird_mask.overlap(mask_top, distance_top)
        point_base = bird_mask.overlap(mask_base, distance_base)

        if point_base or point_top:
            return True
        else:
            return False

class Floor:
    SPEED = 5
    WIDTH = FLOOR_IMAGE.get_width()
    IMAGE = FLOOR_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def __init_subclass__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = SCREEN_WIDTH

    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x1, self.y))
        screen.blit(self.IMAGE, (self.x2, self.y))

def draw_screen(screen, birds, pipes, floor, points):
    screen.blit(BACKGROUND_IMAGE, (0,0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)

    text = POINTS_SIZETEXT.render(f"Score: {points}", 1, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
    floor.draw(screen)
    pygame.display.update()


def main():
    birds = [Bird(230,350)]
    floor = Floor(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    points = 0
    watch = pygame.time.Clock()

    running = True
    while running:
        watch.tick(30)

        #interacting with user
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()

        # moving things
        for bird in birds:
            bird.move()
        floor.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i,bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipes.append(pipe)

        if add_pipe:
            points += 1
            pipes.append(Pipe(600))
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i,bird in enumerate(birds):
            if(bird.y + bird.image.get_height()) > floor.y or bird.y <0:
                birds.pop(i)


        draw_screen(screen, birds, pipes, floor, points)


if __name__ == '__main__':
    main()
