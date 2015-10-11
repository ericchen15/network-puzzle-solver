import copy
import urllib.request
import re

class Board(object):

    wrap = True

    def __eq__(self, other):
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.grid[row][col].shape.connections == other.grid[row][col].shape.connections:
                    return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def change_one(self):
        for row in self.grid:
            for cell in row:
                if -1 in cell.shape.connections:
                    index_neg1 = cell.shape.connections.index(-1)
                    cell.shape.connections[index_neg1] = 1
                    return

    def change_zero(self):
        for row in self.grid:
            for cell in row:
                if -1 in cell.shape.connections:
                    index_neg1 = cell.shape.connections.index(-1)
                    cell.shape.connections[index_neg1] = 0
                    return

    def __init__(self, rows, cols):
        self.grid = [self.make_row(row, cols) for row in range(rows)]
        self.size = rows * cols
        self.rows = rows
        self.cols = cols

    def make_row(self, row, cols):
        return [Cell(self, row, col) for col in range(cols)]

    def apply_every_shape(self, f):
        for row in self.grid:
            for cell in row:
                f(cell.shape)

    def str_row(self, row):
        row_to_print = self.grid[row]
        string_0, string_1, string_2 = "", "", ""
        for cell in row_to_print:
            string_0 += cell.shape.first_row()
        for cell in row_to_print:
            string_1 += cell.shape.second_row()
        for cell in row_to_print:
            string_2 += cell.shape.third_row()
        return "{0}\n{1}\n{2}\n".format(string_0, string_1, string_2)

    def connections_row(self, row):
        row_to_print = self.grid[row]
        string_0, string_1, string_2 = "", "", ""
        for cell in row_to_print:
            string_0 += cell.shape.first_connections()
        for cell in row_to_print:
            string_1 += cell.shape.second_connections()
        for cell in row_to_print:
            string_2 += cell.shape.third_connections()
        return "{0}\n{1}\n{2}\n".format(string_0, string_1, string_2)

    def another_str(self):
        whole_string = ""
        for n in range(self.rows):
            whole_string += self.str_row(n)
        return whole_string

    def __str__(self):
        whole_string = ""
        for n in range(self.rows):
            whole_string += self.connections_row(n)
        return whole_string

    def is_bad(self):
        for row in self.grid:
            for cell in row:
                if cell.check_loop():
                    print('bad island')
                    return True
                if cell.shape.bad_connection():
                    print('bad connection')
                    return True
                if cell.in_loop(None, []):
                    print('bad loop')
                    return True
        return False

    def update(self):
        self.apply_every_shape(Shape.force_own)
        self.apply_every_shape(Shape.update_connections)
        """
        self.apply_every_shape(Shape.set_orientation)
        """

    def solved(self):
        if self.is_bad():
            return False
        for row in self.grid:
            for cell in row:
                if -1 in cell.shape.connections:
                    return False
        return True


class Cell(object):

    def __init__(self, board, row, col):
        self.shape = None
        self.board = board
        self.row = row
        self.col = col

    def __str__(self):
        if self.shape:
            return str(self.shape)

    def __repr__(self):
        return "{2} ({0}, {1})".format(self.row, self.col, self.shape.name)

    def set_shape(self, shape):
        self.shape = shape

    def neighbors(self):
        up = self.row - 1
        down = self.row + 1
        left = self.col - 1
        right = self.col + 1
        if up == -1:
            up = self.board.rows - 1
        if down == self.board.rows:
            down = 0
        if left == -1:
            left = self.board.cols - 1
        if right == self.board.cols:
            right = 0
        neighbor_list = []
        up_cell = self.board.grid[up][self.col]
        down_cell = self.board.grid[down][self.col]
        left_cell = self.board.grid[self.row][left]
        right_cell = self.board.grid[self.row][right]
        if self.board.wrap or not self.is_top():
            neighbor_list += [up_cell]
        if self.board.wrap or not self.is_right():
            neighbor_list += [right_cell]
        if self.board.wrap or not self.is_bottom():
            neighbor_list += [down_cell]
        if self.board.wrap or not self.is_left():
            neighbor_list += [left_cell]
        return neighbor_list

    def is_top(self):
        return self.row == 0

    def is_bottom(self):
        return self.row == self.board.rows - 1

    def is_left(self):
        return self.col == 0

    def is_right(self):
        return self.col == self.board.cols - 1

    def make_block(self, in_block, not_in_block):
        if not self.shape.locked():
            not_in_block += [self]
        else:
            in_block += [self]
            for neighbor in self.neighbors():
                if not neighbor in in_block and not neighbor in not_in_block:
                    neighbor.make_block(in_block, not_in_block)
        return in_block

    def in_loop(self, last, visited):
        if self in visited:
            return True
        visited += [self]
        for neighbor in self.neighbors():
            if self.is_connected(neighbor) and not neighbor == last:
                if neighbor.in_loop(self, visited):
                    return True

    def other_above_self(self, other):
        if self.col != other.col:
            return False
        elif self.row == other.row + 1:
            return True
        elif self.row == 0 and other.row == self.board.rows - 1 and self.board.wrap:
            return True
        else:
            return False

    def other_below_self(self, other):
        if self.col != other.col:
            return False
        elif self.row == other.row - 1:
            return True
        elif other.row == 0 and self.row == self.board.rows - 1 and self.board.wrap:
            return True
        else:
            return False

    def other_left_self(self, other):
        if self.row != other.row:
            return False
        elif self.col == other.col + 1:
            return True
        elif self.col == 0 and other.col == self.board.cols - 1 and self.board.wrap:
            return True
        else:
            return False

    def other_right_self(self, other):
        if self.row != other.row:
            return False
        elif self.col == other.col - 1:
            return True
        elif other.col == 0 and self.col == self.board.cols - 1 and self.board.wrap:
            return True
        else:
            return False

    def is_connected(self, neighbor):
        if self.other_above_self(neighbor):
            return self.shape.connections[0] == 1 and neighbor.shape.connections[2] == 1
        elif self.other_right_self(neighbor):
            return self.shape.connections[1] == 1 and neighbor.shape.connections[3] == 1
        elif self.other_below_self(neighbor):
            return self.shape.connections[2] == 1 and neighbor.shape.connections[0] == 1
        else:
            return self.shape.connections[3] == 1 and neighbor.shape.connections[1] == 1

    def make_linked(self, in_linked):
        if not self.shape.locked():
            return []
        else:
            in_linked += [self]
            for neighbor in self.neighbors():
                if self.is_connected(neighbor) and not neighbor in in_linked:
                    neighbor.make_linked(in_linked)
        return in_linked

    def check_loop(self):
        linked = self.make_linked([])
        if not linked:
            return False
        if len(linked) < self.board.size:
            for cell in linked:
                connected_cells = [neighbor for neighbor in cell.neighbors() if cell.is_connected(neighbor)]
                for connected_cell in connected_cells:
                    if not connected_cell in linked:
                        return False
            return True
        return False

class Shape(object):

    def __init__(self, cell):
        self.orientation = [1, 1, 1, 1]
        self.connections = [-1, -1, -1, -1]
        self.cell = cell

    def locked(self):
        if sum(self.orientation) == 1:
            return True
        else:
            return False

    def orient_contradiction(self):
        if sum(self.orientation) == 0:
            return True
        else:
            return False

    def __str__(self):
        if not self.locked():
            return "   \n ? \n   "
        else:
            return self.picture()

    def show_connections(self):
        total = " "
        if self.connections[0] == 1:
            total += "|"
        elif self.connections[0] == 0:
            total += " "
        else:
            total += "?"
        total += " \n"
        if self.connections[3] == 1:
            total += "-"
        elif self.connections[3] == 0:
            total += " "
        else:
            total += "?"
        total += "o"
        if self.connections[1] == 1:
            total += "-"
        elif self.connections[1] == 0:
            total += " "
        else:
            total += "?"
        total += "\n "
        if self.connections[2] == 1:
            total += "|"
        elif self.connections[2] == 0:
            total += " "
        else:
            total += "?"
        total += " \n"
        return total

    def first_connections(self):
        all_connections = self.show_connections()
        return all_connections[:3]

    def second_connections(self):
        all_connections = self.show_connections()
        return all_connections[4:7]

    def third_connections(self):
        all_connections = self.show_connections()
        return all_connections[8:11]

    def first_row(self):
        all_rows = str(self)
        return all_rows[:3]

    def second_row(self):
        all_rows = str(self)
        return all_rows[4:7]

    def third_row(self):
        all_rows = str(self)
        return all_rows[8:11]

    def force_own(self):
        self.force_own()
        if not self.cell.board.wrap:
            if self.cell.is_top():
                self.connections[0] = 0
            if self.cell.is_right():
                self.connections[1] = 0
            if self.cell.is_bottom():
                self.connections[2] = 0
            if self.cell.is_left():
                self.connections[3] = 0

    def update_connections(self):
        neighbors = self.cell.neighbors()
        if self.cell.board.wrap:
            for n in range(4):
                adjacent = neighbors[n].shape.connections[opposite(n)]
                if adjacent != -1:
                    self.connections[n] = adjacent
        else:
            for neighbor in neighbors:
                if self.cell.other_above_self(neighbor):
                    if neighbor.shape.connections[2] != -1:
                        self.connections[0] = neighbor.shape.connections[2]
                elif self.cell.other_right_self(neighbor):
                    if neighbor.shape.connections[3] != -1:
                        self.connections[1] = neighbor.shape.connections[3]
                elif self.cell.other_below_self(neighbor):
                    if neighbor.shape.connections[0] != -1:
                        self.connections[2] = neighbor.shape.connections[0]
                else:
                    if neighbor.shape.connections[1] != -1:
                        self.connections[3] = neighbor.shape.connections[1]


    def set_orientation(self):
        if self.connections.count(1) == self.lines:
            self.orient()

    def set_connections(self):
        if self.locked():
            self.connect()

    def impossible_connections(self):
        if self.connections.count(1) == 4 or self.connections.count(0) == 4:
            return True
        else:
            return False

    def same_opposites(self):
        if self.connections[0] == self.connections[2]:
            if self.connections[0] != -1:
                return True
        elif self.connections[1] == self.connections[3]:
            if self.connections[1] != -1:
                return True
        else:
            return False

    def same_adjacents(self):
        if self.connections[0] == self.connections[1]:
            if self.connections[0] != -1:
                return True
        elif self.connections[1] == self.connections[2]:
            if self.connections[1] != -1:
                return True
        if self.connections[2] == self.connections[3]:
            if self.connections[2] != -1:
                return True
        elif self.connections[3] == self.connections[0]:
            if self.connections[3] != -1:
                return True
        else:
            return False

    def bad_wrap(self):
        if self.cell.is_top():
            return self.connections[0] == 1
        if self.cell.is_right():
            return self.connections[1] == 1
        if self.cell.is_bottom():
            return self.connections[2] == 1
        if self.cell.is_left():
            return self.connections[3] == 1

def opposite(n):
    if n == 0:
        return 2
    elif n == 1:
        return 3
    elif n == 2:
        return 0
    else:
        return 1
            
class One(Shape):
    
    lines = 1
    name = "One"

    def picture(self):
        if self.orientation[0] == 1:
            return " | \n o \n   "
        elif self.orientation[1] == 1:
            return "   \n o-\n   "
        elif self.orientation[2] == 1:
            return "   \n o \n | "
        else:
            return "   \n-o \n   "

    def bad_connection(self):
        if not self.cell.board.wrap:
            Shape.bad_wrap(self)
        if self.connections.count(0) > 3:
            return True
        elif self.connections.count(1) > 1:
            return True
        else:
            return False

    def orient(self):
        first_connection = self.connections.index(1)
        self.orientation = [0, 0, 0, 0]
        self.orientation[first_connection] = 1

    def connect(self):
        direction = self.orientation.index(1)
        self.connections = [0, 0, 0, 0]
        self.connections[direction] = 1

    def force_own(self):
        if 1 in self.connections:
            self.connections = [1 if element == 1 else 0 for element in self.connections]
        elif self.connections.count(0) == 3:
            self.connections = [0 if element == 0 else 1 for element in self.connections]

class Two(Shape):
    
    lines = 2
    name = "Two"

    def picture(self):
        if self.orientation[0] == 1:
            return " | \n o-\n   "
        elif self.orientation[1] == 1:
            return "   \n o-\n | "
        elif self.orientation[2] == 1:
            return "   \n-o \n | "
        else:
            return " | \n-o \n   "

    def bad_connection(self):
        if not self.cell.board.wrap:
            Shape.bad_wrap(self)
        if self.connections.count(1) > 2:
            return True
        elif self.connections.count(0) > 2:
            return True
        elif self.same_opposites():
            return True
        else:
            return False

    def orient(self):
        first_connection = self.connections.index(1)
        if first_connection == 0 and self.connections[3] == 1:
            first_connection = 3
        self.orientation = [0, 0, 0, 0]
        self.orientation[first_connection] = 1

    def connect(self):
        direction = self.orientation.index(1)
        next_direction = (direction + 1) % 4
        self.connections = [0, 0, 0, 0]
        self.connections[direction] = 1
        self.connections[next_direction] = 1

    def force_own(self):
        if self.connections.count(0) == 1:
            index0 = self.connections.index(0)
            self.connections[opposite(index0)] = 1
        if self.connections.count(1) == 1:
            index1 = self.connections.index(1)
            self.connections[opposite(index1)] = 0
        if self.connections.count(0) == 2:
            self.connections = [0 if element == 0 else 1 for element in self.connections]
        elif self.connections.count(1) == 2:
            self.connections = [1 if element == 1 else 0 for element in self.connections]

class Line(Shape):
    
    lines = 2
    name = "Line"

    def picture(self):
        if self.orientation[0] == 1:
            return " | \n o \n | "
        elif self.orientation[1] == 1:
            return "   \n-o-\n   "
        elif self.orientation[2] == 1:
            return " | \n o \n | "
        else:
            return "   \n-o-\n   "

    def bad_connection(self):
        if not self.cell.board.wrap:
            Shape.bad_wrap(self)
        if self.connections.count(1) > 2:
            return True
        elif self.connections.count(0) > 2:
            return True
        elif self.same_adjacents():
            return True
        else:
            return False

    def orient(self):
        first_connection = self.connections.index(1)
        self.orientation = [0, 0, 0, 0]
        self.orientation[first_connection] = 1

    def connect(self):
        direction = self.orientation.index(1)
        self.connections = [0, 0, 0, 0]
        self.connections[direction] = 1
        self.connections[direction + 2] = 1

    def force_own(self):
        if 1 in self.connections:
            index1 = self.connections.index(1)
            self.connections[opposite(index1)] = 1
            self.connections = [1 if element == 1 else 0 for element in self.connections]
        if 0 in self.connections:
            index0 = self.connections.index(0)
            self.connections[opposite(index0)] = 0
            self.connections = [0 if element == 0 else 1 for element in self.connections]   

class Three(Shape):
    
    lines = 3
    name = "Three"

    def picture(self):
        if self.orientation[0] == 1:
            return " | \n o-\n | "
        elif self.orientation[1] == 1:
            return "   \n-o-\n | "
        elif self.orientation[2] == 1:
            return " | \n-o \n | "
        else:
            return " | \n-o-\n   "

    def bad_connection(self):
        if not self.cell.board.wrap:
            Shape.bad_wrap(self)
        if self.connections.count(1) > 3:
            return True
        elif self.connections.count(0) > 1:
            return True
        else:
            return False

    def orient(self):
        first_zero = self.connections.index(0)
        self.orientation = [0, 0, 0, 0]
        if first_zero == 3:
            first_zero = -1
        self.orientation[first_zero + 1] = 1

    def connect(self):
        direction = self.orientation.index(1)
        only_zero = (direction - 1) % 4
        self.connections = [1, 1, 1, 1]
        self.connections[only_zero] = 0

    def force_own(self):
        if 0 in self.connections:
            self.connections = [0 if element == 0 else 1 for element in self.connections]
        elif self.connections.count(1) == 3:
            self.connections = [1 if element == 1 else 0 for element in self.connections]

class Solver(object):

    def __init__(self, board):
        self.board = board

    def strategy(self):
        old_board = copy.deepcopy(self.board)
        self.board.update()
        new_board = copy.deepcopy(self.board)
        print(new_board)
        print("\n")
        while new_board != old_board:
            old_board = copy.deepcopy(self.board)
            self.board.update()
            new_board = copy.deepcopy(self.board)
            print(new_board)
            print("\n")

        self.board.apply_every_shape(Shape.set_orientation)

        if self.board.is_bad():
            return False
        if self.board.solved():
            return self.board
        else:
            return self.assume()

    def assume(self):
        new_board = copy.deepcopy(self.board)
        new_board.change_one()
        new_solver = Solver(new_board)
        if new_solver.strategy():
            self.board = new_solver.board
            return self.board
        else:
            self.board.change_zero()
            return self.strategy()

shape_dictionary = {'1':One, '2':One, '4':One, '8':One, '3':Two, '6':Two, '9':Two, 'c':Two, '5':Line, 'a':Line, '7':Three, 'b':Three, 'd':Three, 'e':Three}

class Reader(object):

    def __init__(self, month, date, size, wrap):
        if wrap:
            wrap_str = "WRAP"
        else:
            wrap_str = "NOWRAP"
        self.wrap = wrap
        self.size = size
        self.str_date = str(date)
        if len(self.str_date) == 1:
            self.str_date = "0" + self.str_date
        self.url = "https://brainbashers.com/shownetwork.asp?date={0}{1}&size={2}&diff={3}".format(month, self.str_date, size, wrap_str)

    def open(self):
        response = urllib.request.urlopen(self.url)
        self.data = response.read()
        self.text = self.data.decode('utf-8')

    def create_list(self):
        """
        self.char_list = re.match("lcpuzzle.*?\"(.*)\"", self.text)
        """
        index_lcpuzzle = self.text.index("lcpuzzle =")
        text = self.text[index_lcpuzzle:]
        index_quote = text.index('\"')
        text = text[index_quote + 1:]
        self.char_list = text[:(self.size * self.size)]
        assert len(self.char_list) == self.size * self.size

    def list_to_shapes(self):
        self.shape_list = [shape_dictionary[char] for char in self.char_list]

    def create_board(self):
        self.board = Board(self.size, self.size)
        self.board.wrap = self.wrap
        for row in range(self.size):
            for col in range(self.size):
                curr_cell = self.board.grid[row][col]
                curr_cell.set_shape(self.shape_list[self.size * row + col](curr_cell))

def user_input():
    print('this program solves the \"network\" logic puzzles on brainbashers.com')
    print('it genereates a url, finds the puzzle data in the html file, and applies a recursive algorithm to solve the puzzle')
    print('only puzzles from the last 10 days are available')
    month = input('enter month: ')
    date = input('enter date: ')
    size = input('enter size (6, 9, 12): ')
    wrap = input('wrap? Yes/No: ')
    run(int(month), int(date), int(size), wrap.upper() == 'YES' or wrap.upper() == 'Y')

def run(month, date, size, wrap):
    r = Reader(month, date, size, wrap)
    r.open()
    r.create_list()
    r.list_to_shapes()
    r.create_board()

    s = Solver(r.board)
    s.strategy()

user_input()

"""
board = Board(3, 3)
row0, row1, row2 = board.grid
cell00, cell01, cell02 = row0
cell10, cell11, cell12 = row1
cell20, cell21, cell22 = row2
shape00 = One(cell00)
cell00.set_shape(shape00)
shape01 = Two(cell01)
cell01.set_shape(shape01)
shape02 = Three(cell02)
cell02.set_shape(shape02)
shape10 = Line(cell10)
cell10.set_shape(shape10)
shape11 = One(cell11)
cell11.set_shape(shape11)
shape12 = Two(cell12)
cell12.set_shape(shape12)
shape20 = Three(cell20)
cell20.set_shape(shape20)
shape21 = Line(cell21)
cell21.set_shape(shape21)
shape22 = One(cell22)
cell22.set_shape(shape22)

shape11.orientation = [0, 1, 0, 0]
shape11.set_connections()

shape12.orientation = [0, 0, 1, 0]
shape12.set_connections()

shape22.orientation = [1, 0, 0, 0]
shape22.set_connections()

board = Board(3, 3)
row0, row1, row2 = board.grid
cell00, cell01, cell02 = row0
cell10, cell11, cell12 = row1
cell20, cell21, cell22 = row2
shape00 = One(cell00)
cell00.set_shape(shape00)
shape01 = Line(cell01)
cell01.set_shape(shape01)
shape02 = Two(cell02)
cell02.set_shape(shape02)
shape10 = One(cell10)
cell10.set_shape(shape10)
shape11 = Three(cell11)
cell11.set_shape(shape11)
shape12 = Two(cell12)
cell12.set_shape(shape12)
shape20 = One(cell20)
cell20.set_shape(shape20)
shape21 = One(cell21)
cell21.set_shape(shape21)
shape22 = Three(cell22)
cell22.set_shape(shape22)


shape01.connections = [-1, 1, -1, -1]


solver = Solver(board)

board1 = copy.deepcopy(board)
board1.change_one()

bb = Board(6, 6)
row0, row1, row2, row3, row4, row5 = bb.grid
cell00, cell01, cell02, cell03, cell04, cell05 = row0
cell10, cell11, cell12, cell13, cell14, cell15 = row1
cell20, cell21, cell22, cell23, cell24, cell25 = row2
cell30, cell31, cell32, cell33, cell34, cell35 = row3
cell40, cell41, cell42, cell43, cell44, cell45 = row4
cell50, cell51, cell52, cell53, cell54, cell55 = row5

shape00 = One(cell00)
cell00.set_shape(shape00)
shape01 = One(cell01)
cell01.set_shape(shape01)
shape02 = One(cell02)
cell02.set_shape(shape02)
shape03 = Line(cell03)
cell03.set_shape(shape03)
shape04 = Two(cell04)
cell04.set_shape(shape04)
shape05 = One(cell05)
cell05.set_shape(shape05)

shape10 = Three(cell10)
cell10.set_shape(shape10)
shape11 = Line(cell11)
cell11.set_shape(shape11)
shape12 = Three(cell12)
cell12.set_shape(shape12)
shape13 = Three(cell13)
cell13.set_shape(shape13)
shape14 = One(cell14)
cell14.set_shape(shape14)
shape15 = Line(cell15)
cell15.set_shape(shape15)

shape20 = Line(cell20)
cell20.set_shape(shape20)
shape21 = Line(cell21)
cell21.set_shape(shape21)
shape22 = One(cell22)
cell22.set_shape(shape22)
shape23 = Two(cell23)
cell23.set_shape(shape23)
shape24 = Three(cell24)
cell24.set_shape(shape24)
shape25 = Two(cell25)
cell25.set_shape(shape25)

shape30 = Three(cell30)
cell30.set_shape(shape30)
shape31 = Three(cell31)
cell31.set_shape(shape31)
shape32 = Line(cell32)
cell32.set_shape(shape32)
shape33 = Line(cell33)
cell33.set_shape(shape33)
shape34 = Three(cell34)
cell34.set_shape(shape34)
shape35 = One(cell35)
cell35.set_shape(shape35)

shape40 = One(cell40)
cell40.set_shape(shape40)
shape41 = Two(cell41)
cell41.set_shape(shape41)
shape42 = Line(cell42)
cell42.set_shape(shape42)
shape43 = Line(cell43)
cell43.set_shape(shape43)
shape44 = Three(cell44)
cell44.set_shape(shape44)
shape45 = One(cell45)
cell45.set_shape(shape45)

shape50 = One(cell50)
cell50.set_shape(shape50)
shape51 = One(cell51)
cell51.set_shape(shape51)
shape52 = One(cell52)
cell52.set_shape(shape52)
shape53 = Two(cell53)
cell53.set_shape(shape53)
shape54 = Three(cell54)
cell54.set_shape(shape54)
shape55 = Three(cell55)
cell55.set_shape(shape55)

sb = Solver(bb)
bb.grid[0][0].shape.connections[2] = 1

shape00 = One(cell00)
cell00.set_shape(shape00)
shape01 = Three(cell01)
cell01.set_shape(shape01)
shape02 = Three(cell02)
cell02.set_shape(shape02)
shape03 = One(cell03)
cell03.set_shape(shape03)
shape04 = Three(cell04)
cell04.set_shape(shape04)
shape05 = Two(cell05)
cell05.set_shape(shape05)

shape10 = Two(cell10)
cell10.set_shape(shape10)
shape11 = Three(cell11)
cell11.set_shape(shape11)
shape12 = One(cell12)
cell12.set_shape(shape12)
shape13 = Line(cell13)
cell13.set_shape(shape13)
shape14 = Three(cell14)
cell14.set_shape(shape14)
shape15 = One(cell15)
cell15.set_shape(shape15)

shape20 = Line(cell20)
cell20.set_shape(shape20)
shape21 = Three(cell21)
cell21.set_shape(shape21)
shape22 = One(cell22)
cell22.set_shape(shape22)
shape23 = Line(cell23)
cell23.set_shape(shape23)
shape24 = Three(cell24)
cell24.set_shape(shape24)
shape25 = Line(cell25)
cell25.set_shape(shape25)

shape30 = One(cell30)
cell30.set_shape(shape30)
shape31 = Two(cell31)
cell31.set_shape(shape31)
shape32 = Three(cell32)
cell32.set_shape(shape32)
shape33 = Three(cell33)
cell33.set_shape(shape33)
shape34 = Three(cell34)
cell34.set_shape(shape34)
shape35 = One(cell35)
cell35.set_shape(shape35)

shape40 = One(cell40)
cell40.set_shape(shape40)
shape41 = One(cell41)
cell41.set_shape(shape41)
shape42 = Two(cell42)
cell42.set_shape(shape42)
shape43 = One(cell43)
cell43.set_shape(shape43)
shape44 = Three(cell44)
cell44.set_shape(shape44)
shape45 = Three(cell45)
cell45.set_shape(shape45)

shape50 = One(cell50)
cell50.set_shape(shape50)
shape51 = One(cell51)
cell51.set_shape(shape51)
shape52 = One(cell52)
cell52.set_shape(shape52)
shape53 = One(cell53)
cell53.set_shape(shape53)
shape54 = Two(cell54)
cell54.set_shape(shape54)
shape55 = Two(cell55)
cell55.set_shape(shape55)

s = Solver(bb)

bb.wrap = False

shape00 = Two(cell00)
cell00.set_shape(shape00)
shape01 = One(cell01)
cell01.set_shape(shape01)
shape02 = One(cell02)
cell02.set_shape(shape02)
shape03 = One(cell03)
cell03.set_shape(shape03)
shape04 = One(cell04)
cell04.set_shape(shape04)
shape05 = Two(cell05)
cell05.set_shape(shape05)

shape10 = Line(cell10)
cell10.set_shape(shape10)
shape11 = One(cell11)
cell11.set_shape(shape11)
shape12 = Two(cell12)
cell12.set_shape(shape12)
shape13 = Three(cell13)
cell13.set_shape(shape13)
shape14 = Two(cell14)
cell14.set_shape(shape14)
shape15 = Three(cell15)
cell15.set_shape(shape15)

shape20 = Two(cell20)
cell20.set_shape(shape20)
shape21 = Three(cell21)
cell21.set_shape(shape21)
shape22 = One(cell22)
cell22.set_shape(shape22)
shape23 = Three(cell23)
cell23.set_shape(shape23)
shape24 = Line(cell24)
cell24.set_shape(shape24)
shape25 = Line(cell25)
cell25.set_shape(shape25)

shape30 = One(cell30)
cell30.set_shape(shape30)
shape31 = Two(cell31)
cell31.set_shape(shape31)
shape32 = Line(cell32)
cell32.set_shape(shape32)
shape33 = Three(cell33)
cell33.set_shape(shape33)
shape34 = Three(cell34)
cell34.set_shape(shape34)
shape35 = One(cell35)
cell35.set_shape(shape35)

shape40 = Three(cell40)
cell40.set_shape(shape40)
shape41 = Three(cell41)
cell41.set_shape(shape41)
shape42 = Three(cell42)
cell42.set_shape(shape42)
shape43 = Three(cell43)
cell43.set_shape(shape43)
shape44 = Three(cell44)
cell44.set_shape(shape44)
shape45 = One(cell45)
cell45.set_shape(shape45)

shape50 = One(cell50)
cell50.set_shape(shape50)
shape51 = One(cell51)
cell51.set_shape(shape51)
shape52 = One(cell52)
cell52.set_shape(shape52)
shape53 = One(cell53)
cell53.set_shape(shape53)
shape54 = Two(cell54)
cell54.set_shape(shape54)
shape55 = Two(cell55)
cell55.set_shape(shape55)

s = Solver(bb)

r = Reader(10, 4, 12, False)
r.open()
r.create_list()
r.list_to_shapes()
r.create_board()

s = Solver(r.board)
s.strategy()
"""