import copy
import math
import random

X = "X"
O = "O"
EMPTY = None


def initial_state():
    return [[EMPTY for _ in range(4)] for _ in range(4)]


def player(board):
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    return X if x_count == o_count else O


def actions(board):
    return {(i, j) for i in range(4) for j in range(4) if board[i][j] == EMPTY}


def result(board, action):
    i, j = action
    if board[i][j] is not EMPTY:
        raise ValueError("Invalid Action: Cell is already occupied")
    new_board = copy.deepcopy(board)
    new_board[i][j] = player(board)
    return new_board


def winner(board):
    for row in board:
        if row.count(row[0]) == 4 and row[0] is not EMPTY:
            return row[0]

    for col in range(4):
        column = [board[row][col] for row in range(4)]
        if column.count(column[0]) == 4 and column[0] is not EMPTY:
            return column[0]

    if all(board[i][i] == board[0][0] and board[i][i] is not EMPTY for i in range(4)):
        return board[0][0]

    if all(board[i][3 - i] == board[0][3] and board[i][3 - i] is not EMPTY for i in range(4)):
        return board[0][3]

    return None


def terminal(board):
    return winner(board) is not None or all(EMPTY not in row for row in board)


def utility(board):
    w = winner(board)
    return 1 if w == X else -1 if w == O else 0


def minimax(board, difficulty="medium"):
    """
    Returns the optimal action for the current player on the board.
    Difficulty levels:
    - easy: Makes random moves with 70% probability, otherwise makes optimal moves with depth limit 1
    - medium: Makes optimal moves with depth limit 2
    - hard: Makes optimal moves with depth limit 4
    """
    if terminal(board):
        return None

    current_player = player(board)
    available_actions = list(actions(board))
    
    # Easy difficulty: 70% random moves, 30% smart moves with depth 1
    if difficulty == "easy":
        if random.random() < 0.7:
            return random.choice(available_actions)
        depth_limit = 1
    # Medium difficulty: optimal moves with depth 2
    elif difficulty == "medium":
        depth_limit = 2
    # Hard difficulty: optimal moves with depth 4
    else: 
        depth_limit = 4

    if current_player == X:
        value, best_action = max_value(board, -math.inf, math.inf, depth_limit)
    else:
        value, best_action = min_value(board, -math.inf, math.inf, depth_limit)

    return best_action

def max_value(board, alpha, beta, depth):
    if terminal(board) or depth == 0:
        return utility(board), None

    max_eval = -math.inf
    best_action = None
    for action in actions(board):
        eval, _ = min_value(result(board, action), alpha, beta, depth - 1)
        if eval > max_eval:
            max_eval = eval
            best_action = action
        if max_eval >= beta:
            break
        alpha = max(alpha, max_eval)

    return max_eval, best_action


def min_value(board, alpha, beta, depth):
    if terminal(board) or depth == 0:
        return utility(board), None

    min_eval = math.inf
    best_action = None
    for action in actions(board):
        eval, _ = max_value(result(board, action), alpha, beta, depth - 1)
        if eval < min_eval:
            min_eval = eval
            best_action = action
        if min_eval <= alpha:
            break
        beta = min(beta, min_eval)

    return min_eval, best_action