import cv2
from scipy import ndimage
from utils import protractor, sorted_squares, divide_contour
import numpy as np
import math



def find_squares(frame, board_contour):
    """
        Function divides the board into 81 squares
    :param board: image of sudoku board
    :return: if board could  split into 81 squares: split = True and contours_square a list of contours.
            if board could not split into 81 squares: split = False and contours_square None
    """
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
    #img = board
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

    # print("draw")
    #cv2.drawContours(board, contours, -1, (0, 255, 0), thickness=2)
    #cv2.waitKey(-1)
    # print(contours)
    # selecting such contours that have: 1) suitable area, 2) 4 vertices, 3) convex shape
    for i in range(len(contours)):
        area = round(cv2.contourArea(contours[i], 1))
        if 0.5 * AREA_SQ < area < 1.5 * AREA_SQ:
            if contours[i].shape[0] == 4:
                if cv2.isContourConvex(contours[i]):
                    cv2.drawContours(board, contours, i, (255, 0, 0), thickness=4)


                    #x, y, w, h = cv2.boundingRect(contours[i])
                    #cv2.putText(board, '{} a:{}, p:{}'.format(i, area, contours[i].shape[0]), (x, y + 40), FONT, 0.3, (0,0,255), 1)
                    contours_square.append(contours[i])
    split = True
    #cv2.imshow('frame', board)
    #cv2.waitKey(-1)
    if len(contours_square) != 81:
        split = False
        contours_square = None
    else:
        split = True
        contours_square = sorted_squares(contours_square)

    return split, img, contours_square


def split_board(image, contour):
    """
    f from image return list of contour squares and zoom to board
    :return:
    """
    # to zas chyba trezbe od komentowac
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #path_read = r"test\catch_board3.jpg"
    #image = cv2.imread(str(path_read))
    #found, contour = big_contour(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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
    #contours_sq = contours_sq.reshape((9, 9))
    splited = True

    return splited, zoom_image, contours_sq

