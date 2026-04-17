import pygame
from graphics import Graphics
from env import Env
from human_agent import Human_Agent
from random_agent import Random_Agent
from DQN_Agent_min import DQN_Agent_min
from DQN_Agent import DQN_Agent


clock = pygame.time.Clock()
FPS = 60


def main(agent_type="human"):
    '''
    the main game loop
    '''

    pygame.init()

    #RUN VARIABLES
    FORCE_SPLIT = True
    run = True
    balance = 10000
    graphics = Graphics(balance)
    env = Env(graphics, balance)
    env.start(graphics, force_split=FORCE_SPLIT)
    if agent_type == "human":
        agent = Human_Agent()
    elif agent_type == "random":
        agent = Random_Agent()
    elif agent_type == "dqn":
    # agent = DQN_Agent_min(parametes_path="checkpoints/BlackJack-min-run-5.pth", train=False)
        agent = DQN_Agent(min_parametes_path="checkpoints/BlackJack-min-run-10.pth",
                          split_parameters_path="checkpoints-split/BlackJack-split-run-5 (min model number 10).pth",
                          train=False)
    
    last_move_time = pygame.time.get_ticks()
    action_delay = 1500

    #LOOP
    while(run):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: #on quit (the red X at the top)
                run = False
            #human agent
            if isinstance(agent,Human_Agent):
                action = agent.get_action(event, env, graphics)
                env.move(action, graphics, force_split=FORCE_SPLIT)

            #DQN agent
        current_time = pygame.time.get_ticks()
        if not isinstance(agent, Human_Agent) and current_time - last_move_time >= action_delay: #creating a delay so can see what the bot plays
            if isinstance(agent, DQN_Agent):
                action = agent.get_Action(env, train=False)
            else:
                action = agent.get_Action(env.state.get_state_AI(), train=False) if env.state.round_phase == 'playing' else 6
            env.move(action, graphics)
            last_move_time = current_time
            # if action is not None:
            #     print(action, 'bet = ' + str(env.state.bet_val))

        #render interactable objects
        graphics.render_screen(env)

        #update screen
        pygame.display.update()
        clock.tick(FPS)

        #check if the game ended (if needed) and display a picture if the game is over
        graphics.end_pic(graphics.screen, env, force_split=FORCE_SPLIT)


#run the main game loop
if __name__ == '__main__':
    main()