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


class QString:
    def __init__(self, maxLen=6):
        self.__max = maxLen
        self.__N = maxLen + 1
        self.__data = [' '] * (maxLen + 1)
        self.__head = 0
        self.__tail = 0
        self.__len = 0

    def __repr__(self):
        return "QueueString: \'{0:s}\'".format(self.__str__())

    def __str__(self):
        if self.__head < self.__tail:
            return "".join(self.__data[self.__head:self.__tail])
        elif self.__head == self.__tail:
            return ""
        else:
            return "".join(self.__data[self.__head:]) + "".join(self.__data[:self.__tail])

    def __len__(self):
        return self.__len

    def put(self, c):
        if type(c) != str or len(c) != 1:
            raise ValueError("must specify 1 char.")
        self.__data[self.__tail] = c
        self.__tail = (self.__tail + 1) % self.__N
        if self.__len < self.__max:
            self.__len += 1
        else:
            self.__head = (self.__head + 1) % self.__N

    def clear(self):
        self.__head = self.__tail
        self.__len = 0

    def rewind(self, count: int):
        self.__head = (self.__head - count) % self.__N
        self.__len = (self.__len + count) % self.__N

    def __eq__(self, other):
        if super.__eq__(self, other):
            return True
        else:
            return self.__str__() == other


class AIPlayer(Player):
    CONST_SCORES = SCORES = [
        (0,       "00000"),
        (1,       "00001"),
        (1,       "10000"),
        (10,      "00010"),
        (10,      "01000"),
        (25,      "00100"),
        (100,     "10001"),
        (250,     "010001"),
        (250,     "100010"),
        (300,     "01001"),
        (300,     "10010"),
        (400,     "10100"),
        (400,     "00101"),
        (500,     "00011"),
        (500,     "11000"),
        (4000,    "01010"),
        (5000,    "00110"),
        (5000,    "01100"),
        (10000,   "11001"),
        (10000,   "10011"),
        (10000,   "10101"),
        (25000,   "011001"),
        (25000,   "110010"),
        (25000,   "010011"),
        (25000,   "100110"),
        (25000,   "010101"),
        (25000,   "101010"),
        (40000,   "01011"),
        (40000,   "10110"),
        (40000,   "01101"),
        (40000,   "11010"),
        (50000,   "00111"),
        (50000,   "11100"),
        (500000,  "01110"),
        (1000000, "10111"),
        (1000000, "11011"),
        (1000000, "11101"),
        (2500000, "010111"),
        (2500000, "101110"),
        (2500000, "011011"),
        (2500000, "110110"),
        (2500000, "011101"),
        (2500000, "111010"),
        (5000000, "01111"),
        (5000000, "11110"),
    ]
    CONST_SCORES.reverse()

    """ a subclass of Player that looks ahead some number of moves and 
    strategically determines its best next move.
    """
    from pa2_gomoku import Board

    def __init__(self, checker, difficulty=1, use_accum=False):
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
        self.__next_x = -1
        self.__next_y = -1
        self.use_accum = use_accum

    def __init_nextMove(self):
        self.__next_x = -1
        self.__next_y = -1

    def __my_max(self, board: Board,
                 depth=0, alpha=float("inf"), beta=float("-inf")):
        # quit condition:
        if depth >= self.depth:
            return self.__evaluate(board)

        for n_row, n_col in board.iter_empty_places():
            if not board.has_neighbor(n_row, n_col):
                continue
            if depth % 2 == 0:
                board.add_checker(self.checker, n_row, n_col)
            else:
                board.add_checker(self.opponent_checker(), n_row, n_col)
            value = -self.__my_max(board, depth+1, -beta, -alpha)
            board.delete_checker(n_row, n_col, undo=False)
            if value > alpha:
                if depth == 0:
                    self.__next_x = n_row
                    self.__next_y = n_col
                if value >= beta:
                    return beta
                alpha = value

        return alpha

    def __evaluate(self, board: Board):
        """
        Evaluate the score of the current board.
        :param board: The board object
        :return: A score, numeric.
        """
        b_width = board.width
        b_height = board.height

        # Whether to use accum version. If self.accum=True, then the function will be faster,
        # If self.accum=False, the function will be slower but can be useful for debugging.
        score_board = None
        score_num = 0
        if not self.use_accum:
            # score_board is used to store scores of each moves
            score_board = [[0 for c in range(b_width)] for r in range(b_height)]

        me = self.checker
        oppo = self.opponent_checker()

        # =======================================
        # we need to scan 4 directions
        # 1. Horizontal scan
        if b_width >= 5:
            for r in range(b_height):
                line = [(r, c, board.slots[r][c]) for c in range(b_width)]
                evals = self.scan(line, me, oppo)
                if not self.use_accum:
                    for _, c, score in evals:
                        score_board[r][c] += score
                else:
                    score_num += evals

        # 2. Vertical Scan
        if b_height >= 5:
            for c in range(b_width):
                line = [(r, c, board.slots[r][c]) for r in range(b_height)]
                evals = self.scan(line, me, oppo)
                if not self.use_accum:
                    for r, _, score in evals:
                        score_board[r][c] += score
                else:
                    score_num += evals

        if b_width >= 5 and b_height >= 5:
            # 3. Diag NW-SE Scan
            for diff in range(5 - b_width, b_height - 5 + 1):  # because of range, we should + 1
                line = []
                for r in range(b_height):
                    c = r - diff
                    if c >= b_width:
                        break
                    if c >= 0:
                        line.append((r, c, board.slots[r][c]))
                evals = self.scan(line, me, oppo)
                if not self.use_accum:
                    for r1, c1, score in evals:
                        score_board[r1][c1] += score
                else:
                    score_num += evals

            # 4. Diag NE-SW Scan
            for diff in range(4, b_width + b_height - 4 + 1):
                line = []
                for r in range(b_height):
                    c = diff - r
                    if c < 0:
                        break
                    if c < b_width:
                        line.append((r, c, board.slots[r][c]))
                evals = self.scan(line, me, oppo)
                if not self.use_accum:
                    for r1, c1, score in evals:
                        score_board[r1][c1] += score
                else:
                    score_num += evals

        # if not self.use_accum, we have one more step to accumulate scores.
        if not self.use_accum:
            score_num = 0
            for r in range(b_height):
                for c in range(b_width):
                    score_num += score_board[r][c]
        return score_num

    @staticmethod
    def match(p: str, offset):
        for score, pattern in AIPlayer.CONST_SCORES:
            if len(pattern) <= len(p):
                pos = p.find(pattern)
                if pos != -1:
                    ans = []
                    for i, c in enumerate(pattern):
                        if c == '1':
                            ans.append(pos + i + offset)
                    return score, ans
        return 0, None

    def scan(self, line: list, p1, p2):
        """
        Scan a line, calculate the score of both player 1 (p1) and player 2 (p2).
        :param line: A list of tuple: (row, col, checker)
        :param p1: Player 1's checker pattern
        :param p2: Player 2's checker pattern
        :return: If accum=False, then an array of the following form: (slot_row, slot_col, slot_score)
                 if True, then return the accumulation of all slot_score.
        """

        # first we assert p1 != p2. if they are the same, the game cannot proceed.
        assert (p1 != p2)
        # cur_check is used to divide strings.
        # When the newly read cur != cur_check (the previous check), then it means a new string is divided.
        cur_check = '\0'
        # cur_pattern is a type of QString. QString is an object which use circular queue to optimize
        # the algorithm.
        cur_pattern = QString(6)
        # ans_map stores the values of each slot.
        ans_map = dict()
        # last_check_id is used when a new string is divided, we use this to check how many blanks we can rewind.
        last_check_id = 0
        # if not has_checker, we won't call match function. This can save time at the begin.
        has_checker = False

        def store(score, elements_id):
            # if score == 0, then elements_id will be None
            if score > 0:
                for eid in elements_id:
                    ans_map.setdefault(eid, score)
                    if score > ans_map[eid]:
                        ans_map[eid] = score

        for i in range(len(line)):
            cur = line[i][2]
            if cur == ' ' or (cur != ' ' and (cur == cur_check or cur_check == '\0')):
                if has_checker and len(cur_pattern) == 6:
                    score, elements_id = AIPlayer.match(str(cur_pattern), i - 6)
                    store(score, elements_id)
                if cur != ' ':
                    cur_check = cur
                    cur_pattern.put('1')
                    last_check_id = i
                    has_checker = True
                else:
                    cur_pattern.put('0')
            else:
                if has_checker and len(cur_pattern) >= 5:
                    score, elements_id = AIPlayer.match(str(cur_pattern), i - len(cur_pattern))
                    store(score, elements_id)
                cur_pattern.clear()
                # we check if both two players can share some blank places
                rewind_nums = i - last_check_id - 1
                if rewind_nums > 0:
                    cur_pattern.rewind(rewind_nums)
                cur_pattern.put('1')
                cur_check = cur
                last_check_id = i
                has_checker = True
        # when loop end, there's still something not handled
        if has_checker and len(cur_pattern) >= 5:
            score, elements_id = AIPlayer.match(str(cur_pattern), len(line) - len(cur_pattern))
            store(score, elements_id)

        if not self.use_accum:
            final_ans_list = []
            for eid, escore in ans_map.items():
                e_row, e_col, e_check = line[eid]
                if e_check == p2:
                    escore *= -1
                final_ans_list.append((e_row, e_col, escore))
            return final_ans_list
        else:
            ret_sum = 0
            for escore in ans_map.values():
                ret_sum += escore
            return ret_sum

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
            self.__next_x = random.randint(-buff_row, buff_row) + cent_row
            self.__next_y = random.randint(-buff_col, buff_col) + cent_col
        else:
            self.__my_max(board)
        return self.__next_x, self.__next_y
        ################### TODO: ######################################
        # Implement your strategy here. 
        # Feel free to call as many as helper functions as you want.
        # We only cares the return of this function
        ################################################################


