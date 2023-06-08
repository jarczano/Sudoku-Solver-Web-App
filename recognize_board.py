import numpy as np
import cv2
from keras.models import load_model


def recognize_board(board, sorted_split_board):
    """
    :param board: image of sudoku board
    :param sorted_split_board: list of sorting contour squares from top left to bottom right
    :return: digital sudoku board as numpy array
    """

    model_binary = load_model(r'model\model_binary1685438852.1508806.h5')
    model = load_model(r'model\model1685450577.378637.h5')
    digital_board = np.zeros((9, 9), dtype=np.uint8)

    # tutaj lepiej by bylo najpierw tresholdy i blury dla calego zdjecia
    for i in range(9):
        for j in range(9):
            x, y, w, h = cv2.boundingRect(sorted_split_board[i][j])
            margin_top_bottom, margin_left_right = int(0.1 * h), int(0.1 * w)
            #one_square = board[y + margin_top_bottom: y + h - margin_top_bottom, x + margin_left_right: x + w - margin_left_right] # to bardziej sie nadaje tylko dla niskiej rozdzielczosci

            one_square = board[y: y + h, x: x + w]
            #print("one square", one_square)
            one_square = cv2.resize(one_square, (28, 28))
            one_square = 255 - one_square
            one_square = one_square / 255
            _, one_square = cv2.threshold(one_square, 150/255, 250/255, cv2.THRESH_BINARY)
            one_square = cv2.blur(one_square, (2, 2)) # mozew []

            one_square = one_square.reshape(1, 28, 28, 1)

            # if empty or digit
            prediction_binary = np.argmax(model_binary.predict(one_square), axis=1)
            if prediction_binary[0] == 0:
                # tutaj 2 razy robi prediction
                prediction = np.argmax(model.predict(one_square), axis=1)[0] + 1
                #max_probability = model.predict(one_square)[0][prediction]
                #if max_probability > 0.4:
                digital_board[i][j] = prediction
                #print("Prediction: ", prediction)

    return digital_board

