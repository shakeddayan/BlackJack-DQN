import pygame
from env import Env
# from human_agent import Human_Agent
from random_agent import Random_Agent

clock = pygame.time.Clock()
FPS = 60


def main():
    '''
    the main game loop
    '''

    #RUN VARIABLES
    run = 0
    win = 0
    balance = 10000
    env = Env(balance=balance)
    env.start()
    agent = Random_Agent()

    #LOOP
    while(run < 10000):
        run += 1
    
        action = agent.get_Action(env=env)
        # print(action)
        env.move(action, G= None)

        #render interactable objects
        # graphics.render_screen(env)

        #update screen
        # pygame.display.update()
        # clock.tick(FPS)

        #check if the game ended (if needed) and display a picture if the game is over
        # graphics.end_pic(graphics.screen, env)
        has_split = env.state.second_hand_active
        if env.checkend:
            print(env.state)
            d_cards = env.d_hand_vals
            check_end_status = env.CheckEnd()
            print(check_end_status)
            if (check_end_status != 0):
                 print(d_cards)
            if check_end_status in [1,4,5,6,8]:
                    win += 1
                    if check_end_status == 1 and has_split == True:
                        win += 1


    print(f"win: {win}\nwin rate: {win * 100/(run-1)}%\nend balance: {env.state.balance}")


#run the main game loop
if __name__ == '__main__':
    main()