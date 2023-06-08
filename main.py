import time
from flask_socketio import SocketIO, emit
from flask import Flask, Response, render_template
import cv2
from find_sudoku_board import find_sudoku_board
from split_board import split_board, find_squares
from recognize_board import recognize_board
from sudoku import Sudoku
from image_solve_board import image_solve_board
from utils import get_available_cameras
import copy
import io, base64
import numpy as np


app = Flask(__name__)
socketio = SocketIO(app)


def emit_response(response, image='null'):
    if image != 'null':
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        _, frame_encoded = cv2.imencode(".jpg", image, encode_param)
        processed_img_data = base64.b64encode(frame_encoded).decode()

        b64_src = "data:image/jpg;base64,"
        processed_img_data = b64_src + processed_img_data
    else:
        processed_img_data = 'null'
    emit('response', [str(response), processed_img_data])

@socketio.on("image")
def receive_image(image):
    frame = base64_to_image(image)


    # check image quality to select proper algorithm
    if frame.shape[0] >= 1080 and frame.shape[1] >= 1080:
        high_quality = True
    else:
        high_quality = False
    print('high: ', frame.shape[0], ' width: ', frame.shape[1])
    print("High quality: ", high_quality)

    # Try find the sudoku board on frame
    found = False
    try:
        found, board_contour = find_sudoku_board(frame)
        print("found", found)
    except Exception:
        pass

    if found:
        print('4')
        #print("found")
        if high_quality:
            splited, board_image, contours_sq = find_squares(frame, board_contour)
        else:
            splited, board_image, contours_sq = split_board(frame, board_contour)

        if splited:

            emit_response('recognition', board_image)
            #emit("response", ["recognition", board_image])

            print('5')
            # Recognize the digits entered in the squares
            digital_board = recognize_board(board_image, contours_sq) # można jeszcze w zaleznosci od jakosci

            digital_board_origin = copy.deepcopy(digital_board)

            # Create object Sudoku
            sudoku_read = Sudoku(digital_board)

            sudoku_read.create_board_pos()

            sudoku_read.check_correct()
            print('correct:', sudoku_read.correct)
            if sudoku_read.correct:

                #emit("response", ["solving", 'none'])
                emit_response("solving")

                print('6')
                # Solve sudoku
                sudoku_solved = Sudoku.solve(sudoku_read)
                print('7')
                # Display sudoku solution
                img_solution = image_solve_board(board_image, contours_sq, digital_board_origin, sudoku_solved)

                emit_response("solution", img_solution)
                #emit("response", ["solution", img_solution])
                # tutaj powinno byc drugie else jeżeli nie uda się rozwiązać, ale funkcja solve nie ma wyjscia bezpieczenstaw jezeli sudoku bedzie zjebane zeby nie mielic w nieskonczonosc

            else:
                emit_response("error")
                #emit("response", ["error", 'none'])



@app.route('/')
def index():
    return render_template('index.html')




@socketio.on('connect')
def handle_connect():
    print('Połączono z klientem SocketIO')

@socketio.on('disconnect')
def handle_disconnect():
    print('Rozłączono klienta SocketIO')

def base64_to_image(base64_string):
    # Extract the base64 encoded binary data from the input string
    base64_data = base64_string.split(",")[1]
    # Decode the base64 data to bytes
    image_bytes = base64.b64decode(base64_data)
    # Convert the bytes to numpy array
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    # Decode the numpy array as an image using OpenCV
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host='192.168.1.5', port=5000,
                 ssl_context=('cert.crt', 'private.key'))
    #app.run(debug=True, host='192.168.1.5')

    # 192.168.1.5