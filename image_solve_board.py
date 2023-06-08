import cv2
import heapq


def image_solve_board(board, sorted_contours_square, digital_board, sudoku_solved):
    """
    :param board: image of sudoku board
    :param sorted_contours_square: sorted list of contours of squares
    :param digital_board: origin sudoku board as numpy array
    :param sudoku_solved: solved sudoku board as numpy array
    :return: image of a solved board of sudoku
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    board = cv2.cvtColor(board, cv2.COLOR_GRAY2BGR)

    for row in range(9):
        for col in range(9):
            if digital_board[row][col] == 0:
                bottom_point = heapq.nlargest(2, sorted_contours_square[row][col], key=lambda x: x[0][1])
                bottom_point = sorted(bottom_point, key=lambda x: x[0][0])
                left_bottom = bottom_point[0][0]
                right_bottom = bottom_point[1][0]
                height_sq = right_bottom[0] - left_bottom[0]
                shift_right = int(height_sq * 0.2)
                shift_top = int(height_sq * 0.18)
                x_org = left_bottom[0] + shift_right
                y_org = left_bottom[1] - shift_top
                thickness = int(height_sq * 0.04)
                font_scale = round(height_sq * 0.03, 2)

                cv2.putText(board, str(sudoku_solved[row][col]), org=(x_org, y_org),
                            fontFace=font, fontScale=font_scale, color=(0, 255, 0),
                            thickness=thickness, lineType=cv2.LINE_AA)

    return board
