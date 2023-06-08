import cv2
import heapq
import numpy as np
from utils import euclidian_distance


def find_sudoku_board(frame):
    """
    F return contour of board square
    :param frame:
    :return:
    """
    height, width = frame.shape[0], frame.shape[1]

    n_largest = 5
    found = False
    board = None

    # resize image
    width_resize = 640
    height_resize = int(width_resize * height / width)
    screen_area = width_resize * height_resize

    scale = width / width_resize
    approx_epsilon = 0.05 * width_resize

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (width_resize, height_resize))

    image = cv2.medianBlur(image, 3)
    edges = cv2.Canny(image, 50, 150)

    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    largest_contours = heapq.nlargest(n_largest, contours, key=cv2.contourArea)

    # selecting such contour that: 1) has 4 vertices, 2) its not in the edge of image, 3) has suitable area,
    # 4) has convex shape, 5) is approximately a square
    for i in range(n_largest):
        approx_contour = cv2.approxPolyDP(largest_contours[i], approx_epsilon, True)
        if approx_contour.shape[0] == 4:
            if 0 not in approx_contour:
                if 0.37 * screen_area < cv2.contourArea(approx_contour) < 0.9 * screen_area:
                    if cv2.isContourConvex(approx_contour):

                        # check if contour is square
                        contour = np.amin(approx_contour, axis=1)
                        contour = contour[contour[:, 1].argsort()]
                        top = contour[0:2]
                        bottom = contour[2:4]
                        top = top[top[:, 0].argsort()]
                        bottom = bottom[bottom[:, 0].argsort()]
                        top_left = top[0]
                        top_right = top[1]
                        bottom_left = bottom[0]
                        bottom_right = bottom[1]
                        top_length = euclidian_distance(top_left, top_right)
                        left_side_length = euclidian_distance(top_left, bottom_left)
                        right_side_length = euclidian_distance(top_right, bottom_right)
                        bottom_length = euclidian_distance(bottom_right, bottom_left)

                        if all(0.95 * top_length < val < 1.05 * top_length for val in
                               (top_length, left_side_length, right_side_length, bottom_length)):

                            found = True
                            board = scale * approx_contour
                            board = board.astype(np.int32)

                            cv2.drawContours(frame, [board], -1, (0, 255, 0), 5)

                            #ret, buffer = cv2.imencode('.jpg', frame)
                            #frame_f = buffer.tobytes()
                            #yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_f + b'\r\n')

                            break


    return found, board
