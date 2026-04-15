EMPTY: int = 0
PAWN: int = 1
KNIGHT: int = 2
BISHOP: int = 3
ROOK: int = 4
QUEEN: int = 5
KING: int = 6

queens_gambit = {
    1: "d2d4",
    2: "c2c4",
    3: "g1f3",
    4: "b1c3",
    5: "c1f4",
    6: "e2e3",
    7: "f1d3",
    8: "e1g1",
}

queens_gambit_black = {
    1: "d7d5",
    2: "e7e6",
    3: "g8f6",
    4: "f8e7",
    5: "e8g8",
    6: "c7c5",
    7: "b8c6",
}

as_black: bool = False
as_white: bool = False
ep_cell = ""
castle = []

def parse_move(move):
    x1 = ord(move[0]) - ord('a')
    y1 = int(move[1]) - 1
    x2 = ord(move[2]) - ord('a')
    y2 = int(move[3]) - 1
    return x1, y1, x2, y2

def is_valid_basic(board, move):
    x1, y1, x2, y2 = parse_move(move)

    # есть ли наша фигура
    if not board[x1][y1][0]:
        return False

    # не бьём свою
    if board[x2][y2][0]:
        return False

    return True

def get_opening_move(opening, move_number, board):
    # пробуем текущий и несколько следующих ходов
    for i in range(move_number, move_number + 3):
        if i in opening:
            move = opening[i]
            if is_valid_basic(board, move):
                return move
    return None

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

def is_in_check(board):
    king_x = king_y = -1

    # найти короля
    for x in range(8):
        for y in range(8):
            is_my, t = board[x][y]
            if is_my and t == KING:
                king_x, king_y = x, y
                break

    if king_x == -1:
        return None

    # проверка атак
    for x in range(8):
        for y in range(8):
            is_my, t = board[x][y]

            if is_my:
                continue

            dx = king_x - x
            dy = king_y - y

            if t == KNIGHT:
                if (abs(dx), abs(dy)) in [(1,2),(2,1)]:
                    return (x,y)

    return None

def generate_pawn_moves(board):
    quiet_moves = []
    captures = []
    valuable_captures = []

    for letter in range(8):
        for number in range(8):
            is_my, type = board[letter][number]

            if not is_my:
                continue
            
            if type == PAWN:
                direction = 1 if as_white else -1
                newY = number + direction

                if 0 <= newY < 8:
                    # взятия
                    for dx in [-1, 1]:
                        newX = letter + dx
                        if 0 <= newX < 8:
                            opp_value = board[newX][newY][1]
                            our_value = board[letter][number][1]
                            if board[newX][newY][1] != EMPTY and not board[newX][newY][0]:
                                move = f"{ chr(letter+97) }{ number + 1 }{ chr(newX+97) }{ newY + 1 }"
                                if newY == 7:
                                    move += "q"
                                if our_value < opp_value:
                                    valuable_captures.append(move)
                                    continue
                                captures.append(move)
                    # ход вперёд
                    if board[letter][newY][1] == EMPTY:
                        move = move = f"{ chr(letter+97) }{ number + 1 }{ chr(letter+97) }{ newY + 1 }"
                        if newY == 7: 
                            move+='q'
                        quiet_moves.append(move)
    
    print(f"# --- PAWNS ---")
    print(f"# val: {valuable_captures}")
    print(f"# cap: {captures}")
    print(f"# qui: {quiet_moves}")
    return valuable_captures, captures, quiet_moves

def generate_knight_moves(board):
    quiet_moves = []
    captures = []
    valuable_captures = []

    steps = [(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]

    for x in range(8):
        for y in range(8):
            is_my, piece = board[x][y]

            if not is_my or piece != KNIGHT:
                continue

            for dx, dy in steps:
                nx, ny = x + dx, y + dy

                if not (0 <= nx < 8 and 0 <= ny < 8):
                    continue

                if board[nx][ny][0]:
                    continue

                move = f"{chr(x+97)}{y+1}{chr(nx+97)}{ny+1}"

                if board[nx][ny][1] != EMPTY:
                    if piece < board[nx][ny][1]:
                        valuable_captures.append(move)
                    else:
                        captures.append(move)
                else:
                    quiet_moves.append(move)

    return valuable_captures, captures, quiet_moves

def generate_bishop_moves(board):
    quiet_moves = []
    captures = []
    valuable_captures = []

    for letter in range(8):
        for number in range(8):
            is_my, type = board[letter][number]

            if not is_my:
                continue
            
            if type == BISHOP:
                steps = [ (1, 1), (1, -1), (-1, 1), (-1, -1) ]
                for dx, dy in steps:
                    newX, newY = letter + dx, number + dy
                    while (0 <= newX < 8 and 0 <= newY < 8):
                        if board[newX][newY][1] != EMPTY and board[newX][newY][0]:
                            break
                        if board[newX][newY][1] != EMPTY and not board[newX][newY][0]:
                            opp_value = board[newX][newY][1]
                            our_value = board[letter][number][1]
                            move = f"{ chr(letter+97) }{ number + 1 }{ chr(newX+97) }{ newY + 1 }"
                            if our_value < opp_value:
                                valuable_captures.append(move)
                                newX, newY = letter + dx, number + dy
                                continue
                            captures.append(move)
                            newX, newY = letter + dx, number + dy
                            continue
                        move = f"{ chr(letter+97) }{ number + 1 }{ chr(letter+97) }{ newY + 1 }"
                        quiet_moves.append(move)

                        newX, newY = letter + dx, number + dy
    
    print(f"# --- BISHOPS ---")
    print(f"# val: {valuable_captures}")
    print(f"# cap: {captures}")
    print(f"# qui: {quiet_moves}")
    return valuable_captures, captures, quiet_moves

def generate_rook_moves(board):
    quiet_moves = []
    captures = []
    valuable_captures = []

    for letter in range(8):
        for number in range(8):
            is_my, type = board[letter][number]

            if not is_my:
                continue
            
            if type == ROOK:
                steps = [ (0, 1), (1, 0), (-1, 0), (0, -1) ]
                for dx, dy in steps:
                    newX, newY = letter + dx, number + dy
                    while (0 <= newX < 8 and 0 <= newY < 8):
                        if board[newX][newY][1] != EMPTY and board[newX][newY][0]:
                            break
                        if board[newX][newY][1] != EMPTY and not board[newX][newY][0]:
                            opp_value = board[newX][newY][1]
                            our_value = board[letter][number][1]
                            move = f"{ chr(letter+97) }{ number + 1 }{ chr(newX+97) }{ newY + 1 }"
                            if our_value < opp_value:
                                valuable_captures.append(move)
                                newX, newY = letter + dx, number + dy
                                continue
                            captures.append(move)
                            newX, newY = letter + dx, number + dy
                            continue
                        move = f"{ chr(letter+97) }{ number + 1 }{ chr(letter+97) }{ newY + 1 }"
                        quiet_moves.append(move)

                        newX, newY = letter + dx, number + dy
    
    print(f"# --- ROOKS ---")
    print(f"# val: {valuable_captures}")
    print(f"# cap: {captures}")
    print(f"# qui: {quiet_moves}")
    return valuable_captures, captures, quiet_moves

def generate_queen_moves(board):
    quiet_moves = []
    captures = []
    valuable_captures = []

    for letter in range(8):
        for number in range(8):
            is_my, type = board[letter][number]

            if not is_my:
                continue
            
            if type == QUEEN:
                steps = [ (0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1) ]
                for dx, dy in steps:
                    newX, newY = letter + dx, number + dy
                    while (0 <= newX < 8 and 0 <= newY < 8):
                        if board[newX][newY][1] != EMPTY and board[newX][newY][0]:
                            break
                        if board[newX][newY][1] != EMPTY and not board[newX][newY][0]:
                            opp_value = board[newX][newY][1]
                            our_value = board[letter][number][1]
                            move = f"{ chr(letter+97) }{ number + 1 }{ chr(newX+97) }{ newY + 1 }"
                            if our_value < opp_value:
                                valuable_captures.append(move)
                                newX, newY = letter + dx, number + dy
                                continue
                            captures.append(move)
                            newX, newY = letter + dx, number + dy
                            continue
                        move = f"{ chr(letter+97) }{ number + 1 }{ chr(letter+97) }{ newY + 1 }"
                        quiet_moves.append(move)

                        newX, newY = letter + dx, number + dy
    
    print(f"# --- QUEEN ---")
    print(f"# val: {valuable_captures}")
    print(f"# cap: {captures}")
    print(f"# qui: {quiet_moves}")
    return valuable_captures, captures, quiet_moves

def generate_king_moves(board):
    quiet_moves = []
    captures = []
    valuable_captures = []

    for letter in range(8):
        for number in range(8):
            is_my, type = board[letter][number]

            if not is_my:
                continue
            
            if type == KING:
                # Все 8 направлений для короля
                steps = [(0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
                
                for dx, dy in steps:
                    newX, newY = letter + dx, number + dy
                    
                    if not (0 <= newX < 8 and 0 <= newY < 8):
                        continue
                    
                    # Пустая клетка
                    if board[newX][newY][1] == EMPTY:
                        move = f"{chr(letter+97)}{number + 1}{chr(newX+97)}{newY + 1}"
                        quiet_moves.append(move)
                    
                    # Враг на клетке
                    elif not board[newX][newY][0]:
                        opp_value = board[newX][newY][1]
                        our_value = board[letter][number][1]
                        move = f"{chr(letter+97)}{number + 1}{chr(newX+97)}{newY + 1}"
                        
                        if our_value < opp_value:
                            valuable_captures.append(move)
                        else:
                            captures.append(move)
    
    print(f"# --- KING ---")
    print(f"# val: {valuable_captures}")
    print(f"# cap: {captures}")
    print(f"# qui: {quiet_moves}")
    return valuable_captures, captures, quiet_moves

def is_valid_move(board, move, is_white, ep_cell="", castle=None):
    if not move:
        return False

    x1, y1, x2, y2 = parse_move(move)

    if not (0 <= x1 < 8 and 0 <= y1 < 8 and 0 <= x2 < 8 and 0 <= y2 < 8):
        return False

    is_my, piece = board[x1][y1]

    if piece == EMPTY or not is_my:
        return False

    if board[x2][y2][0]:
        return False

    dx = x2 - x1
    dy = y2 - y1

    if piece == PAWN:
        direction = 1 if is_white else -1

        if dx == 0 and dy == direction and board[x2][y2][1] == EMPTY:
            return True

        if abs(dx) == 1 and dy == direction and board[x2][y2][1] != EMPTY:
            return True

        return False

    if piece == KNIGHT:
        return (abs(dx), abs(dy)) in [(1,2),(2,1)]

    if piece == BISHOP:
        if abs(dx) != abs(dy):
            return False
        return True

    if piece == ROOK:
        if dx != 0 and dy != 0:
            return False
        return True

    if piece == QUEEN:
        return dx == 0 or dy == 0 or abs(dx) == abs(dy)

    if piece == KING:
        return max(abs(dx), abs(dy)) == 1

    return False

def pick_move(board, attacker = None):
    if attacker is not None:
        isChecked = True
        check_x, check_y = attacker
        check = f"{check_x}{check_y}"
        print(f"# check: {check}")

    val_pawns, cap_pawns, quiet_pawns = generate_pawn_moves(board)
    val_knights, cap_knights, quiet_knights = generate_knight_moves(board)
    val_bishops, cap_bishops, quiet_bishops = generate_bishop_moves(board)
    val_rooks, cap_rooks, quiet_rooks = generate_rook_moves(board)
    val_queen, cap_queen, quiet_queen = generate_queen_moves(board)
    val_king, cap_king, quiet_king = generate_king_moves(board)

    if val_pawns != []:
        if isChecked:
            for move in val_pawns:
                if move[2:] == check:
                    return move, True
        return val_pawns[0], True
    
    if val_knights != []:
        if isChecked:
            for move in val_knights:
                if move[2:] == check:
                    return move, True
        return val_knights[0], True
    
    if val_bishops != []:
        if isChecked:
            for move in val_bishops:
                if move[2:] == check:
                    return move, True
        return val_bishops[0], True
    
    if val_rooks != []:
        if isChecked:
            for move in val_rooks:
                if move[2:] == check:
                    return move, True
        return val_rooks[0], True
    
    if val_queen != []:
        if isChecked:
            for move in val_queen:
                if move[2:] == check:
                    return move, True
        return val_queen[0], True
    
    if val_king != []:
        if isChecked:
            for move in val_king:
                if move[2:] == check:
                    return move, True
        return val_king[0], True
    
    if cap_pawns != []:
        if isChecked:
            for move in cap_pawns:
                if move[2:] == check:
                    return move, True
        return cap_pawns[0], True
    
    if cap_knights != []:
        if isChecked:
            for move in cap_knights:
                if move[2:] == check:
                    return move, True
        return cap_knights[0], True
    
    if cap_bishops != []:
        if isChecked:
            for move in cap_bishops:
                if move[2:] == check:
                    return move, True
        return cap_bishops[0], True
    
    if cap_rooks != []:
        if isChecked:
            for move in cap_rooks:
                if move[2:] == check:
                    return move, True
        return cap_rooks[0], True
    
    if cap_queen != []:
        if isChecked:
            for move in cap_queen:
                if move[2:] == check:
                    return move, True
        return cap_queen[0], True
    
    if cap_king != []:
        if isChecked:
            for move in cap_king:
                if move[2:] == check:
                    return move, True
        return cap_king[0], True
    
    if quiet_pawns != []:
        return quiet_pawns[0], False
    if quiet_knights != []:
        return quiet_knights[0], False
    if quiet_bishops != []:
        return quiet_bishops[0], False
    if quiet_rooks != []:
        return quiet_rooks[0], False
    if quiet_queen != []:
        return quiet_queen[0], False
    if quiet_king != []:
        return quiet_king[0], False

# ========================
# Main
# ========================

def main():
    board, ping = read_board()
    move_number = ping + 1

    attacker = is_in_check(board)
    print(f"# attacker: {attacker}")

    move, isVal = pick_move(board, attacker)

    if not isVal:
        if as_white:
            move = get_opening_move(queens_gambit, move_number, board)
        elif as_black:
            move = get_opening_move(queens_gambit_black, move_number, board)
        if not is_valid_move(board, move, as_white, ep_cell, castle):
            move, isVal = pick_move(board, attacker)

    print(f"{move} {move_number}")

if __name__ == "__main__":
    main()