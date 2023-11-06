import random
import math

board = {(0, 0): '.', (0, 1): '.', (0, 2): '.',
         (1, 0): '.', (1, 1): '.', (1, 2): '.',
         (2, 0): '.', (2, 1): '.', (2, 2): '.'}
human = 'X'
computer = 'O'


def show(start_info=0):
    cur_board = ''
    for i in range(0, 3):
        for j in range(0, 1):
            cur_board += f"{board[(i, j)]}  |  {board[(i, j + 1)]}  |  {board[(i, j + 2)]}" + '\n'
        if i != 2:
            cur_board += "---+-----+---" + '\n'
    return cur_board


QiPan = show()


def isSuccess(player):
    sign = human if player == 1 else computer
    winning_combinations = [((2, 0), (2, 1), (2, 2)), ((1, 0), (1, 1), (1, 2)), ((0, 0), (0, 1), (0, 2)),
                            ((2, 0), (1, 0), (0, 0)), ((2, 1), (1, 1), (0, 1)), ((2, 2), (1, 2), (0, 2)),
                            ((0, 0), (1, 1), (2, 2)), ((0, 2), (1, 1), (2, 0))]

    for combo in winning_combinations:

        if board[combo[0]] == board[combo[1]] == board[combo[2]] == sign:
            return True

    # if '.' not in board.values():
    #     return 'Tie'

    return False


def noFree():
    if [key for key in board.keys() if board.get(key) == '.']:
        return False
    return True


def minmax_algorithm(depth, alpha, beta, is_maximizing):
    score = {
        'Computer': 1,
        'Tie': 0,
        'Human': -1
    }
    if isSuccess(1):
        return score['Human']
    if isSuccess(2):
        return score['Computer']
    if noFree():
        return score['Tie']

    if is_maximizing:
        best_score = -math.inf
        least_depth = -1
        for index, position in board.items():
            if position == '.':
                board[index] = computer
                current_score = minmax_algorithm(depth + 1, alpha, beta, False)
                board[index] = '.'
                best_score = max(current_score, best_score)
                alpha = max(alpha, current_score)
                if alpha >= beta:
                    break

        return best_score
    else:
        best_score = math.inf
        for index, position in board.items():
            if position == '.':
                board[index] = human
                current_score = minmax_algorithm(depth + 1, alpha, beta, True)
                board[index] = '.'
                best_score = min(current_score, best_score)
                beta = min(beta, current_score)
                if alpha >= beta:
                    break

        return best_score


def best_move():
    best_score = -math.inf
    move = None
    for index, position in board.items():
        if position == '.':
            board[index] = computer
            current_score = minmax_algorithm(0, -math.inf, math.inf, False)
            board[index] = '.'
            if current_score > best_score:
                best_score = current_score
                move = index

    return move


def nextSet(x, y, no):
    """
    功能：玩家no在(x,y)位置下棋
    输入：x,y代表下棋位置，QiPan的行号、列号（0-2），no：玩家编号（1或2）
    输出：是否成功，以及当前下棋位置，如True,[1,2],或False,[-1,-1]
    """
    sign = human if no == 1 else computer
    if board[(x, y)] == ".":
        board[(x, y)] = human if no == 1 else computer
        return True, [x, y]
    else:
        return False, [-1, -1]


def nextFirst(no):
    """
    功能：电脑下棋，采用按顺序第一个空位下棋。
    输入：no：电脑的编号（固定为2）
    输出：是否成功，以及当前下棋位置，如True,[1,2],或False,[-1,-1]
    """
    for i in range(0, 3):
        for j in range(0, 3):
            if board[i, j] == ".":
                board[i, j] = computer
                return True, [i, j]
    return False, [-1, -1]


def nextRandom(no):
    """
    功能：电脑下棋，采用随机下棋。
    输入：no：电脑的编号（固定为2）
    输出：是否成功，以及当前下棋位置，如True,[1,2],或False,[-1,-1]
    """
    positions = [key for key in board.keys() if board.get(key) == '.']
    if positions:
        position = random.choices(positions)
        x, y = position[0]
        board[(x, y)] = computer
        return True, [x, y]
    return False, [-1, -1]
    """
    注：choices返回的时包含一个元素的列表 [(x, y),]
    直接写board[tuple(position)] = computer 的结果会是创建一个新的键值对
    """


def nextSmart(no):
    """
    功能：电脑下棋，智能下棋。
    输入：no：电脑的编号（固定为2）
    输出：是否成功，以及当前下棋位置，如True,[1,2],或False,[-1,-1]
    """
    pass


def nextSuper(no):
    """
    功能：电脑下棋，电脑不败。
    输入：no：电脑的编号（固定为2）
    输出：是否成功，以及当前下棋位置，如True,[1,2],或False,[-1,-1]
    """
    pass


def nextSuperDG(no):
    """
    功能：电脑下棋，电脑无敌。
    输入：no：电脑的编号（固定为2）
    输出：是否成功，以及当前下棋位置，如True,[1,2],或False,[-1,-1]
    """
    position = best_move()
    board[position] = computer
    return True, list(position)


def reset():
    """
    功能：QiPan棋盘复位，全部置为0
    输入：无
    输出：无
    """
    for key in board:
        board[key] = '.'

