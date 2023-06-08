import copy
import numpy as np
import random


class Sudoku:
    def __init__(self, board):
        self.board = board
        self.board_pos = []
        self.solved = False
        self.correct = True

    def check_correct(self):
        """
        function checks if the board is correct at the moment. IThe function checks if no digit is repeated in a row,
        column, or small square.
        :return: change object attribute correct to False if sudoku is incorrect
        """

        # checking if there are unique digits in the row
        for row in self.board:
            row = np.delete(row, row == 0)
            if len(row) != len(np.unique(row)):
                self.correct = False
                break

        # checking if there are unique digits in the column
        for col in range(9):
            col = self.board[:, col]
            col = np.delete(col, col == 0)
            if len(col) != len(np.unique(col)):
                self.correct = False
                break

        # checking if there are unique digits in the small square
        for row in range(3):
            for col in range(3):
                row_from = row * 3
                row_to = (row + 1) * 3
                col_from = col * 3
                col_to = (col + 1) * 3
                square = self.board[row_from:row_to, col_from:col_to].reshape((1, 9))
                square = np.delete(square, square[0] == 0)
                if len(square) != len(np.unique(square)):
                    self.correct = False
                    break

        # checking if is possible to enter any digit for the each field
        for row in range(9):
            for col in range(9):
                if len(self.board_pos[row][col]) == 0:
                    self.correct = False
                    break

    def create_board_pos(self):
        """
        Creates sudoku board of possibilities, where the field is filled there is digit,
        where field is empty there list of possibilities of digits from 1 to 9
        :return: create board_pos attribute for sudoku
        """

        numbers = np.arange(1, 10)
        self.board_pos = np.ones((9, 9), dtype=object)
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    self.board_pos[row][col] = numbers
                else:
                    self.board_pos[row][col] = np.array([self.board[row][col]])

        # plotting out possibilities
        for row in range(9):
            occupied_row = self.board[row]
            for col in range(9):
                if self.board[row][col] == 0:
                    occupied_col = self.board[:, col]
                    row_from = int((row // 3) * 3)
                    row_to = row_from + 3
                    col_from = int((col // 3) * 3)
                    col_to = col_from + 3
                    occupied_sq = self.board[row_from:row_to, col_from:col_to].reshape(1, 9)[0]
                    occupied = np.unique(np.concatenate((occupied_row, occupied_col, occupied_sq)))
                    occupied = np.setdiff1d(occupied, np.array([0]))
                    # assigns each field its possibilities
                    self.board_pos[row][col] = np.setdiff1d(self.board_pos[row][col], occupied)

    def __find_index_numbers(self, row_from, row_to, col_from, col_to):
        """
        Function for a given area, the function returns dictionary where keys are digits that are not yet
        entered in this area of the board, and their values are indices where there are
        :param row_from:
        :param row_to:
        :param col_from:
        :param col_to:
        :return:
        """
        area = self.board[row_from: row_to, col_from: col_to]
        digits = np.arange(1, 10)
        pos_numbers = np.setdiff1d(digits, area)

        index_numbers = {}

        for num in pos_numbers:
            index_numbers[num] = []
            for row in range(row_from, row_to):
                for col in range(col_from, col_to):
                    if sum(np.isin(self.board_pos[row][col], [num])) == 1:
                        index_numbers[num] += [(row, col)]
        return index_numbers

    def __update_board_pos(self, digit, row, col):
        # when we input the digit in board[row][col] then this function update board possibilities
        # delete this digit from row, column and small square

        # delete from row
        for i in range(9):
            if i != col:
                self.board_pos[row][i] = np.setdiff1d(self.board_pos[row][i], [digit]) # nie wiem czy to w [] musi byc

        # delete from column
        for j in range(9):
            if j != row:
                self.board_pos[j][col] = np.setdiff1d(self.board_pos[j][col], [digit])

        # delete from small square
        row_from = int((row // 3) * 3)
        row_to = row_from + 3
        col_from = int((col // 3) * 3)
        col_to = col_from + 3

        for i in range(row_from, row_to):
            for j in range(col_from, col_to):
                if i != row or j != col:
                    self.board_pos[i][j] = np.setdiff1d(self.board_pos[i][j], [digit])

    def only_poss_field(self):
        # checks if for any field is only one possibility, if yes then completes the board

        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0 and len(self.board_pos[row][col]) == 1:
                    self.board[row][col] = self.board_pos[row][col][0]
                    # update the board of possibility
                    self.__update_board_pos(self.board_pos[row][col][0], row, col)

    def only_poss_col(self):
        # checks if for any column some digits could be in only one field, if yes then completes the board

        for row in range(9):
            index_numbers = self.__find_index_numbers(row, row + 1, 0, 9)

            for num in index_numbers:
                if len(index_numbers[num]) == 1:
                    self.board_pos[index_numbers[num][0][0], index_numbers[num][0][1]] = np.array([num])
                    self.board[index_numbers[num][0][0], index_numbers[num][0][1]] = num
                    # update the board of possibility
                    self.__update_board_pos(num, row, index_numbers[num][0][1])

    def only_poss_row(self):
        # checks if for any row some digits could be in only one field, if yes then completes the board
        for col in range(9):
            index_numbers = self.__find_index_numbers(0, 9, col, col + 1)
            for num in index_numbers:
                if len(index_numbers[num]) == 1:
                    self.board_pos[index_numbers[num][0][0], index_numbers[num][0][1]] = np.array([num])
                    self.board[index_numbers[num][0][0], index_numbers[num][0][1]] = num
                    # update the board of possibility
                    self.__update_board_pos(num, index_numbers[num][0][0], col)

    def only_poss_square(self):
        # checks if for any small square some digits could be in only one field, if yes then completes the board
        for row in range(3):
            for col in range(3):
                row_from = row * 3
                row_to = (row + 1) * 3
                col_from = col * 3
                col_to = (col + 1) * 3
                index_numbers = self.__find_index_numbers(row_from, row_to, col_from, col_to)

                for num in index_numbers:
                    if len(index_numbers[num]) == 1:
                        self.board_pos[index_numbers[num][0][0], index_numbers[num][0][1]] = np.array([num])
                        self.board[index_numbers[num][0][0], index_numbers[num][0][1]] = num

                        # update the board of possibility
                        self.__update_board_pos(num, index_numbers[num][0][0], index_numbers[num][0][1])

    def type_random(self):
        # randomly chooses one field with the fewest number of possibilities and randomly
        # chooses the digit for that field

        result = []
        min_len = 9
        for row in range(9):
            for col in range(9):
                if len(self.board_pos[row, col]) > 1:
                    if len(self.board_pos[row, col]) == min_len:
                        result.append((row, col, self.board_pos[row, col]))
                    elif len(self.board_pos[row, col]) < min_len:
                        min_len = len(self.board_pos[row, col])
                        result = [(row, col, self.board_pos[row, col])]

        guess = random.choice(result) # tutaj wywala blad czasami list index out of range
        digit = np.random.choice(guess[2])
        self.board[guess[0], guess[1]] = digit
        self.board_pos[guess[0], guess[1]] = np.array([digit])

        # update the board of possibility
        self.__update_board_pos(digit, guess[0], guess[1])

    def print(self):
        for row in range(9):
            if row == 3 or row == 6:
                print('--------------------------')
            print(self.board[row][0:3], '|', self.board[row][3:6],'|', self.board[row][6:9])
        print('\n')

    def print_board_pos(self):
        for row in range(9):
            for col in range(9):
                print(self.board_pos[row][col], end=' ')
                if col == 8:
                    print('\n')

    def fully(self):
        # return the number of completed fields
        return sum(sum(self.board != 0))

    def number_to_excluded(self):
        # return the number of possibilities which should be eliminated

        exclusion = 0
        for row in self.board_pos:
            for col in row:
                if len(col) != 1:
                    exclusion += len(col) - 1

        if exclusion == 0:
            self.solved = True

        return exclusion

    @staticmethod
    def solve(sudoku):
        sudoku.create_board_pos()
        counter = 0
        while not sudoku.solved:

            b_n_exc = sudoku.number_to_excluded()
            sudoku.only_poss_field()
            a_n_exc = sudoku.number_to_excluded()
            if b_n_exc == a_n_exc:
                sudoku.only_poss_row()
                sudoku.only_poss_col()
                sudoku.only_poss_square()
                a_n_exc = sudoku.number_to_excluded()

                if b_n_exc == a_n_exc:
                    sudoku_copy = copy.deepcopy(sudoku)
                    while not sudoku_copy.solved:

                        b_n_exc = sudoku_copy.number_to_excluded()
                        sudoku_copy.only_poss_field()
                        a_n_exc = sudoku_copy.number_to_excluded()

                        if b_n_exc == a_n_exc:
                            sudoku_copy.only_poss_row()
                            sudoku_copy.only_poss_col()
                            sudoku_copy.only_poss_square()
                            a_n_exc = sudoku_copy.number_to_excluded()

                        sudoku_copy.check_correct()

                        if not sudoku_copy.correct:
                            sudoku_copy = copy.deepcopy(sudoku)
                            counter += 1

                        if b_n_exc == a_n_exc:
                            sudoku_copy.type_random()

                        if sudoku_copy.solved:
                            sudoku = sudoku_copy
        sudoku.only_poss_field()
        return sudoku.board

    @staticmethod
    def solve2(sudoku):
        sudoku.create_board_pos()
        counter = 0
        while not sudoku.solved:

            b_n_exc = sudoku.number_to_excluded()
            sudoku.only_poss_field()
            a_n_exc = sudoku.number_to_excluded()
            if b_n_exc == a_n_exc:
                sudoku.only_poss_row()
                sudoku.only_poss_col()
                sudoku.only_poss_square()
                a_n_exc = sudoku.number_to_excluded()

                if b_n_exc == a_n_exc:
                    sudoku_copy = copy.deepcopy(sudoku)
                    while not sudoku_copy.solved:

                        b_n_exc = sudoku_copy.number_to_excluded()
                        sudoku_copy.only_poss_field()
                        a_n_exc = sudoku_copy.number_to_excluded()

                        if b_n_exc == a_n_exc:
                            sudoku_copy.only_poss_row()
                            sudoku_copy.only_poss_col()
                            sudoku_copy.only_poss_square()
                            a_n_exc = sudoku_copy.number_to_excluded()

                        sudoku_copy.check_correct()

                        if not sudoku_copy.correct:
                            sudoku_copy = copy.deepcopy(sudoku)
                            counter += 1

                        if b_n_exc == a_n_exc:
                            sudoku_copy.type_random()

                        if sudoku_copy.solved:
                            sudoku = sudoku_copy
        sudoku.only_poss_field()
        return sudoku.board
