# 
# Programming Assignment 2, CS640
#
# A Gomoku (Gobang) Game
#
# Adapted from CS111
# By Yiwen Gu
#
# You need to implement an AI Player for Gomoku
# A Random Player is provided for you
# 
#

from pa2_gomoku import Player
import random
# numpy is used to accelerate matrix computing
import numpy as np


FIVE = 7
FOUR = 6
THREE = 4
TWO = 2
SFOUR = 5
STHREE = 3
STWO = 1


class AIPlayer(Player):
    """ a subclass of Player that looks ahead some number of moves and 
    strategically determines its best next move.
    """
    from pa2_gomoku import Board

    def __init__(self, checker, difficulty=1, use_accum=True):
        """
        :param checker: This player's checker symbol
        :param difficulty: specify difficulty
        :param use_accum: Specify when calculating internally, whether the function should use
                   accumulate intermediate values. instead of values w.r.t each single slots.
        """
        super().__init__(checker)
        depth = 0
        seconds = -1
        assert (difficulty >= 0)
        difficulty = int(difficulty)

        if difficulty == 0:  # level 0: 1-depth
            depth = 1
        elif difficulty == 1:  # level 1: 3-depth
            depth = 3
        elif difficulty == 2:  # level 2: 7-depth
            depth = 7
        elif difficulty == 3:  # level 3: think 1 seconds
            seconds = 1
        else:
            seconds = pow(2, difficulty - 3)
        self.depth = depth
        self.seconds = seconds
        self.__next_moves = []
        self.use_accum = use_accum
        self.__temp_record = None

    def __init_nextMove(self):
        self.__next_moves.clear()

    def next_move(self, board: Board):
        """ returns the called AIPlayer's next move for a game on
            the specified Board object.
            input: board is a Board object for the game that the called
                     Player is playing.
            return: row, col are the coordinated of a vacant location on the board
        """
        assert (not board.is_full())
        assert (self.depth % 2 == 1)

        self.num_moves += 1
        self.__init_nextMove()
        if board.is_empty():
            # if it's the 1st move, and it's AI's turn
            # then ai will randomly choose one in the center of the board.
            cent_row = board.width // 2
            cent_col = board.height // 2
            buff_row = round(board.width / 20)
            buff_col = round(board.width / 20)
            self.__next_moves.append(
                (random.randint(-buff_row, buff_row) + cent_row,
                 random.randint(-buff_col, buff_col) + cent_col))
        else:
            self.__temp_record = np.zeros((board.height, board.width, 4), dtype=np.bool)
            self.__my_max(board)
        row, col = random.choice(self.__next_moves)
        return row, col
        ################################################################
        # Implement your strategy here.
        # Feel free to call as many as helper functions as you want.
        # We only cares the return of this function
        ################################################################

    def __my_max(self, board: Board,
                 depth=0, alpha=float("-inf"), beta=float("inf")):
        # quit condition:
        if depth >= self.depth:
            return self.__evaluate(board)

        me_chk_id = board.get_checker_id(self.checker)
        op_chk_id = board.get_checker_id(self.opponent_checker)
        for n_row, n_col in board.iter_recent_empty():
            if not board.has_neighbor(n_row, n_col):  # TODO: this step can also be optimized!
                continue
            if depth % 2 == 0:
                board.add_checker_id(me_chk_id, n_row, n_col)
            else:
                board.add_checker_id(op_chk_id, n_row, n_col)
            value = -self.__my_max(board, depth + 1, -beta, -alpha)
            board.delete_checker(n_row, n_col)
            if value > alpha:
                if depth == 0:
                    self.__next_moves.clear()
                    self.__next_moves.append((n_row, n_col))
                if value >= beta:
                    return beta
                alpha = value
            elif value == alpha:
                if depth == 0:
                    self.__next_moves.append((n_row, n_col))

        return alpha

    def __calc_score(self, score_count: dict, me_chk_id: int, op_chk_id: int):
        """
        :param score_count:
        :param me_chk_id:
        :param op_chk_id:
        :return:
        """
        my_count = score_count[me_chk_id]
        oppo_count = score_count[op_chk_id]
        if oppo_count[FIVE] > 0:
            return -10000
        if my_count[FIVE] > 0:
            return 10000

        if my_count[SFOUR] >= 2:
            my_count[FOUR] += 1
        if oppo_count[SFOUR] >= 2:
            oppo_count[FOUR] += 1

        if oppo_count[FOUR] > 0:
            return -9050
        if oppo_count[SFOUR] > 0:
            return -9040
        if my_count[FOUR] > 0:
            return 9030
        if my_count[SFOUR] > 0 and my_count[THREE] > 0:
            return 9020

        if oppo_count[THREE] > 0 and my_count[SFOUR] == 0:
            return -9010

        if my_count[THREE] > 1 and oppo_count[THREE] == 0 and oppo_count[STHREE] == 0:
            return 9000

        my_score = op_score = 0
        if my_count[SFOUR] > 0:
            my_score += 400

        if oppo_count[THREE] > 1:
            op_score += 500
        elif oppo_count[THREE] > 0:
            op_score += 100

        if my_count[THREE] > 1:
            my_score += 2000
        elif my_count[THREE] > 0:
            my_score += 400

        if oppo_count[STHREE] > 0:
            op_score += oppo_count[STHREE] * 10
        if my_count[STHREE] > 0:
            my_score += my_count[STHREE] * 10

        if oppo_count[TWO] > 0:
            op_score += oppo_count[TWO] * 6
        if my_count[TWO] > 0:
            my_score += my_count[TWO] * 6

        if oppo_count[STWO] > 0:
            op_score += oppo_count[STWO] * 2
        if my_count[STWO] > 0:
            my_score += my_count[STWO] * 2

        return my_score - op_score

    def __evaluate(self, board: Board):
        """
        Evaluate the score of the current board.
        :param board: The board object
        :return: A score, numeric.
        """
        assert (self.__temp_record is not None)
        self.__temp_record.fill(0)
        # score_board has 3 dims: row, col, and 4 different directions.
        me_chk_id = board.get_checker_id(self.checker)
        op_chk_id = board.get_checker_id(self.opponent_checker)

        score_count = {me_chk_id: [0] * 8, op_chk_id: [0] * 8}

        # we only iterate slots which has been used
        nz = board.slots != 0
        rows, cols = np.where(nz)

        for row, col in zip(rows, cols):
            if board.slots[row, col] == me_chk_id:
                self.__check_point(board, row, col, score_count)
            else:
                self.__check_point(board, row, col, score_count)
        return self.__calc_score(score_count, me_chk_id, op_chk_id)

    def __check_point(self, board: Board, row: int, col: int, score_count: dict):
        b_width = board.width
        b_height = board.height

        # mostly left, top, right, bottom edge
        col_lower = max(0, col - 4)
        col_upper = min(b_width - 1, col + 4)
        row_lower = max(0, row - 4)
        row_upper = min(b_height - 1, row + 4)

        my_record = self.__temp_record[row, col]
        # direction (1, 0)
        if b_width >= 5 and my_record[0] == 0:
            indices = (row, range(col_lower, col_upper + 1))
            self.__scan(board, indices, col - col_lower, score_count, 0)
        # direction (0, 1)
        if b_height >= 5 and my_record[1] == 0:
            indices = (range(row_lower, row_upper + 1), col)
            self.__scan(board, indices, row - row_lower, score_count, 1)
        if b_width >= 5 and b_height >= 5:
            # direction (1, 1)
            if my_record[2] == 0:
                offset = col - row
                row_bgn = max(row_lower, -offset)
                row_end = min(row_upper, b_width - offset - 1)
                indices = (range(row_bgn, row_end + 1), range(row_bgn + offset, row_end + offset + 1))
                self.__scan(board, indices, row - row_bgn, score_count, 2)

            # direction (1, -1)
            if my_record[3] == 0:
                offset = col + row
                row_bgn = max(row_lower, offset - b_width + 1)
                row_end = min(row_upper, offset)
                indices = (range(row_bgn, row_end + 1), range(offset - row_bgn, offset - row_end - 1, -1))
                self.__scan(board, indices, row - row_bgn, score_count, 3)

    def __scan(self, board: Board, indices, self_idx, score_count: dict, direction: int):
        line = board.slots[indices]
        me_chk_id = line[self_idx]

        len_line = len(line)
        # initialize the left_idx and right_idx
        left_idx = self_idx - 1
        right_idx = self_idx + 1
        while right_idx < len_line:
            if line[right_idx] != me_chk_id:
                break
            right_idx += 1
        right_idx -= 1
        while left_idx >= 0:
            if line[left_idx] != me_chk_id:
                break
            left_idx -= 1
        left_idx += 1
        # how many are the same as the self slot.
        me_range = right_idx - left_idx + 1

        # initialize the left_range and right_range
        left_range = left_idx - 1
        right_range = right_idx + 1
        while right_range < len_line:
            if line[right_range] != 0:
                break
            right_range += 1
        right_range -= 1
        while left_range >= 0:
            if line[left_range] != 0:
                break
            left_range -= 1
        left_range += 1
        # how many are available slots
        chess_range = right_range - left_range + 1

        self.__set_record(indices, left_idx, right_idx, direction)
        if me_range == 5:
            score_count[me_chk_id][FIVE] += 1

        # Live Four : XMMMMX
        # Incoming Four : XMMMMP, PMMMMX
        elif me_range == 4:
            left_empty = (left_idx > 1 and line[left_idx - 1] == 0)
            right_empty = (right_idx < len_line - 1 and line[right_idx + 1] == 0)
            if left_empty and right_empty:
                score_count[me_chk_id][FOUR] += 1
            elif left_empty or right_empty:
                score_count[me_chk_id][SFOUR] += 1

        # Incoming Four : MXMMM, MMMXM, the two types can both exist
        # Live Three : XMMMXX, XXMMMX
        # Sleep Three : PMMMX, XMMMP, PXMMMXP
        elif me_range == 3:
            left_empty = right_empty = left_four = right_four = False
            if left_idx > 1 and line[left_idx - 1] == 0:
                if left_idx > 2 and line[left_idx - 2] == me_chk_id:  # MXMMM
                    self.__set_record(indices, left_idx - 2, left_idx - 1, direction)
                    left_four = True
                left_empty = True

            if right_idx < len_line - 1 and line[right_idx + 1] == 0:
                if right_idx < len_line - 2 and line[right_idx + 2] == me_chk_id:  # MMMXM
                    self.__set_record(indices, right_idx + 1, right_idx + 2, direction)
                    right_four = True
                right_empty = True

            if left_four or right_four:
                score_count[me_chk_id][SFOUR] += 1
            elif left_empty and right_empty:
                if chess_range > 5:  # XMMMXX, XXMMMX
                    score_count[me_chk_id][THREE] += 1
                else:  # PXMMMXP
                    score_count[me_chk_id][STHREE] += 1
            elif left_empty or right_empty:  # PMMMX, XMMMP
                score_count[me_chk_id][STHREE] += 1

        # Incoming Four: MMXMM, only check right direction
        # Live Three: XMXMMX, XMMXMX the two types can both exist
        # Slept Three: PMXMMX, XMXMMP, PMMXMX, XMMXMP
        # Live Two: XMMX
        # Slept Two: PMMX, XMMP
        elif me_range == 2:
            left_empty = left_three = right_three = False
            right_empty = right_idx < len_line - 1 and line[right_idx + 1] == 0
            if left_idx > 1 and line[left_idx - 1] == 0:
                if left_idx > 2 and line[left_idx - 2] == me_chk_id:
                    self.__set_record(indices, left_idx - 2, left_idx - 1, direction)
                    has_left_3 = left_idx > 3
                    if has_left_3 and line[left_idx - 3] == 0:
                        if right_empty:  # XMXMMX
                            score_count[me_chk_id][THREE] += 1
                        else:  # XMXMMP
                            score_count[me_chk_id][STHREE] += 1
                        left_three = True
                    elif not has_left_3 or line[left_idx - 3] != me_chk_id:  # PMXMMX
                        if right_empty:
                            score_count[me_chk_id][STHREE] += 1
                            left_three = True
                left_empty = True

            if right_empty:
                if right_idx < len_line - 2 and line[right_idx + 2] == me_chk_id:
                    has_right_3 = right_idx < len_line - 3
                    if has_right_3 and line[right_idx + 3] == me_chk_id:  # MMXMM
                        self.__set_record(indices, right_idx + 1, right_idx + 2, direction)
                        score_count[me_chk_id][SFOUR] += 1
                        right_three = True
                    elif has_right_3 and line[right_idx + 3] == 0:
                        # setRecord(self, x, y, right_idx+1, right_idx+2, dir_index, dir)
                        if left_empty:  # XMMXMX
                            score_count[me_chk_id][THREE] += 1
                        else:  # PMMXMX
                            score_count[me_chk_id][STHREE] += 1
                        right_three = True
                    elif left_empty:  # XMMXMP
                        score_count[me_chk_id][STHREE] += 1
                        right_three = True

            if left_three or right_three:
                pass
            elif left_empty and right_empty:  # XMMX
                score_count[me_chk_id][TWO] += 1
            elif left_empty or right_empty:  # PMMX, XMMP
                score_count[me_chk_id][STWO] += 1

        # Live Two: XMXMX, XMXXMX only check right direction
        # Slept Two: PMXMX, XMXMP
        elif me_range == 1:
            left_empty = False
            has_right_1 = right_idx < len_line - 1
            right_empty = has_right_1 and line[right_idx + 1] == 0
            if left_idx > 1 and line[left_idx - 1] == 0:
                if left_idx > 2 and line[left_idx - 2] == me_chk_id:
                    if left_idx > 3 and line[left_idx - 3] == 0:
                        if right_empty:
                            pass
                        elif not has_right_1 or line[right_idx + 1] != me_chk_id:  # XMXMP
                            score_count[me_chk_id][STWO] += 1
                left_empty = True

            if right_empty:
                if right_idx < len_line - 2:
                    if line[right_idx + 2] == me_chk_id:
                        if right_idx < len_line - 3 and line[right_idx + 3] == 0:
                            if left_empty:  # XMXMX
                                # setRecord(self, x, y, left_idx, right_idx+2, dir_index, dir)
                                score_count[me_chk_id][TWO] += 1
                            else:  # PMXMX
                                score_count[me_chk_id][STWO] += 1
                    elif line[right_idx + 2] == 0:
                        if right_idx < len_line - 4 and line[right_idx + 3] == me_chk_id and line[right_idx + 4] == 0:
                            # XMXXMX
                            score_count[me_chk_id][TWO] += 1

    def __set_record(self, indices, left: int, right: int, direction: int):
        assert (type(indices) == tuple)
        tr, tc = indices
        new_tr = self.__filter_range(tr, left, right) if type(tr) == range else tr
        new_tc = self.__filter_range(tc, left, right) if type(tc) == range else tc
        self.__temp_record[new_tr, new_tc, direction] = 1

    def __filter_range(self, r: range, left: int, right: int):
        step = r.step
        if r.step is None:
            step = 1
        if step > 0:
            return range(r[left], r[right] + 1, step)
        elif step < 0:
            return range(r[left], r[right] - 1, step)