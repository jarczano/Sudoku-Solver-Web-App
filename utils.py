import math
import numpy as np
import cv2

def euclidian_distance(point_a, point_b):
    # F return distance between 2 point
    return math.sqrt((point_b[0] - point_a[0]) ** 2 + (point_b[1] - point_a[1]) ** 2)


def sorted_squares(contours_square):
    """
    Function sort list of contours of squares from top left to bottom right
    :param contours_square: list of contours of squares
    :return: sorted list of contours of squares
    """

    mean_coordinates = []
    for j in range(len(contours_square)):
        x_m = np.mean([contours_square[j][k][0][0] for k in range(4)])
        y_m = np.mean([contours_square[j][k][0][1] for k in range(4)])
        mean_coordinates.append([x_m, y_m])

    contours_square_mean = zip(contours_square, mean_coordinates)
    contours_sorted = sorted(contours_square_mean, key=lambda x: x[1][1])
    result = np.zeros((9, 9), dtype=object)
    for i in range(9):
        nine = contours_sorted[i * 9: (i + 1) * 9]
        nine_sorted = sorted(nine, key=lambda x: x[1][0])
        tuples = zip(*nine_sorted)
        coor, mean = [list(tuple) for tuple in tuples]
        result[i, :] = coor
    return result


def protractor(contour):
    """
        F return the angle between top horizontal line of contour and axis ox
    :param contour:
    :return:
    """
    if len(contour) == 4:
        contour = np.amin(contour, axis=1)
        contour = contour[contour[:, 1].argsort()]

        # P1 is point with smaller x value, P2 is point with grater x value
        if contour[0][0] < contour[1][0]:
            x1, y1 = contour[0][0], contour[0][1]
            x2, y2 = contour[1][0], contour[1][1]
        else:
            x1, y1 = contour[1][0], contour[1][1]
            x2, y2 = contour[0][0], contour[0][1]

        if y1 > y2:
            angle = np.arctan((y1 - y2) / (x2 - x1)) * 180 / np.pi
            clockwise = True
        else:
            angle = np.arctan((y2 - y1) / (x2 - x1)) * 180 / np.pi
            clockwise = False

        return (-2 * clockwise + 1) * angle


def divide_contour(contour):
    """
    Function divide big contour whole sudoku board into 81 small squares
    :param contour:
    :return:
    """
    top = contour[0:2]
    bottom = contour[2:4]
    top = top[top[:, 0].argsort()]
    bottom = bottom[bottom[:, 0].argsort()]

    top_left = top[0]
    top_right = top[1]
    bottom_left = bottom[0]
    bottom_right = bottom[1]

    top_partition = [top_left]
    left_partition = [top_left]
    right_partition = [top_right]
    bottom_partition = [bottom_left]

    for part in range(1, 10):
        top_partition.append(top_left + (top_right - top_left) * part / 9)
        left_partition.append(top_left + (bottom_left - top_left) * part / 9)
        right_partition.append(top_right + (bottom_right - top_right) * part / 9)
        bottom_partition.append(bottom_left + (bottom_right - bottom_left) * part / 9)

    point_matrix = np.zeros(shape=(10, 10, 2))
    for row in range(1, 9):
        for col in range(1, 9):
            alfa = (bottom_partition[col][1] - top_partition[col][1]) / (
                    bottom_partition[col][0] - top_partition[col][0])
            beta = top_partition[col][1] - (bottom_partition[col][1] - top_partition[col][1]) / (
                    bottom_partition[col][0] - top_partition[col][0]) * top_partition[col][0]
            gamma = (right_partition[row][1] - left_partition[row][1]) / (
                    right_partition[row][0] - left_partition[row][0])
            delta = left_partition[row][1] - (right_partition[row][1] - left_partition[row][1]) / (
                    right_partition[row][0] - left_partition[row][0]) * left_partition[row][0]

            x_coor = (delta - beta) / (alfa - gamma)
            y_coor = alfa * (delta - beta) / (alfa - gamma) + beta

            corner = np.array([x_coor, y_coor])
            point_matrix[row, col] = corner

    point_matrix[0][::] = np.array(top_partition)
    point_matrix[9][::] = np.array(bottom_partition)

    for row in range(10):
        point_matrix[row][0] = np.array(left_partition)[row]
        point_matrix[row][9] = np.array(right_partition)[row]


    contours_sq = []
    for row in range(9):
        for col in range(9):
            contours_sq.append([point_matrix[row][col], point_matrix[row + 1][col], point_matrix[row][col + 1], point_matrix[row + 1][col + 1]])

    contours_sq = np.array(contours_sq)
    counturs_sq_reshape = []
    for i in range(81):
        counturs_sq_reshape.append(contours_sq[i].reshape(4, 1, 2))
    #counturs_sq_reshape = np.array(counturs_sq_reshape)
    return counturs_sq_reshape


def get_available_cameras():
    num_cameras = 10  # Próba otwarcia maksymalnie 10 kamer

    available_cameras = []

    for i in range(num_cameras):
        camera = cv2.VideoCapture(i)
        if camera.isOpened():
            available_cameras.append(i)
            camera.release()

    return available_cameras
