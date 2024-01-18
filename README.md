# Sudoku Solver Web App

## Introduction:
Sudoku is a puzzle game that involves filling a 9x9 grid with numbers from 1 to 9, ensuring that each column, each row, and each of the nine 3x3 subgrids (referred to as "blocks" or "sub-squares") contains all the digits from 1 to 9.  
This project works as a web application server. The website utilizes the camera on the client's device to perform real-time recognition of a Sudoku puzzle, subsequently solving the puzzle and displaying the results. The project is available in two versions: a local application and a web application.

https://github.com/jarczano/Sudoku-Solver-Web-App/assets/107764304/0292f297-c4bb-4115-9bc4-d01fe915797d

## Project Description - How It Works:

### Image Recognition  
1. The entire Sudoku board is recognized using the Canny edge detector and the contour detection algorithm by Satoshi Suzuki. If the detected contour meets the requirements of having 4 vertices, sufficient screen coverage, a convex shape, and is approximately square, the process continues.  
2. For dividing the board into 81 individual cells, two approaches are used depending on the image quality. The algorithm for high-quality images is more effective but may not work well with low-resolution images.  
- Low image quality: This approach uses a geometric division of the detected Sudoku board's edges into 9 equal segments to determine individual cells.  
- High image quality: For recognizing the 81 individual cells, image processing algorithms like blur, threshold, Line Segment Detector, and the contour detection algorithm by Satoshi Suzuki are used. Once 81 cells meeting the requirements (sufficient area, 4 vertices, convex shape) are detected, the process continues. In this algorithm, the contours of individual cells must be additionally sorted from the top-left to the bottom-right.  
3. For recognizing the contents of the cells, two Convolutional Neural Network models are used. The first model recognizes whether a cell is empty or filled. The second model recognizes the digits and creates a corresponding 9x9 matrix for the Sudoku board.  

### Sudoku Solving
- Simple Sudoku boards  
For each empty cell, all possible options (digits from 1 to 9) are inserted. Then, for each of these cells, the digits that are already present in the same row, column, or 3x3 square are eliminated.  
When only one possibility remains for a cell, that number is filled in, and the digit is removed from the possibility set for the corresponding row, column, and 3x3 square. An additional algorithm checks if any digit can only be placed in one specific cell within a row, column, or 3x3 square. The combination of these algorithms is sufficient for solving simple Sudoku boards.
- Difficult Sudoku boards  
For Sudoku puzzles with a small number of initially filled cells, when the solving algorithms mentioned above become ineffective, a random selection method is used. Before starting, a copy of the initial board is created. The method involves randomly selecting a cell with the fewest possible options and filling it with a randomly chosen value from the available set. Then, the "exclude possibilities" method is applied until it becomes ineffective, and then the "random selection" algorithm is used.  
After each iteration, a correctness check algorithm is executed to verify if there is at least one possible option for each cell. If the Sudoku board becomes unsolvable, the process reverts to the initial copy; otherwise, solving continues. This is not an optimal Sudoku-solving algorithm, as the goal was to come up with a custom approach.

### Digit Recognition Model
Two Convolutional Neural Network models are used for recognizing the contents of the cells. The first model recognizes whether a cell is empty or filled, while the second model recognizes the digit present in a filled cell.
The training data for the CNN models, which consists of images of digits 1 to 9, was created based on a collection of .ttf fonts from Google Fonts and augmented using data augmentation techniques.
The CNN model training code is available in the local version of the project.

## Usage:

- Clone the repository: `git clone https://github.com/jarczano/Sudoku-Solver-Web-App`
- Install the requirements: `pip install -r requirements.txt`
- Add the SSL certificate `cert.crt` and the private key `private.key` to the main folder. You can generate them for free using OpenSSL.
- Run `main.py`: `python main.py`

The application can be accessed on devices connected to the local network using the address displayed after running `main.py`.  
Model training is available in a local version aplication.

## Technologies:
- Numpy
- Flask
- Keras
- Tensorflow
- Scipy
- Opencv

## Related Projects:
- Sudoku Solver Locally App https://github.com/jarczano/Sudoku-Solver-Local-App
## License:
- MIT

## Author:
- Jarosław Turczyn
