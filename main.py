from re import T
import pygame, random, asyncio, time
import logging
from sys import exit
import boto3
# import botocore
# from botocore.exceptions import ClientError

logging.basicConfig(filename='game.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


AWS_ACCESS_KEY = "AKIAV3N7ULSXXGLBNPCR"
AWS_SECRET_KEY = "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"
AWS_S3_BUCKET_NAME = "pygame2"
AWS_REGION = "us-east-1"
LOCAL_FILE = "game.txt"

def upload_logs_to_s3():
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    response = s3_client.upload_file(LOCAL_FILE, AWS_S3_BUCKET_NAME, LOCAL_FILE)
    print(f'upload file response : {response}')


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        playerWalk0 = pygame.image.load('graphics/player/running0.png').convert_alpha()
        playerWalk1 = pygame.image.load('graphics/player/running1.png').convert_alpha()
        self.playerWalking = [playerWalk0, playerWalk1]
        self.playerIndex = 0
        self.playerJump = pygame.image.load('graphics/player/jump.png').convert_alpha()
        self.image = self.playerWalking[self.playerIndex]
        self.rect = self.image.get_rect(midbottom = (100, 200))
        self.gravity = 0
        self.jumpSound = pygame.mixer.Sound('audio/jump.ogg')
        self.jumpSound.set_volume(0.01)

    def playerInput(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.jumpSound.play()
            self.gravity = -20
    
    def applyGravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 305: self.rect.bottom = 305
    
    def animate(self):
        if self.rect.bottom < 305:
            self.image = self.playerJump
        else:
            self.playerIndex += 0.1
            if self.playerIndex >= len(self.playerWalking): self.playerIndex = 0
            self.image = self.playerWalking[int(self.playerIndex)]

    def update(self):
        self.playerInput()
        self.applyGravity()
        self.animate()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self,type):
        super().__init__()
        
        if type == 'flyer':
            flyerF0 = pygame.image.load('graphics/flyer/Flyer0.png').convert_alpha()
            flyerF1 = pygame.image.load('graphics/flyer/Flyer1.png').convert_alpha()
            self.frames = [flyerF0, flyerF1]
            yPos = 210
        else:
            slimerF0 = pygame.image.load('graphics/pooper/slimer0.png').convert_alpha()
            slimerF1 = pygame.image.load('graphics/pooper/slimer1.png').convert_alpha()
            self.frames = [slimerF0, slimerF1]
            yPos = 300
        self.animationIndex = 0
        self.image = self.frames[self.animationIndex]
        self.rect = self.image.get_rect(midbottom = (random.randint(600, 700), yPos))
    
    def animate(self):
        self.animationIndex += 0.1
        if self.animationIndex >= len(self.frames): self.animationIndex = 0
        self.image = self.frames[int(self.animationIndex)]
    
    def update(self):
        self.animate()
        self.rect.x -= 5
        self.destory()
    
    def destory(self):
        if self.rect.x <= -50:
            self.kill()

def displayScore():
    current_time = ((pygame.time.get_ticks()- startTime) / 1000)
    scoreSf = font.render(f'Score: {int(current_time)}', False, ('black'))
    scoreRect = scoreSf.get_rect(center=(320, 100))
    screen.blit(scoreSf, scoreRect)
    return current_time

def spriteCollisions(player, obstacleGroup):
    if pygame.sprite.spritecollide(player.sprite, obstacleGroup, False):
        obstacleGroup.empty()
        return False
    else: return True

def read_high_scores():
    try:
        with open('highscores', 'r') as file:
            high_scores = [int(score.strip()) for score in file.readlines()]
            return high_scores
    except FileNotFoundError:
        return []


def write_high_score(score):
    current_high_score = read_high_scores()
    if not current_high_score or score > max(current_high_score):
        with open('highscores', 'w') as file:
            file.write(str(score) + '\n')



def display_high_scores(screen, high_scores, font):
    max_score = max(high_scores) if high_scores else 0
    high_score_text = font.render(f"High Score: {max_score}", True, (255, 255, 255))
    high_score_rect = high_score_text.get_rect(center=(320, 50))
    screen.blit(high_score_text, high_score_rect)
    y = 150
    for score in high_scores:
        score_text = font.render(str(score), True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(320, y))
        screen.blit(score_text, score_rect)
        y += 50

def updateDifficulty(difficulty):
    if difficulty == 'easy':
        return 5, 1500
    elif difficulty == 'medium':
        return 7, 1000
    elif difficulty == 'hard':
        return 10, 800
    
def homePage(screen, clock):
    BUTTON_COLOR = (135, 206, 250) 
    BUTTON_HOVER_COLOR = (70, 130, 180)  

    background_color = (0, 0, 128) 

    button_width, button_height = 150, 40
    button_x, button_y = 10, 100
    button_spacing = 20

    buttons = {
    'start': pygame.Rect(220, 150, button_width, button_height),
    'high_scores': pygame.Rect(220, 210, button_width, button_height),
    'exit': pygame.Rect(220, 270, button_width, button_height),
    'music_toggle': pygame.Rect(440, 10, 200, 50),
    'easy': pygame.Rect(button_x, button_y, button_width, button_height),
    'medium': pygame.Rect(button_x, button_y + button_height + button_spacing, button_width, button_height),
    'hard': pygame.Rect(button_x, button_y + 2 * (button_height + button_spacing), button_width, button_height),
}



    pygame.mixer.music.load('audio/fa.ogg')
    pygame.mixer.music.play(-1)  

    font = pygame.font.Font(None, 36)

    music_on_text = font.render("Music: ON", True, (0, 0, 0))
    music_off_text = font.render("Music: OFF", True, (0, 0, 0))

    music_on = True

    show_high_scores = False

    high_score = read_high_scores()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if show_high_scores:  
                    if 245 <= mouse_pos[0] <= 395 and 150 <= mouse_pos[1] <= 190:
                        show_high_scores = False  
                else:
                    for button_name, button_rect in buttons.items():
                        if button_rect.collidepoint(mouse_pos):
                            if button_name == 'start':
                                print("Start game")
                                return
                            elif button_name == 'high_scores':
                                print("Show high scores")
                                show_high_scores = True
                            elif button_name == 'exit':
                                logging.shutdown()
                                upload_logs_to_s3()
                                pygame.quit()
                                exit()
                            elif button_name == 'music_toggle':
                                if music_on:
                                    pygame.mixer.music.pause()
                                    music_on = False
                                else:
                                    pygame.mixer.music.unpause()
                                    music_on = True

        screen.fill(background_color)

        if show_high_scores:
            high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
            high_score_rect = high_score_text.get_rect(center=(320, 50))
            screen.blit(high_score_text, high_score_rect)
            button_width = high_score_rect.width + 20
            button_x = 320 - button_width // 2
            pygame.draw.rect(screen, BUTTON_COLOR, (button_x, 150, button_width, 40))
            return_to_home_text = font.render('Return To Home', True, (255, 255, 255))
            return_to_home_rect = return_to_home_text.get_rect(center=(320, 170))
            screen.blit(return_to_home_text, return_to_home_rect)
        else:
            for button_name, button_rect in buttons.items():
                if button_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect)
                else:
                    pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
            
                if button_name == 'music_toggle':
                    screen.blit(music_on_text if music_on else music_off_text, button_rect)
                else:
                    text = font.render(button_name.replace('_', ' ').title(), True, (255, 255, 255))
                    text_rect = text.get_rect(center=button_rect.center)
                    screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)


def tester(obstacle_Timer):
    timer = obstacle_Timer
    timerSF = font.render(f'Timer: {int(timer)}', False, ('black'))
    timerRect = timerSF.get_rect(center = (320, 200))
    screen.blit(timerSF, timerRect)

pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
screen = pygame.display.set_mode((640, 360), flags=pygame.SCALED)
pygame.display.set_caption('PyJumper')
clock = pygame.time.Clock()
font = pygame.font.Font('font/Pixeltype.ttf', 50)
gameActive = False
startTime = 0
score = 0

#intro screen
playerStand = pygame.image.load('graphics/player/down.png').convert_alpha()
playerStand = pygame.transform.scale(playerStand, (90, 180))
playerStandRect = playerStand.get_rect(center = (320, 180))

gameOverSf = font.render('YOU NEED TO WIPE!!!', False, ('black'))
gameOverRect = gameOverSf.get_rect(center = (320, 70))

startScreenSf = font.render("DON'T POOP YOUR PANTS", False, ('black'))
startScreenRect = startScreenSf.get_rect(center = (320, 300))

homeButtonSf = font.render("Return To Home", False, ('black'))
homeButtonRect = homeButtonSf.get_rect(center = (320, 330))

startAgainButtonSf = font.render("Start Again", False, ('black'))
startAgainButtonRect = startAgainButtonSf.get_rect(center = (320, 280))

#Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacleGroup = pygame.sprite.Group()


async def main():
    global gameActive, startTime, score, font, clock, screen, bgMusic
    global playerStand, playerStandRect, gameOverSf, gameOverRect, startScreenSf
    global player, obstacleGroup, startScreenRect, startAgainButtonRect, startAgainButtonSf
    global score_written
    x = 0
    y = 0
    test = False
    if not gameActive:  
        startTime = 0
        score = 0
        player.sprite.rect.midbottom = (100, 200)
        obstacleGroup.empty()  
        score_written = False

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.shutdown()
                upload_logs_to_s3()
                pygame.quit()
                exit()

            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and not gameActive:
                    gameActive = True
                    test = True
                    startTime = pygame.time.get_ticks()

                if event.type == pygame.MOUSEBUTTONDOWN and not gameActive:
                    mouse_pos = pygame.mouse.get_pos()
                    if homeButtonRect.collidepoint(mouse_pos):
                        return
                    elif startAgainButtonRect.collidepoint(mouse_pos):
                        gameActive = True
                        startTime = pygame.time.get_ticks()
                        score = 0
                        player.sprite.rect.midbottom = (100, 200)
                        obstacleGroup.empty()  
                        x = 0
                        y = 0
                        test = True  

        if gameActive:
            if test:
                x += 0.015
                if x > 1:
                    obstacleGroup.add(Obstacle(random.choice(['flyer', 'slimer', 'slimer', 'slimer', 'flyer'])))
                    y += 1
                    x = 0

        if gameActive:
            screen.blit(pygame.image.load('graphics/Sky.png').convert_alpha(), (0, 0))
            screen.blit(pygame.image.load('graphics/ground.png').convert_alpha(), (0, 300))
            score = displayScore()

            player.draw(screen)
            player.update()

            obstacleGroup.draw(screen)
            obstacleGroup.update()

            gameActive = spriteCollisions(player, obstacleGroup)

        else:
            screen.fill('cyan')
            scoreMessage = font.render(f'Score: {int(score)}', False, 'black')
            scoreMessageRect = scoreMessage.get_rect(center=(320, 300))
            if score == 0:
                screen.blit(startScreenSf, startScreenRect)
                screen.blit(homeButtonSf, homeButtonRect)
                screen.blit(playerStand, playerStandRect)
            else:
                screen.blit(scoreMessage, scoreMessageRect)
                screen.blit(gameOverSf, gameOverRect)
                screen.blit(playerStand, playerStandRect)
                screen.blit(homeButtonSf, homeButtonRect)
                screen.blit(startAgainButtonSf, startAgainButtonRect)
                if not score_written:
                    write_high_score(int(score))
                    score_written = True

        pygame.display.update()
        await asyncio.sleep(0)


if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((640, 360))
    clock = pygame.time.Clock()
    homePage(screen, clock)
    asyncio.run(main())