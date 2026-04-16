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

white = {
    1: "d2d4",
    2: "c2c4",                    
    3: "g1f3",                   
    4: "b1c3",
    5: "c1f4",
    6: "e2e3",
    7: "f1e2",
    8: "e1g1",
}

black = {
    1: "g1f3",
    2: "d2d3",
    3: "g2g3",
    4: "f1g2",
    5: "e1g1",
    6: "b1d2",
    7: "e2e4",
    8: "f1e1"
}

def is_valid_move(board, move) -> bool:
    from_x, from_y = ord(move[0]) - ord('a'), int(move[1]) - 1
    to_x, to_y = ord(move[2]) - ord('a'), int(move[3]) - 1
    if board[to_x][to_y][0] == True and board[to_x][to_y][1] != EMPTY: return False
    return True

def read_board():
    global as_black, as_white, ep_cell, castle

    ping = int(input())
    amount = int(input())

    board = [[[False, EMPTY] for _ in range(8)] for _ in range(8)]

    for i in range(amount):
        line = input().split()
        pos = line[0]
        x, y = ord(pos[0]) - ord('a'), int(pos[1]) - 1

        is_my_team = line[1] == '+'
        if i == 1:
            if is_my_team:
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

    move = black[move_number] if as_black else white[move_number]
    
    if is_valid_move(board, move):
        print(f"{move} {move_number}")
        print(f"# {move} {move_number}")

if __name__ == "__main__":
    main()