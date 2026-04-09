EMPTY: int = 0
PAWN: int = 1
KNIGHT: int = 2
BISHOP: int = 3
ROOK: int = 4
QUEEN: int = 5
KING: int = 6

queens_gambit = {
    
}

as_black : bool = False
as_white : bool = False

ping = int(input())  # Тут можно хранить что угодно, например ход
print(f"# Ход номер: {ping+1}")  # Выводим в отладку
amount = int(input())  # Читам число фигур

# Читам доску
board = [[[False, EMPTY] for _ in range(8)] for _ in range(8)];
for i in range(0, amount):
    line = input().split()
    # Клетка фигуры
    pos = line[0]
    x, y = ord(line[0][0]) - ord('a'), int(line[0][1]) - 1
    
    is_my_team = line[1] == '+'
    if is_my_team:
        if y == 0 or y == 1:
            as_white = True
        else:
            as_black = True
        
    type = int(line[2])  # Тип фигуры
    board[x][y] = [is_my_team, type]

def best_move_as_white():
    for y in range(7):
        for x in range(8):
            if board[x][y][0] and board[x][y][1] == PAWN:
                if board[x][y+1][1] == EMPTY:
                    print(f"{chr(x+ord('a'))}{y+1}{chr(x+ord('a'))}{y+2}")
                    return
def best_move_as_black():
    for y in range(7):
        for x in range(8):
            if board[x][y][0] and board[x][y][1] == PAWN:
                if board[x][y-1][1] == EMPTY:
                    print(f"{chr(x+ord('a'))}{y+1}{chr(x+ord('a'))}{y}")
                    return

for y in range(7):
    for x in range(8):
        if as_white:
            best_move_as_white()
        elif as_black:
            best_move_as_black()