# 
# Programming Assignment 2, CS640
#
# A Gomoku (Gobang) Game
#
# Adapted from CS111
# By Yiwen Gu
#
# The script provides a Gomoku Board class and a Player class
#
# 
import random
import numpy as np
from collections import deque


class Board:
    """ a data type for a Connect Five board with arbitrary dimensions
    """

    def __init__(self, height: int = 10, width: int = 10,
                 checker_p1: str = "X", checker_p2: str = "O"):
        if height <= 0 or width <= 0:
            raise ValueError("height or width should be both greater than 0.")
        # the size of the board
        self.__height = height
        self.__width = width
        # set checker mapping
        self.__checker = [" ", "\0", "\0"]
        self.__chk_map = dict()
        self.set_checkers(checker_p1, checker_p2)
        # a numpy object to store the board
        self.__slots = np.zeros((height, width), dtype=np.int)
        self.__moves_history = deque()

    @property
    def height(self):
        """
        Returns the height of the Board.
        :return: An integer, indicate the value of height.
        """
        return self.__height

    @property
    def width(self):
        """
        Returns the width of the Board.
        :return: An integer, indicate the value of width.
        """
        return self.__width

    @property
    def checker_player1(self):
        return self.__checker[1]

    @property
    def checker_player2(self):
        return self.__checker[2]

    @property
    def slots(self):
        return self.__slots

    def get_checker_id(self, checker: str):
        """
        Get the internal id for specified checker symbol.
        If not found, then `None` will be returned.

        :param checker: A str standing for the checker symbol.
        :return: Integer if found, else `None`.
        """
        if checker in self.__chk_map:
            return self.__chk_map[checker]
        return None

    def set_checkers(self, checker_p1: str, checker_p2: str):
        """
        Set the checker symbol of this Board object. Both symbol should not
        be empty, neither have the same symbol. If you specify some checkers
        symbol with more than 1 characters, a warning message will be outputed.

        :param checker_p1: The symbol of 1st player's checker.
        :param checker_p2: The symbol of 2nd player's checker.
        """
        if checker_p1 == " " or checker_p2 == " ":
            raise ValueError("You cannot specify a checker with space ' ' character.")
        if checker_p1 == checker_p2:
            raise ValueError("You must ensure that two checkers are different.")
        if len(checker_p1) > 1:
            print("checker_p1 = '{0:s}' has more than 1 chars.".format(checker_p1))
        if len(checker_p2) > 2:
            print("checker_p2 = '{0:s}' has more than 1 chars.".format(checker_p2))
        self.__checker[1] = checker_p1
        self.__checker[2] = checker_p2
        self.__chk_map.clear()
        self.__chk_map[checker_p1] = 1
        self.__chk_map[checker_p2] = 2

    def __repr__(self):
        """ Returns a string representation of a Board object.
        """
        # add one row of slots at a time to s
        # this is the optimized version
        s = "\n".join([
            # there is one vertical bar at the start of the row
            "|" + "|".join([self.__checker[self.slots[row, col]]
                            for col in range(self.width)]) + "| " + str(row % 10)
            for row in range(self.height)
        ])
        s += ("\n" + "-" * (self.width * 2 + 3) + "\n ")
        s += " ".join([str(c % 10) for c in range(self.width)])
        s += '\n'
        return s

    def can_add_to(self, row: int, col: int):
        """ returns True if you can add a checker to the specified position 
            (row, col) in the called Board object, and False otherwise.
            input: row, col are integers
        """
        if (col < 0 or col >= self.width) or (row < 0 or row >= self.height):
            return False
        return self.slots[row, col] == 0

    def add_checker(self, checker: str, row: int, col: int):
        """
        adds the specified checker to the column with the specified
        index col in the called Board. The checker must have been
        defined using constructor or :class:`set_checkers` function.

        :param checker: checker which is already defined.
        :param row: row to add the move
        :param col: col to add the move
        """
        if checker not in self.__chk_map:
            raise ValueError("Unexpected checker symbol '{0:s}'".format(checker))

        if self.can_add_to(row, col):
            self.slots[row][col] = self.__chk_map[checker]
            self.__moves_history.append((row, col))

    def add_checker_id(self, checker_id: int, row: int, col: int):
        if checker_id == 1 or checker_id == 2:
            if self.can_add_to(row, col):
                self.slots[row][col] = checker_id
                self.__moves_history.append((row, col))
        else:
            raise ValueError("Invalid checker id {0:d}".format(checker_id))

    def delete_checker(self, row: int, col: int):
        """
        Delete the move from the board.
        :param row: X pos
        :param col: Y pos
        """
        if self.slots[row, col] != 0:
            self.slots[row, col] = 0
            self.__moves_history.pop()

    def reset(self):
        """
        An utility to reset the Board.
        """
        self.slots.fill(0)
        self.__moves_history.clear()

    def is_full(self):
        """
        Return if the board is full of moves.
        :return: True of False, the board is full.
        """
        return np.count_nonzero(self.slots == 0) == 0

    def is_empty(self):
        """
        Return if no players have made a move.
        :return: True of False, the board is empty.
        """
        return np.count_nonzero(self.slots) == 0

    def is_win_for(self, checker: str, row: int, col: int):
        """
        Checks for if the specified checker added to position row, col
        will lead to a win
        :param checker: checker which is already defined.
        :param row: row to add the move
        :param col: col to add the move
        :return: True or False it's win.
        """
        if checker not in self.__chk_map:
            raise ValueError("Unexpected checker symbol '{0:s}'".format(checker))

        checker_id = self.__chk_map[checker]
        return self.__is_horizontal_win(checker_id, row, col) or self.__is_vertical_win(checker_id, row, col) or \
               self.__is_diagonal1_win(checker_id, row, col) or self.__is_diagonal2_win(checker_id, row, col)

    def __is_horizontal_win(self, checker_id: int, row: int, col: int):
        """
        Check when given row and col, if the surrounding contain 5 same checkers.
        Notes: We assume that self.slots[row, col] is already the same!
        :param checker_id: Player's checker_id
        :param row: row
        :param col: col
        :return: True if win, else false.
        """
        cnt = 1
        for i in range(1, 5):
            # Check if the next four columns in this row
            # contain the specified checker.
            if (col + i < self.width) and (self.slots[row, col + i] == checker_id):
                cnt += 1
            else:
                break
        if cnt == 5:
            return True
        else:
            # check towards left           
            for i in range(1, 6 - cnt):
                if (col - i >= 0) and (self.slots[row, col - i] == checker_id):
                    cnt += 1
                else:
                    break
        return cnt == 5

    def __is_vertical_win(self, checker_id: int, row: int, col: int):
        cnt = 1
        for i in range(1, 5):
            # Check if the next four rows in this col
            # contain the specified checker.            
            if (row + i < self.width) and (self.slots[row + i, col] == checker_id):
                cnt += 1
            else:
                break

        if cnt == 5:
            return True
        else:
            # check upwards
            for i in range(1, 6 - cnt):
                if (row - i >= 0) and (self.slots[row - i, col] == checker_id):
                    cnt += 1
                    # print('Vup: ' + str(cnt))
                else:
                    break
        return cnt == 5

    def __is_diagonal1_win(self, checker_id: int, row: int, col: int):
        cnt = 1
        for i in range(1, 5):
            if (row + i < self.height) and (col + i < self.width) and (self.slots[row + i, col + i] == checker_id):
                cnt += 1
                # print('D1: L ' + str(cnt))
            else:
                break
        if cnt == 5:
            return True
        else:
            for i in range(1, 6 - cnt):
                if (row - i >= 0) and (col - i >= 0) and (self.slots[row - i, col - i] == checker_id):
                    cnt += 1
                    # print('D1: R ' + str(cnt))
                else:
                    break
        return cnt == 5

    def __is_diagonal2_win(self, checker_id: int, row: int, col: int):
        cnt = 1
        for i in range(1, 5):
            if (row - i >= 0) and (col + i < self.width) and (self.slots[row - i, col + i] == checker_id):
                cnt += 1
                # print('D2: L ' + str(cnt))
            else:
                break
        if cnt == 5:
            return True
        else:
            for i in range(1, 6 - cnt):
                if (row + i < self.height) and (col - i >= 0) and (self.slots[row + i][col - i] == checker_id):
                    cnt += 1
                    # print('D2: R ' + str(cnt))
                else:
                    break
        return cnt == 5

    def iter_empty(self):
        """
        Get an iterator, contains all places which are empty and can add a new check.
        :return:
        """
        rows, cols = np.where(self.slots == 0)
        for row, col in zip(rows, cols):
            yield row, col

    def iter_recent_empty(self):
        """
        Get an iterator, contains all places which are empty.
        The one who's nearest to the last move will be returned at first.
        :return: An iterator of tuples.
        """
        assert(len(self.__moves_history) > 0)
        cur = self.__moves_history[-1]
        temp = np.zeros((self.height, self.width), dtype=np.int8)
        # BFS search to return tuples
        q = deque()
        q.append(cur)
        temp[cur[0], cur[1]] = 1
        while len(q) > 0:
            cur = q.popleft()
            c_row, c_col = cur
            # up
            if c_row > 0 and temp[c_row - 1, c_col] == 0:
                q.append((c_row - 1, c_col))
                temp[c_row - 1, c_col] = 1
                if self.slots[c_row - 1, c_col] == 0:
                    yield c_row - 1, c_col
            # right
            if c_col < self.width - 1 and temp[c_row, c_col + 1] == 0:
                q.append((c_row, c_col + 1))
                temp[c_row, c_col + 1] = 1
                if self.slots[c_row, c_col + 1] == 0:
                    yield c_row, c_col + 1
            # down
            if c_row < self.height - 1 and temp[c_row + 1, c_col] == 0:
                q.append((c_row + 1, c_col))
                temp[c_row + 1, c_col] = 1
                if self.slots[c_row + 1, c_col] == 0:
                    yield c_row + 1, c_col
            # left
            if c_col > 0 and temp[c_row, c_col - 1] == 0:
                q.append((c_row, c_col - 1))
                temp[c_row, c_col - 1] = 1
                if self.slots[c_row, c_col - 1] == 0:
                    yield c_row, c_col - 1

    def has_neighbor(self, row: int, col: int):
        """
        An utility to test whether a place, has neighbor moves.
        :param row: The index of row
        :param col: The index of column
        :return: Return True if has at least a neighbor move, or else, False.
        """
        lower_row = max(0, row - 1)
        upper_row = min(self.height, row + 2)
        lower_col = max(0, col - 1)
        upper_col = min(self.height, col + 2)
        sliced = self.slots[lower_row:upper_row, lower_col:upper_col]
        sliced[row-lower_row, col-lower_col] = 0
        return np.count_nonzero(sliced) > 0


###### test case #############

# b1 = Board(13,13)

# b1.add_checker('X', 0, 5)
# b1.add_checker('O', 4, 7)

# b1.add_checker('X', 0, 4)
# b1.add_checker('X', 0, 6)
# b1.add_checker('X', 0, 7)
# b1.add_checker('X', 0, 8)

# b1.add_checker('O', 5, 8)
# b1.add_checker('O', 6, 9)
# b1.add_checker('O', 3, 6)
# b1.add_checker('O', 2, 5)

# b1.add_checker('X', 1, 5)
# b1.add_checker('X', 2, 5)
# b1.add_checker('X', 3, 5)
# b1.add_checker('X', 4, 5)

# b1.add_checker('X', 7, 1)
# b1.add_checker('X', 6, 1)
# b1.add_checker('X', 5, 1)
# b1.add_checker('X', 3, 1)
# b1.add_checker('X', 4, 1)

# b1.add_checker('O', 1, 6)
# b1.add_checker('O', 0, 7)
# b1.add_checker('O', 3, 4)
# b1.add_checker('O', 4, 3)
# b1.add_checker('O', 5, 2)
# print(b1)
# assert(b1.is_win_for('O', 5, 2))

# b2 = Board(2,2)
# b2.add_checker("X", 0,0)
# b2.add_checker("X", 1,0)
# b2.add_checker("X", 1,1)
# b2.add_checker("X", 0,1)
# print(b2)
# b2.is_full()
# b2.reset()
# print(b2)
# b2.is_full()

##############################


class Player:
    def __init__(self, checker: str):
        self.__chk = self.__opp = '\0'
        self.checker = checker
        self.num_moves = 0

    def __repr__(self):
        return "Player: {0:s}".format(self.checker)

    @property
    def checker(self):
        return self.__chk

    @checker.setter
    def checker(self, new: str):
        if not (new == 'X' or new == 'O'):
            raise ValueError("checker can only be 'X' or 'O'")
        self.__chk = new
        self.__opp = 'O' if new == 'X' else 'X'

    @property
    def opponent_checker(self):
        return self.__opp

    def next_move(self, board):
        """ gets and returns the called Player's next move for a game on
            the specified Board object. The method ensures that the move
            is valid for the specified Board -- asking repeatedly if
            necessary until the human player enters a valid move.
            input: board is a Board object for the game that the called
                     Player is playing.
        """
        self.num_moves += 1

        while True:
            pos_str = input('Enter a position: ')
            pos_lst = pos_str.strip().split()
            if board.can_add_to(int(pos_lst[0]), int(pos_lst[1])):
                return int(pos_lst[0]), int(pos_lst[1])
            else:
                print('Try again!')


class RandomPlayer(Player):
    """ a subclass of Player that chooses at random
        from the available position.
    """

    def next_move(self, board):
        """ returns the called RandomPlayer's next move for a game on
            the specified Board object. The method chooses at random
            from the columns that are not yet full, and we assume 
            that there is at least one such column.
            input: board is a Board object for the game that the called
                   Player is playing.
        """
        assert (not board.is_full())
        self.num_moves += 1
        open_pos = list(board.iter_empty())
        return random.choice(open_pos)

#### test case #####
# p1 = Player('X')
# move = p1.next_move(b1)
# print('Player ' + p1.checker + ' places a checker at position ' + str(move))
# p2 = RandomPlayer('O')
# move = p2.next_move(b1)
# print('Player ' + p2.checker + ' places a checker at position ' + str(move))
# b1.add_checker(p2.checker, move[0], move[1])
# print(b1)

####################
