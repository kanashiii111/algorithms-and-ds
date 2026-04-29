import sys
import time

# --- Конфигурация и Фигуры ---
EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING, KING_ENDGAME = 0, 1, 2, 3, 4, 5, 6, 7
INF, MATE_VAL = 10**9, 10**7
TIME_LIMIT = 0.75

# Флаги ходов
MOVE_NORMAL = 0
MOVE_EP = 1
MOVE_CASTLE_S = 2
MOVE_CASTLE_L = 3
MOVE_PROMO = 4
MOVE_DOUBLE = 5

VALS = {PAWN: 100, KNIGHT: 320, BISHOP: 330, ROOK: 500, QUEEN: 900, KING: 20000}

# Весовые таблицы (PST) - значения оставлены без изменений
PST_DATA = {
    PAWN: [
        [0, 0, 0, 0, 0, 0, 0, 0], [5, 10, 10, 12, 12, 10, 10, 5],
        [8, 12, 16, 20, 20, 16, 12, 8], [10, 14, 18, 24, 24, 18, 14, 10],
        [12, 16, 22, 28, 28, 22, 16, 12], [18, 22, 28, 36, 36, 28, 22, 18],
        [30, 35, 40, 50, 50, 40, 35, 30], [0, 0, 0, 0, 0, 0, 0, 0]
    ],
    KNIGHT: [
        [-35, -20, -10, -10, -10, -10, -20, -35], [-20, -5, 5, 8, 8, 5, -5, -20],
        [-10, 8, 12, 16, 16, 12, 8, -10], [-10, 10, 18, 22, 22, 18, 10, -10],
        [-10, 10, 18, 22, 22, 18, 10, -10], [-10, 8, 12, 16, 16, 12, 8, -10],
        [-20, -5, 5, 8, 8, 5, -5, -20], [-35, -20, -10, -10, -10, -10, -20, -35]
    ],
    BISHOP: [
        [-15, -10, -10, -10, -10, -10, -10, -15], [-10, 5, 0, 0, 0, 0, 5, -10],
        [-10, 8, 10, 12, 12, 10, 8, -10], [-10, 8, 12, 16, 16, 12, 8, -10],
        [-10, 8, 12, 16, 16, 12, 8, -10], [-10, 8, 10, 12, 12, 10, 8, -10],
        [-10, 5, 0, 0, 0, 0, 5, -10], [-15, -10, -10, -10, -10, -10, -10, -15]
    ],
    ROOK: [
        [4, 6, 8, 10, 10, 8, 6, 4], [8, 10, 12, 14, 14, 12, 10, 8],
        [0, 2, 4, 8, 8, 4, 2, 0], [0, 2, 4, 8, 8, 4, 2, 0],
        [0, 2, 4, 8, 8, 4, 2, 0], [0, 2, 4, 8, 8, 4, 2, 0],
        [6, 8, 10, 12, 12, 10, 8, 6], [4, 6, 8, 10, 10, 8, 6, 4]
    ],
    QUEEN: [
        [-10, -5, -5, -2, -2, -5, -5, -10], [-5, 0, 2, 4, 4, 2, 0, -5],
        [-5, 2, 6, 8, 8, 6, 2, -5], [-2, 4, 8, 10, 10, 8, 4, -2],
        [-2, 4, 8, 10, 10, 8, 4, -2], [-5, 2, 6, 8, 8, 6, 2, -5],
        [-5, 0, 2, 4, 4, 2, 0, -5], [-10, -5, -5, -2, -2, -5, -5, -10]
    ],
    KING: [
        [-40, -35, -30, -25, -25, -30, -35, -40], [-30, -25, -20, -15, -15, -20, -25, -30],
        [-20, -15, -10, -8, -8, -10, -15, -20], [-10, -8, -5, 0, 0, -5, -8, -10],
        [-10, -8, -5, 0, 0, -5, -8, -10], [-20, -15, -10, -8, -8, -10, -15, -20],
        [-30, -25, -20, -15, -15, -20, -25, -30], [-40, -35, -30, -25, -25, -30, -35, -40]
    ],
    KING_ENDGAME: [
        [-50, -40, -30, -20, -20, -30, -40, -50],
        [-30, -20, -10,   0,   0, -10, -20, -30],
        [-30, -10,  20,  30,  30,  20, -10, -30],
        [-30, -10,  30,  40,  40,  30, -10, -30],
        [-30, -10,  30,  40,  40,  30, -10, -30],
        [-30, -10,  20,  30,  30,  20, -10, -30],
        [-30, -30,   0,   0,   0,   0, -30, -30],
        [-50, -30, -30, -30, -30, -30, -30, -50]
    ]
}

# Вспомогательные данные
VECTORS = {
    KNIGHT: [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
    BISHOP: [(-1, -1), (-1, 1), (1, -1), (1, 1)],
    ROOK: [(-1, 0), (1, 0), (0, -1), (0, 1)],
}
VECTORS[KING] = VECTORS[BISHOP] + VECTORS[ROOK]

# Глобальные кэши
TT, KILLERS, HISTORY = {}, [[None, None] for _ in range(64)], {}
DEADLINE = 0.0

# --- Утилиты ---

def get_phase(board):
    non_pawn_material = 0
    for y in range(8):
        for x in range(8):
            pc = abs(board[y][x])
            if pc in [KNIGHT, BISHOP, ROOK, QUEEN]:
                non_pawn_material += VALS[pc]
    
    return "ENDGAME" if non_pawn_material < 1550 else "MIDGAME"

def is_on_board(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def to_coord(cell):
    return ord(cell[0]) - ord('a'), int(cell[1]) - 1

def from_coord(x, y):
    return f"{chr(ord('a') + x)}{y + 1}"

def format_move(mv):
    x1, y1, x2, y2, flag = mv
    s = from_coord(x1, y1) + from_coord(x2, y2)
    return s + 'q' if flag == MOVE_PROMO else s

def get_hash(state, side):
    board_flat = tuple(item for row in state["board"] for item in row)
    ep = -1 if state["ep"] is None else state["ep"][1] * 8 + state["ep"][0]
    c = state["castle"]
    c_bits = (1 if c[1]["a"] else 0) | (2 if c[1]["h"] else 0) | (4 if c[-1]["a"] else 0) | (8 if c[-1]["h"] else 0)
    return (board_flat, side, ep, c_bits)

# --- Логика движка ---

class ChessEngine:
    @staticmethod
    def is_attacked(board, tx, ty, side):
        # Пешки
        py = ty - side
        for dx in [-1, 1]:
            if is_on_board(tx + dx, py) and board[py][tx + dx] == side * PAWN:
                return True
        # Кони
        for dx, dy in VECTORS[KNIGHT]:
            if is_on_board(tx + dx, ty + dy) and board[ty + dy][tx + dx] == side * KNIGHT:
                return True
        # Скользящие
        for p_type in [BISHOP, ROOK]:
            for dx, dy in VECTORS[p_type]:
                nx, ny = tx + dx, ty + dy
                while is_on_board(nx, ny):
                    pc = board[ny][nx]
                    if pc != EMPTY:
                        if pc == side * p_type or pc == side * QUEEN: return True
                        break
                    nx, ny = nx + dx, ny + dy
        # Король
        for dx, dy in VECTORS[KING]:
            if is_on_board(tx + dx, ty + dy) and board[ty + dy][tx + dx] == side * KING:
                return True
        return False
    
    @staticmethod
    def evaluate(state):
        board = state["board"]
        phase = get_phase(board) ##########
        total = 0
        counts = {1: 0, -1: 0}
        pawn_val = VALS[PAWN] + (20 if phase == "ENDGAME" else 0) ##########
        for y in range(8):
            for x in range(8):
                pc = board[y][x]
                if pc == EMPTY: continue
                side = 1 if pc > 0 else -1
                pt = abs(pc)

                base_val = pawn_val if pt == PAWN else VALS[pt]
                if pt == KING and phase == "ENDGAME":
                    pst_val = PST_DATA[KING_ENDGAME][y][x] if side == 1 else PST_DATA[KING_ENDGAME][7-y][x] #######
                else:
                    pst_val = PST_DATA[pt][y][x] if side == 1 else PST_DATA[pt][7-y][x] #######
                val = base_val + pst_val
                
                # val = pawn_val if pt == PAWN else VALS[pt] + (PST_DATA[pt][y][x] if side == 1 else PST_DATA[pt][7-y][x])
                
                if pt == PAWN:
                    # Проходные
                    is_passed = True
                    enemy_p = -side * PAWN
                    for ny in (range(y+1, 8) if side == 1 else range(y-1, -1, -1)):
                        for fx in [x-1, x, x+1]:
                            if is_on_board(fx, ny) and board[ny][fx] == enemy_p:
                                is_passed = False; break
                    if is_passed: val += 20 + 10 * (y if side == 1 else 7-y)

                if pt == BISHOP: counts[side] += 1
                total += val if side == 1 else -val
        
        if counts[1] >= 2: total += 35
        if counts[-1] >= 2: total -= 35
        
        # Рокировка
        for s in [1, -1]:
            k_pos = None
            for y in range(8):
                for x in range(8):
                    if board[y][x] == s * KING: k_pos = (x, y); break
            if k_pos:
                kx, ky = k_pos
                bonus = 0
                if (kx, ky) in [(6, 0 if s == 1 else 7), (2, 0 if s == 1 else 7)]: bonus = 60
                elif kx == 4: bonus = 10 if (state["castle"][s]["a"] or state["castle"][s]["h"]) else -20
                total += bonus if s == 1 else -bonus
        return total

    @staticmethod
    def get_moves(state, side, caps_only=False):
        board, ep, castle = state["board"], state["ep"], state["castle"]
        mvs = []
        home, promo, start = (0, 7, 1) if side == 1 else (7, 0, 6)
        
        for y in range(8):
            for x in range(8):
                pc = board[y][x]
                if pc * side <= 0: continue
                pt = abs(pc)
                
                if pt == PAWN:
                    ny = y + side
                    if is_on_board(x, ny) and board[ny][x] == EMPTY:
                        if ny == promo: mvs.append((x, y, x, ny, MOVE_PROMO))
                        elif not caps_only:
                            mvs.append((x, y, x, ny, MOVE_NORMAL))
                            if y == start and board[y + 2*side][x] == EMPTY:
                                mvs.append((x, y, x, y + 2*side, MOVE_DOUBLE))
                    for dx in [-1, 1]:
                        nx = x + dx
                        if is_on_board(nx, ny):
                            if board[ny][nx] * side < 0:
                                mvs.append((x, y, nx, ny, MOVE_PROMO if ny == promo else MOVE_NORMAL))
                            elif ep == (nx, ny):
                                mvs.append((x, y, nx, ny, MOVE_EP))
                
                elif pt in [KNIGHT, KING]:
                    for dx, dy in VECTORS[pt]:
                        nx, ny = x + dx, y + dy
                        if is_on_board(nx, ny):
                            target = board[ny][nx]
                            if target * side < 0: mvs.append((x, y, nx, ny, MOVE_NORMAL))
                            elif target == EMPTY and not caps_only: mvs.append((x, y, nx, ny, MOVE_NORMAL))
                    
                    if pt == KING and not caps_only and x == 4 and y == home:
                        if not ChessEngine.is_attacked(board, 4, home, -side):
                            if castle[side]["h"] and board[home][7] == side*ROOK and all(board[home][i] == EMPTY for i in [5, 6]) \
                               and not any(ChessEngine.is_attacked(board, i, home, -side) for i in [5, 6]):
                                mvs.append((4, home, 6, home, MOVE_CASTLE_S))
                            if castle[side]["a"] and board[home][0] == side*ROOK and all(board[home][i] == EMPTY for i in [1, 2, 3]) \
                               and not any(ChessEngine.is_attacked(board, i, home, -side) for i in [2, 3]):
                                mvs.append((4, home, 2, home, MOVE_CASTLE_L))
                
                else: # Sliding pieces
                    for dx, dy in VECTORS[pt if pt != QUEEN else ROOK]: # УБРАТЬ
                        pass 
                    dirs = (VECTORS[BISHOP] if pt == BISHOP else VECTORS[ROOK] if pt == ROOK else VECTORS[BISHOP]+VECTORS[ROOK])
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        while is_on_board(nx, ny):
                            target = board[ny][nx]
                            if target == EMPTY:
                                if not caps_only: mvs.append((x, y, nx, ny, MOVE_NORMAL))
                            else:
                                if target * side < 0: mvs.append((x, y, nx, ny, MOVE_NORMAL))
                                break
                            nx, ny = nx + dx, ny + dy
        return mvs

    @staticmethod
    def apply(state, mv, side):
        x1, y1, x2, y2, flag = mv
        nb = [row[:] for row in state["board"]]
        nc = {1: state["castle"][1].copy(), -1: state["castle"][-1].copy()}
        pc = nb[y1][x1]
        cap = nb[y2][x2]
        nb[y1][x1] = EMPTY
        
        if abs(pc) == KING: nc[side]["a"] = nc[side]["h"] = False
        elif abs(pc) == ROOK:
            h = 0 if side == 1 else 7
            if y1 == h:
                if x1 == 0: nc[side]["a"] = False
                elif x1 == 7: nc[side]["h"] = False
        
        eh = 7 if side == 1 else 0
        if abs(cap) == ROOK and y2 == eh:
            if x2 == 0: nc[-side]["a"] = False
            elif x2 == 7: nc[-side]["h"] = False

        nep = None
        if flag == MOVE_EP:
            nb[y2][x2] = pc; nb[y2-side][x2] = EMPTY
        elif flag == MOVE_CASTLE_S:
            nb[y2][x2] = pc; nb[y2][5] = nb[y2][7]; nb[y2][7] = EMPTY
        elif flag == MOVE_CASTLE_L:
            nb[y2][x2] = pc; nb[y2][3] = nb[y2][0]; nb[y2][0] = EMPTY
        elif flag == MOVE_PROMO: nb[y2][x2] = side * QUEEN
        else:
            nb[y2][x2] = pc
            if abs(pc) == PAWN and abs(y2-y1) == 2: nep = (x1, (y1+y2)//2)
            
        return {"board": nb, "ep": nep, "castle": nc}

# --- Поиск ---

def move_val(state, mv, side, ply, tt_mv):
    if tt_mv == mv: return 10**9
    x1, y1, x2, y2, flag = mv
    s = 0
    victim = abs(state["board"][y2][x2]) if flag != MOVE_EP else PAWN
    atk = abs(state["board"][y1][x1])
    if victim: s = 100000 + 10 * VALS[victim] - VALS[atk]
    if flag == MOVE_PROMO: s += 90000
    if ply < 64:
        if KILLERS[ply][0] == mv: s += 80000
        elif KILLERS[ply][1] == mv: s += 79000
    s += HISTORY.get(mv, 0)
    # Штраф за подставку (move_self_hang_penalty)
    if atk not in [PAWN, KING]:
        child = ChessEngine.apply(state, mv, side)
        if ChessEngine.is_attacked(child["board"], x2, y2, -side):
            defended = ChessEngine.is_attacked(child["board"], x2, y2, side)
            if not defended: s -= VALS[atk] // 2
            elif victim and VALS[atk] > VALS[victim]: s -= (VALS[atk] - VALS[victim]) // 3
    return s

def get_sorted(state, side, ply, tt_mv=None, caps=False):
    mvs = [m for m in ChessEngine.get_moves(state, side, caps) if not ChessEngine.is_attacked(ChessEngine.apply(state, m, side)["board"], *next((x,y) for y in range(8) for x in range(8) if ChessEngine.apply(state, m, side)["board"][y][x] == side*KING), -side)]
    return sorted(mvs, key=lambda m: move_val(state, m, side, ply, tt_mv), reverse=True)

def q_search(state, side, alpha, beta, ply):
    if time.perf_counter() > DEADLINE: raise TimeoutError
    
    in_chk = ChessEngine.is_attacked(state["board"], *next((x,y) for y in range(8) for x in range(8) if state["board"][y][x] == side*KING), -side)
    if not in_chk:
        pat = side * ChessEngine.evaluate(state)
        if pat >= beta: return beta
        if pat > alpha: alpha = pat
    
    mvs = get_sorted(state, side, ply, caps=not in_chk)
    if not mvs: return -MATE_VAL + ply if in_chk else (side * ChessEngine.evaluate(state))
    
    for mv in mvs:
        if not in_chk and state["board"][mv[3]][mv[2]] == EMPTY and mv[4] not in [MOVE_PROMO, MOVE_EP]: continue
        res = -q_search(ChessEngine.apply(state, mv, side), -side, -beta, -alpha, ply + 1)
        if res >= beta: return beta
        if res > alpha: alpha = res
    return alpha

def ab_search(state, side, depth, alpha, beta, ply):
    if time.perf_counter() > DEADLINE: raise TimeoutError
    h_key = get_hash(state, side)
    tt_ent = TT.get(h_key)
    tt_mv = None
    if tt_ent and tt_ent[0] >= depth:
        if tt_ent[1] == 0: return tt_ent[2]
        if tt_ent[1] == 1: alpha = max(alpha, tt_ent[2])
        else: beta = min(beta, tt_ent[2])
        if alpha >= beta: return tt_ent[2]
    if tt_ent: tt_mv = tt_ent[3]

    if depth <= 0: return q_search(state, side, alpha, beta, ply)
    
    mvs = get_sorted(state, side, ply, tt_mv)
    if not mvs:
        return -MATE_VAL + ply if ChessEngine.is_attacked(state["board"], *next((x,y) for y in range(8) for x in range(8) if state["board"][y][x] == side*KING), -side) else 0
    
    best_s, best_m, old_a = -INF, mvs[0], alpha
    for mv in mvs:
        child = ChessEngine.apply(state, mv, side)
        ext = 1 if ChessEngine.is_attacked(child["board"], *next((x,y) for y in range(8) for x in range(8) if child["board"][y][x] == -side*KING), side) else 0
        s = -ab_search(child, -side, depth - 1 + ext, -beta, -alpha, ply + 1)
        if s > best_s: best_s, best_m = s, mv
        alpha = max(alpha, s)
        if alpha >= beta:
            if state["board"][mv[3]][mv[2]] == EMPTY:
                if ply < 64: KILLERS[ply][1], KILLERS[ply][0] = KILLERS[ply][0], mv
                HISTORY[mv] = HISTORY.get(mv, 0) + depth*depth
            break
            
    f = 0 if old_a < best_s < beta else (1 if best_s >= beta else 2)
    TT[h_key] = (depth, f, best_s, best_m)
    return best_s

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

# --- Точка входа ---

def main():
    global DEADLINE
    raw = sys.stdin.read().split()
    if not raw: return
    ptr = 0
    ping = int(raw[ptr]); ptr += 1
    n_pcs = int(raw[ptr]); ptr += 1
    board = [[0]*8 for _ in range(8)]
    my_side = 1
    for i in range(n_pcs):
        cell, color, pt = raw[ptr:ptr+3]; ptr += 3
        x, y = to_coord(cell)
        board[y][x] = int(pt) * (1 if color == '+' else -1)
        if i == 0:
            my_side = 1 if color == '+' else -1
    
    ep_cell = raw[ptr]; ptr += 1
    ep = to_coord(ep_cell) if ep_cell != '-' else None
    
    c_raw = raw[ptr:ptr+4]; ptr += 4
    castle = {1: {"a": c_raw[0] == 'a', "h": c_raw[1] == 'h'}, -1: {"a": c_raw[2] == 'a', "h": c_raw[3] == 'h'}}
    state = {"board": board, "ep": ep, "castle": castle}

    move_number = ping + 1
    if move_number in black.keys():
        move = white[move_number] if my_side == 1 else black[move_number]
        for sorted_move in get_sorted(state, 1, 0):
            formatted = format_move(sorted_move)
            if move == formatted:
                print(f"{move} {ping + 1}")
                print(f"# {move} {ping + 1}")
                return

    DEADLINE = time.perf_counter() + TIME_LIMIT
    best_overall = get_sorted(state, 1, 0)[0]
    print(f"{format_move(best_overall)} {ping+1}", flush=True)
    
    for d in range(1, 64):
        try:
            h_key = get_hash(state, 1)
            tt_ent = TT.get(h_key)
            tt_mv = tt_ent[3] if tt_ent else best_overall
            
            mvs = get_sorted(state, 1, 0, tt_mv)
            best_s, alpha, beta = -INF, -INF, INF
            for mv in mvs:
                child = ChessEngine.apply(state, mv, 1)
                ext = 1 if ChessEngine.is_attacked(child["board"], *next((x,y) for y in range(8) for x in range(8) if child["board"][y][x] == -KING), 1) else 0
                s = -ab_search(child, -1, d-1+ext, -beta, -alpha, 1)
                if s > best_s: best_s, best_overall = s, mv
                alpha = max(alpha, s)
            
            TT[h_key] = (d, 0, best_s, best_overall)
            print(f"{format_move(best_overall)} {ping+1}", flush=True)
        except TimeoutError: break

if __name__ == "__main__":
    main()