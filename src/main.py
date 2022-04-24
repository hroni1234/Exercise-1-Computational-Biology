import math
import random
import pygame
from inputBox import InputBox
from label import Label
from Person import Person
from Cell import Cell
from typing import List
import matplotlib.pyplot as plt
import sys

size = (width, height) = (200, 200)
N = 12000  # persons number
D = 0.02  # covid percentage
R = 0.1  # fast persons percentage
F = 10  # fast steps
X = 14  # generations till healing
L = 0.02  # low infection p
H = 0.8  # high infection p
P = L  # infection risk
T = 0.2  # threshold
pause = False
ext = False


def initialize_grid():
    grid = []
    num_of_fast = math.floor(R * N)
    num_of_infected = math.floor(N * D)
    # empty grid initialization
    for i in range(width):
        current_row = []
        for j in range(height):
            current_row.append(Cell())
        grid.append(current_row)
    # set positions to all persons
    for i in range(N):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        while not grid[x][y].is_empty():
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
        grid[x][y].set_persons(Person(X))
    # setting the fast ones
    for i in range(num_of_fast):
        x = random.randint(0, width - 1)
        y = random.randint(0, width - 1)
        while grid[x][y].is_empty() or grid[x][y].persons[0].is_fast:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
        grid[x][y].persons[0].is_fast = True
    # setting the infected ones
    for i in range(num_of_infected):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        while grid[x][y].is_empty() or grid[x][y].persons[0].is_covid:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
        grid[x][y].persons[0].infected()
    return grid


def move_prople_on_the_grid(old_gen: List[List[Cell]]):
    move_position_indexs = {} #her for each cell that we want to populate, we save all the person that want to move in
    for old_x in range(width):
        for old_y in range(height):
            if not old_gen[old_x][old_y].is_empty(): #if the cell isnt empty we want to choose new random position for the person in it
                try_count = 8  # number of nebs will be the number of try to find new cell or to stay in place, after 8 trys he will stay in his place
                fast_or_slow_step_x = 1
                fast_or_slow_step_y = 1
                if old_gen[old_x][old_y].persons[0].is_fast: #if the dude is fast we want him to do F steps in mannhatan steps
                    fast_or_slow_step_x = random.randint(0, F)
                    fast_or_slow_step_y = F - fast_or_slow_step_x
                new_x = (old_x + random.randint(-1, 1) * fast_or_slow_step_x) % width
                new_y = (old_y + random.randint(-1, 1) * fast_or_slow_step_y) % height
                while (not old_gen[new_x][new_y].is_empty()) and try_count > 0:
                    new_x = (old_x + random.randint(-1, 1) * fast_or_slow_step_x) % width
                    new_y = (old_y + random.randint(-1, 1) * fast_or_slow_step_y) % height
                    try_count -= 1
                # if all neighbours are taken, don't move, easy case
                if try_count > 0:
                    if (new_x, new_y) not in move_position_indexs.keys():
                        move_position_indexs[(new_x, new_y)] = []
                    move_position_indexs[(new_x, new_y)].append((old_x, old_y))
    # !!!!position people!!!!
    move = move_position_indexs.keys()#save run time
    for new_pos in move: #now populate the cells
        i,j = new_pos
        if len(move_position_indexs[(i, j)]) != 0:
            c = random.randint(0, len(move_position_indexs[(i, j)])-1) # if only one person want to get in c=0, else its select randomly one of the persons
            x, y = move_position_indexs[(i, j)][c]
            old_gen[i][j].set_persons(old_gen[x][y].persons[0])
            old_gen[x][y].persons = old_gen[x][y].persons[1:]  # remove person from old cell

    return old_gen


def after_people_have_moved(gen: List[List[Cell]]):
    cells_to_infect = []
    # we dont want that the cells we be infected during the itertion
    # cause it may lead to chain of infetions (no legal in only one gen), for example:
    # grid = [1,0,0,0] -> grid = [1,1,0,0] -> .. ->grid =[1,1,1,1]
    # So we save that only grid[1] should be infected, and we do that in the end
    for i in range(width):
        for j in range(height):
            if not gen[i][j].is_empty():
                gen[i][j].persons[0].generation_passed()  # some stuff
                # save who to infect in covid19
                if not gen[i][j].persons[0].is_covid and not gen[i][j].persons[0].is_healed:
                    for x_neb in [(i - 1) % width, i, (i + 1) % width]:
                        for y_neb in [(j - 1) % height, j, (j + 1) % height]:
                            if not gen[x_neb][y_neb].is_empty():
                                neb = gen[x_neb][y_neb].persons[0]
                                if neb.is_covid and random.random() < P:
                                    cells_to_infect.append((i, j))
    # infect in covid19
    for (x, y) in cells_to_infect:
        gen[x][y].persons[0].infected()
    return gen


'''take grid of cells and convert it into grid of integers.'''
def to_color_grid(grid: List[List[Cell]]):
    # black empty 3
    # green heal 2
    # whit human 1
    # red infected <= 0
    colored_grid = []
    for i in range(width):
        colored_grid.append([])
        for j in range(height):
            if grid[i][j].is_empty():
                colored_grid[i].append(3)
            elif grid[i][j].persons[0].is_healed:
                colored_grid[i].append(2)
            elif grid[i][j].persons[0].is_covid:
                colored_grid[i].append(-1 * grid[i][j].persons[0].days_to_recovery)
            else:  # just regular human
                colored_grid[i].append(1)
    return colored_grid


def get_infected_percentage(gen: List[List[Cell]]):
    num_of_infected_currently = 0
    for i in range(width):
        for j in range(height):
            if not gen[i][j].is_empty() and gen[i][j].persons[0].is_covid:
                num_of_infected_currently += 1
    return num_of_infected_currently / N


def get_healed_percentage(gen: List[List[Cell]]):
    num_of_healed_currently = 0
    for i in range(width):
        for j in range(height):
            if not gen[i][j].is_empty() and gen[i][j].persons[0].is_healed:
                num_of_healed_currently += 1
    return num_of_healed_currently / N


# for the UI
board = pygame.display.set_mode((550, 550))
background_color = (20, 0, 0)
FONT = pygame.font.SysFont("Segoe UI", 20)

'''for the UI and to get the params'''
def game_intro():
    global N, D, R, F, X, L, H, P, T
    clock = pygame.time.Clock()
    label_1 = Label(20, 50, "number of people (most be <=40000):")
    label_2 = Label(20, 100, "Percentage of infection(0 to 1):")
    label_3 = Label(20, 150, "percentage of \"fast\" people(0 to 1):")
    label_4 = Label(20, 200, "genertion till recovery:")
    label_5 = Label(20, 250, "low p (0 to 1):")
    label_6 = Label(20, 300, "high p (0 to 1):")
    label_7 = Label(20, 350, "thershold: (0 to 1):")
    label_8 = Label(20, 400, "To pause/continue press space.")
    label_9 = Label(20, 450, "To start the animation press Enter.")
    label_boxes = [label_1, label_2, label_3, label_4, label_5, label_6, label_7, label_8, label_9]
    input_box1 = InputBox(420, 40, 50, 32, str(N))
    input_box2 = InputBox(420, 90, 50, 32, str(D))
    input_box3 = InputBox(420, 140, 50, 32, str(R))
    input_box4 = InputBox(420, 190, 50, 32, str(X))
    input_box5 = InputBox(420, 240, 50, 32, str(L))
    input_box6 = InputBox(420, 290, 50, 32, str(H))
    input_box7 = InputBox(420, 340, 50, 32, str(T))
    input_boxes = [input_box1, input_box2, input_box3, input_box4, input_box5, input_box6, input_box7]
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for box in input_boxes:
                box.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    N = int(input_box1.text)
                    D = float(input_box2.text)
                    R = float(input_box3.text)
                    X = int(input_box4.text)
                    L = float(input_box5.text)
                    H = float(input_box6.text)
                    T = float(input_box7.text)
                    done = True

        for box in input_boxes:
            box.update()

        board.fill(background_color)
        for box in input_boxes:
            box.draw(board)

        for box in label_boxes:
            box.draw(board)

        pygame.display.flip()
        clock.tick(30)


'''UI'''
def grid_ui(colored_grid: List[List[int]]):
    block_size = 2
    global height, width
    for i in range(height):
        for j in range(width):
            x = i * block_size
            y = j * block_size
            if colored_grid[j][i] == 2:
                pygame.draw.rect(board, (128, 255, 0), (x, y, block_size, block_size))
            elif colored_grid[j][i] <= 0:
                pygame.draw.rect(board, (255, 0, 0), (x, y, block_size, block_size))
            elif colored_grid[j][i] == 1:
                pygame.draw.rect(board, (255, 255, 255), (x, y, block_size, block_size))
            else:
                pygame.draw.rect(board, (0, 0, 0), (x, y, block_size, block_size))
            pygame.draw.line(board, (20, 20, 20), (x, y), (x, height))
            pygame.draw.line(board, (20, 20, 20), (x, y), (width, y))
    pygame.display.update()


'''check_event : check for keyword that had pressed,
scape for pause and to continue.
click on the X to stop the simulation'''
def check_event():
    global pause, ext
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pause = False
            ext = True
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pause = not pause


'''check if the system got vaild params'''
def validation():
    global N, D, R, F, X, L, H, P, T
    return 1 <= N <= 40000 and 0 <= D <= 1 and 0 <= R <= 1 and 0 <= X and 0 <= L <= 1 and 0 <= H <= 1 and 0 <= T <= 1


if __name__ == '__main__':

    # intro UI
    game_intro()
    if not validation():
        print("Bad params were given")
        sys.exit()
    if H < L:
        print("warning the pH < pL, you may not want to do it ")
    # init
    current_gen = initialize_grid()
    gen_index = 0
    per = []
    p = D

    while not ext:
        # print some info
        print("pass gen" + gen_index.__str__())
        p = get_infected_percentage(current_gen)
        per.append(p)  # for the graph
        print("covid-19 percentage : " + (p * 100).__str__())

        # handle the exit and the pause, if puse we just do busy wait with "True condition loop"
        check_event()
        while pause:
            check_event()
        # UI
        colored_grid = to_color_grid(current_gen)
        grid_ui(colored_grid)

        # the algorithem
        next_gen = move_prople_on_the_grid(current_gen)
        current_gen = next_gen
        if p > T:
            P = L
        else:
            P = H
        current_gen = after_people_have_moved(current_gen)  # infection and some other stuff
        gen_index += 1

    # print summary info
    healed_p = get_healed_percentage(current_gen)
    print("summary:")
    print("covid-19 p: " + p.__str__())
    print("healed p: " + healed_p.__str__())
    print("people who didnt infected at all p :" + (1 - p - healed_p).__str__())

    # show the sickness graph
    plt.plot(per)
    plt.title("Wave")
    plt.ylabel("covid-19")
    plt.xlabel("generation")
    plt.show()

'''for debug'''
def is_valid_grid(gen: List[List[Cell]]):
    for i in range(width):
        for j in range(height):
            if gen[i][j].is_conflict():
                return False
    return True
