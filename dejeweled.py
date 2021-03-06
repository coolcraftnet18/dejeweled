import random
import copy
import ai
import time

USER_INPUT = False
PRINT_BOARDS = True
OUTPUT_TO_FILE = True

WIDTH = 8
HEIGHT = 10
GEMS = ["△", "◆", "◙", "▩", "◎", "◓", "▢"]

ORIG_AGENTS = ["expectimax", "random"]

def main():
    OUTPUT_FILE = "out/{}x{}_{}gems.csv".format(WIDTH, HEIGHT, len(GEMS))

    AGENTS = ORIG_AGENTS.copy()
    AGENT = AGENTS[0]
    AGENTS.pop(0)

    BOARD = [[random.choice(GEMS) for c in range(WIDTH)] for r in range(HEIGHT)]
    SCORE = MOVES = GEMS_CLEARED = CASCADES = 0

    # clear matches
    while get_matches(BOARD) != []:
        for match in get_matches(BOARD):
            for gem in match:
                BOARD[gem[1]][gem[0]] = random.choice(GEMS)

    # game loop
    while True:
        if PRINT_BOARDS:
            print("\nscore: ", SCORE)
            print_board(BOARD)

        if not get_valid_swaps(BOARD):
            print("GAME OVER")
            print_board(BOARD)
            print("agent:          ", AGENT)
            print("final score:    ", SCORE)
            print("moves:          ", MOVES)
            print("gems cleared:   ", GEMS_CLEARED)
            print("cascades:       ", CASCADES)
            gpm = float(GEMS_CLEARED) / float(MOVES)
            print("avg gems/move:  ", gpm)
            spm = float(SCORE) / float(MOVES)
            print("avg score/move: ", spm)
            
            if OUTPUT_TO_FILE:
                with open(OUTPUT_FILE, mode='a') as f :
                    f.write("{},{},{},{},{},{},{}\n".format(AGENT,SCORE,MOVES,GEMS_CLEARED,CASCADES,gpm,spm))

            
            if not AGENTS:
                exit()
            else:
                AGENT = AGENTS[0]
                AGENTS.pop(0)
                BOARD = [[random.choice(GEMS) for c in range(WIDTH)] for r in range(HEIGHT)]
                SCORE = MOVES = GEMS_CLEARED = CASCADES = 0

        if USER_INPUT:
            print("enter pairs to swap: x1 y1 x2 y2")
            coords = [int(val) for val in input().split(" ")]
        else:
            current_node = ai.Node(BOARD, SCORE, 0)
            coords = current_node.get_next_swap(AGENT)
        
        MOVES += 1

        # make swap on prospective next board
        next_board = copy.deepcopy(BOARD)
        swap_gems(next_board,coords[0], coords[1], coords[2], coords[3])
        
        # check that match is valid
        matches = get_matches(next_board)
        if matches == []: continue
        BOARD = next_board

        # track if we are cascading
        settled_once = False
        # clear matches and increment score until settled
        while get_matches(BOARD) != []:
            if settled_once: CASCADES += 1
            for match in get_matches(BOARD):
                for gem in match:
                    SCORE += (10 + (len(match) - 3) * 10)
                    BOARD[gem[1]][gem[0]] = " "
                    GEMS_CLEARED += 1

            settled_once = True
            drop_and_fill(BOARD)

def get_gem(board, x, y):
    '''
    get gem on board at specified (x, y)
    ensures x and y are within bounds of board
    '''
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT): return " "
    else: return board[y][x]

def swap_gems(board,x1,y1,x2,y2):
    '''
    Swap two gems on a board given their coordinates
    '''
    # Swap the gems
    board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]

def get_matches(board):
    '''
    return a list of groups of gems in matching triplets that should be removed
    [[(x1,y1),(x2,y2),(x3,y3)],...]
    '''
    groups_to_remove = []
    board_copy = copy.deepcopy(board)

    # loop through each space, check for 3 adjacent identical gems
    for x in range(WIDTH):
        for y in range(HEIGHT):
            # look for horizontal matches
            if board_copy[y][x] == get_gem(board_copy,x+1,y) == get_gem(board_copy,x+2,y) != " ":
                target = board_copy[y][x]
                offset = 0
                gems = []
                while get_gem(board_copy,x+offset,y) == target:
                    gems.append((x+offset, y))
                    board_copy[y][x+offset] = " "
                    offset += 1
                groups_to_remove.append(gems)

            # look for vertical matches
            if board_copy[y][x] == get_gem(board_copy,x,y+1) == get_gem(board_copy,x,y+2) != " ":
                target = board_copy[y][x]
                offset = 0
                gems = []
                while get_gem(board_copy,x,y+offset) == target:
                    gems.append((x,y+offset))
                    board_copy[y+offset][x] = " "
                    offset += 1
                groups_to_remove.append(gems)

    return groups_to_remove

def get_valid_swaps(board):
    '''
    Return a list of pairs to swap
    '''
    swaps = set()

    # X represents a gem of a specific type
    for x in range(WIDTH):
        for y in range(HEIGHT):
            current_gem = board[y][x]
            if(current_gem == get_gem(board, x+1, y) != " "):
                # Case  _ X x _
                # check left up
                if(current_gem == get_gem(board, x-1, y-1)):
                    swaps.add((x-1, y-1, x-1, y))
                # check left down
                if(current_gem == get_gem(board, x-1, y+1)):
                    swaps.add((x-1, y, x-1, y+1))
                # check left left
                if(current_gem == get_gem(board, x-2, y)):
                    swaps.add((x-2, y, x-1, y))
                # check right up
                if(current_gem == get_gem(board, x+2, y-1)):
                    swaps.add((x+2, y-1, x+2, y))
                # check right down
                if(current_gem == get_gem(board, x+2, y+1)):
                    swaps.add((x+2, y, x+2, y+1))
                # check right right
                if(current_gem == get_gem(board, x+3, y)):
                    swaps.add((x+2, y, x+3, y))

            elif(current_gem == get_gem(board, x+2, y) != " "):
                # Case X _ x
                # check down
                if(current_gem == get_gem(board, x+1, y+1)):
                    swaps.add((x+1, y, x+1, y+1))
                # check up
                if(current_gem == get_gem(board, x+1, y-1)):
                    swaps.add((x+1, y, x+1, y-1))

            if(current_gem == get_gem(board, x, y+1) != " "):
                # Case _
                #      X
                #      x
                #      _
                # Check up right
                if(current_gem == get_gem(board, x+1, y-1)):
                    swaps.add((x, y-1, x+1, y-1))

                # Check up left
                if(current_gem == get_gem(board, x-1, y-1)):
                    swaps.add((x, y-1, x-1, y-1))

                # Check up up
                if(current_gem == get_gem(board, x, y-2)):
                    swaps.add((x, y-2, x, y-1))

                # Check down left
                if(current_gem == get_gem(board, x-1, y+2)):
                    swaps.add((x-1, y+2, x, y+2))

                # Check down right
                if(current_gem == get_gem(board, x+1, y+2)):
                    swaps.add((x, y+2, x+1, y+2))

                # Check down down
                if(current_gem == get_gem(board, x, y+3)):
                    swaps.add((x, y+2, x, y+3))

            elif(current_gem == get_gem(board, x, y+2) != " "):
                # Case X
                #      _
                #      x
                # check left right
                if(current_gem == get_gem(board, x+1, y+1)):
                    swaps.add((x, y+1, x+1, y+1))
                if(current_gem == get_gem(board, x-1, y+1)):
                    swaps.add((x-1, y+1, x, y+1))

    return swaps

def apply_gravity(board):
    for x in range(WIDTH):
        for y in range(HEIGHT - 1):
            if board[y+1][x] == " ":
                swap_gems(board, x, y, x, y+1)

def drop_and_fill(board):
    apply_gravity(board)

    for x in range(WIDTH):
        for y in range(HEIGHT):
            if board[y][x] == " ":
                board[y][x] = random.choice(GEMS)
    
def print_board(board):
    for col in board:
        print("║ ", end="")
        for row in col:
            print(row, " ", end="")
        print("║")

if __name__ == "__main__":
    main()
