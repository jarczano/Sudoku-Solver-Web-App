from flask_socketio import SocketIO, emit
from flask import Flask, render_template
import cv2
import copy
import base64

from app.find_sudoku_board import find_sudoku_board
from app.split_board import split_board, find_squares
from app.recognize_board import recognize_board
from app.sudoku import Sudoku
from app.image_solve_board import image_solve_board
from app.utils import base64_to_image, get_ipv4_address


app = Flask(__name__)
socketio = SocketIO(app)


def emit_response(response, image='null'):
    """
    Function sends a response to the server
    :param response: one of the stage "recognition", "solving", "error", "solution"
    :param image: Image of found sudoku board or image of the solved sudoku board
    :return: emit response to the server
    """
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
    """
    The function receives an image from the client's camera. It recognizes the Sudoku puzzle,
    solves it, and sends the response back to the server.
    :param image: image from camera
    :return: sends the response back to the server
    """

    frame = base64_to_image(image)

    # Check image quality to select proper algorithm
    if frame.shape[0] >= 1080 and frame.shape[1] >= 1080:
        high_quality = True
    else:
        high_quality = False
    print('High frame: ', frame.shape[0], ' Width frame: ', frame.shape[1])

    # Try find the sudoku board on frame
    found = False
    try:
        found, board_contour = find_sudoku_board(frame)
        print("Found: ", found)
    except Exception:
        pass

    if found:

        # Divides sudoku boards into 81 individual fields
        if high_quality:
            splited, board_image, contours_sq = find_squares(frame, board_contour)
        else:
            splited, board_image, contours_sq = split_board(frame, board_contour)
        print("Board splited: ", splited)

        if splited:

            emit_response('recognition', board_image)

            # Recognize the digits entered in the squares
            digital_board = recognize_board(board_image, contours_sq)

            digital_board_origin = copy.deepcopy(digital_board)

            # Create object Sudoku
            sudoku_read = Sudoku(digital_board)

            sudoku_read.create_board_pos()

            sudoku_read.check_correct()
            print('Sudoku correct:', sudoku_read.correct)
            if sudoku_read.correct:

                emit_response("solving")

                # Solve sudoku
                success, sudoku_solved = Sudoku.solve(sudoku_read)

                if success:
                    # Display sudoku solution
                    img_solution = image_solve_board(board_image, contours_sq, digital_board_origin, sudoku_solved)
                    emit_response("solution", img_solution)
                else:
                    emit_response("error")
            else:
                emit_response("error")


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print('Connect with client SocketIO')


@socketio.on('disconnect')
def handle_disconnect():
    print('Disconnect with client SocketIO')


ip_address = get_ipv4_address()


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host=ip_address, port=5000,
                 ssl_context=('cert.crt', 'private.key'))
