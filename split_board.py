import cv2
from scipy import ndimage
from utils import protractor, sorted_squares, divide_contour
import numpy as np
import math


def find_squares(frame, board_contour):
    """
    Function recognises 81 squares in sudoku board
    :param frame: frame from user camera
    :param board_contour:  contours of sudoku board
    :return: a zoomed-in and straightened image of the Sudoku board, list of 81 contours small square
    """

    # checking at what angle the board is tilted
    angle = protractor(board_contour)
    x, y, w, h = cv2.boundingRect(board_contour)
    board = frame[y:y + h, x:x + w]
    board = ndimage.rotate(board, angle, cval=255)

    HEIGHT, WIDTH = board.shape[0], board.shape[1]
    HEIGHT_SQ = HEIGHT / 9
    WIDTH_SQ = WIDTH / 9
    AREA_SQ = HEIGHT_SQ * WIDTH_SQ

    # image preprocessing
    img = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(img, (7, 7), 0)
    blur = cv2.medianBlur(blur, 5)
    ret, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY_INV)

    # line detection
    lsd = cv2.createLineSegmentDetector(0)
    lines = lsd.detect(img)[0]
    for line in lines:
        x1, y1, x2, y2 = int(line[0][0]), int(line[0][1]), int(line[0][2]), int(line[0][3])
        cv2.line(thresh, (x1, y1), (x2, y2), (255, 0, 0), 4)

    # contours detection
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cv2.approxPolyDP(contour, HEIGHT_SQ * 0.15, True) for contour in contours]
    contours_square = []

    # selecting such contours that have: 1) suitable area, 2) 4 vertices, 3) convex shape
    for i in range(len(contours)):
        area = round(cv2.contourArea(contours[i], 1))
        if 0.5 * AREA_SQ < area < 1.5 * AREA_SQ:
            if contours[i].shape[0] == 4:
                if cv2.isContourConvex(contours[i]):
                    cv2.drawContours(board, contours, i, (255, 0, 0), thickness=4)
                    contours_square.append(contours[i])
    split = True
    if len(contours_square) != 81:
        split = False
        contours_square = None
    else:
        split = True
        contours_square = sorted_squares(contours_square)

    return split, img, contours_square


def split_board(image, contour):
    """
    The function determines a list of contours for all cells based on an equal division of the four edges of the board
    :param image: frame from user camera
    :param contour: contours of sudoku board
    :return: a zoomed-in and straightened image of the Sudoku board, list of 81 contours small square
    """

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # checking at what angle the board is tilted
    angle = protractor(contour)

    contour = np.amin(contour, axis=1)
    contour = contour[contour[:, 1].argsort()]



    # rotate img
    rotate_image = ndimage.rotate(image, angle, cval=0)

    # rotate contour
    rotate_contour = []
    # center coordinate of image
    xs = int(rotate_image.shape[1] / 2)
    ys = int(rotate_image.shape[0] / 2)

    delta_x = int((rotate_image.shape[1] - image.shape[1]) / 2)
    delta_y = int((rotate_image.shape[0] - image.shape[0]) / 2)

    fi = -angle * math.pi / 180

    for point in contour:
        xp, yp = point[0] + delta_x, point[1] + delta_y
        xp_r = int((xp - xs) * math.cos(fi) - (yp - ys) * math.sin(fi) + xs)
        yp_r = int((xp - xs) * math.sin(fi) + (yp - ys) * math.cos(fi) + ys)
        rotate_contour.append([[xp_r, yp_r]])
    rotate_contour = np.array(rotate_contour)

    x, y, w, h = cv2.boundingRect(rotate_contour)
    delta = np.array([x, y])
    zoom_contour = rotate_contour - delta

    zoom_image = rotate_image[y:y+h, x:x+w]

    # crate contours small square
    zoom_contour = np.amin(zoom_contour, axis=1)

    contours_sq = divide_contour(zoom_contour)
    contours_sq = np.array(contours_sq).astype(np.int32)
    contours_sq = contours_sq.reshape((9, 9, 4, 1, 2))
    splited = True

    return splited, zoom_image, contours_sq

