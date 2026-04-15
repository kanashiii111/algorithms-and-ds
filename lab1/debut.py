EMPTY: int = 0
PAWN: int = 1
KNIGHT: int = 2
BISHOP: int = 3
ROOK: int = 4
QUEEN: int = 5
KING: int = 6

as_white: bool = False
as_black: bool = False
ep_cell = ""
castle = []

playing_white = {
    ("c7c5",): "g1f3",
    
}

def read_board():
    global as_black, as_white, ep_cell, castle

    ping = int(input())
    amount = int(input())

    board = [[[False, EMPTY] for _ in range(8)] for _ in range(8)]

    for _ in range(amount):
        line = input().split()
        pos = line[0]
        x, y = ord(pos[0]) - ord('a'), int(pos[1]) - 1

        is_my_team = line[1] == '+'
        if is_my_team:
            if y <= 1:
                as_white = True
            else:
                as_black = True

        type = int(line[2])
        board[x][y] = [is_my_team, type]
    ep_cell = input()
    castle = [x for x in input().split()]

    return board, ping


# ========================
# Main
# ========================

def main():
    board, ping = read_board()
    move_number = ping + 1

    move 


    print(f"{move} {move_number}")

if __name__ == "__main__":
    main()