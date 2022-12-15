import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("bg.png")))
STAT_FONT = pygame.font.SysFont("comic-sans", 25)

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0 #everytime we jump we set the tick_count to 0
        self.height = self.y 

    def move(self):
        self.tick_count += 1

        d = self.vel * self.tick_count + 1.5 * self.tick_count**2 #movement self.tick_count(is the time continues to go up as time moves ) based on this we check if we are going up(or when we reach maximum jump height check jump function) or down

        if d >= 16:  #when the speed at which the bird falls is at 16 we dont wanna go over that speed
            d = 16  #thus we automatically set it at 16 max speed (terminal velocity)

        if d < 0: #if we are moving upwards we will move up a little bit more
            d -= 2 #this sets your jump if u wanna jump highier decrease the number 
        
        self.y = self.y + d

        if d < 0 or self.y < self.height + 50: #condition to check if the flappy bird is going up else
            if self.tilt < self.MAX_ROTATION:  
                self.tilt = self.MAX_ROTATION #tilt up
        else:    #sets the rotation down if you are falling 
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL #tilt down

    def draw(self,win): #win is the window we draw the bird into
        self.img_count += 1 #keeps track of how many tics we have displayed an image

        if self.img_count < self.ANIMATION_TIME: #this is how you rotate the images of self(bird)
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME *2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME *3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME *4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME *4 + 1: #does a full loop towards the first image index and sets img count to 0 
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80: #this checks if the tilt is at a certain point when you are falling this will prevent the bird img from looping so it looks like its falling
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME *2

        rotated_image = pygame.transform.rotate(self.img,self.tilt) #this code is how you rotate and image towards its center in pygame.
        new_rect = rotated_image.get_rect(center = self.img.get_rect( topleft = (self.x,self.y)).center)    
        win.blit( rotated_image , new_rect.topleft ) #blit means draw

    def get_mask(self): #this is how we get collisions for our objects
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200 #how much space inbetween our pipes(other pipe objects)
    VEL = 5  #this is how fast our pipe objects move to look like the bird is moving 

    def __init__(self, x):#the reason we set x only is so that the height or (y) of our pipes is random every time 
        self.x = x 
        self.height = 0

        self.top = 0
        self.top = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG,False,True) #stores the pipe image top
        self.PIPE_BOTTOM = PIPE_IMG #THIS FLIPS THE PIPE IMG AND STORES IT AT THE BOTTOM 

        self.passed = False #this checks if our bird already passed our pipe this helps collision
        self.set_height() #this function sets how tall the pipe is 

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height() #this figures out where the top of our pipe to be placed
        self.bottom = self.height + self.GAP

    def move(self): #change the X position based on the velocity the pipe moves each frame
        self.x -= self.VEL

    def draw(self,win):
        win.blit(self.PIPE_TOP,(self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self,bird):
        bird_mask = bird.get_mask() #mask is checking the pixels inside a box if they are touching the pixels in another box this method is better for picture perfect collision
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y)) #we cannot have decimals here so thats why we roundoff the y of the bird object
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset) #to check if the masks are overlapping if the dont this will return to us none
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point: # if collision occurs either top or bottom pipe hits the bird
            return True

        return False

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        if self.x1 <= -self.WIDTH:
            self.x1 = 0
            self.x2 = self.WIDTH

        self.x1 = self.x1 - self.VEL
        self.x2 = self.x2 - self.VEL

    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))

def draw_window(win,birds,pipes, base,score): #draws the window for our game 
    win.blit(BG_IMG,(0,0)) #draws the background image 

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: "+ str(score),1,(255,255,255,255))
    win.blit(text,(WIN_WIDTH - 10 - text.get_width(),10))

    base.draw(win)
    for bird in birds:
        bird.draw(win) #draws the bird over our window drawing

    pygame.display.update()#updates the display

def main (genomes,config):
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)
        

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT)) 
    run = True
    clock = pygame.time.Clock() #sets how fast the games framerate to set how fast our window is running 

    score = 0

    while run: #main animation loop
        clock.tick(30) #at most 30 ticks every sec
        for event in pygame.event.get(): #loops through all our events
            if event.type == pygame.QUIT: #if we click on the X on the top right corner it will end our pygame
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds)> 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        #bird.move() #calling of the movement function
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

            

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()
        
        if add_pipe:
            score+= 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win,birds,pipes,base,score) #drawfunction 


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config.txt")
    run(config_path)