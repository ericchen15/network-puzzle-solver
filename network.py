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

def big_to_small(char):
    char_ascii = ord(char)
    if char_ascii < 66:
        return char
    elif char_ascii < 75:
        char_ascii -= 17
    elif char_ascii < 80:
        char_ascii += 22
    else:
        return char
    return chr(char_ascii)

class Reader(object):

    do_open = True

    def open(self):
        if self.do_open:
            response = urllib.request.urlopen(self.url)
            self.data = response.read()
            self.text = self.data.decode('utf-8')

    def list_to_shapes(self):
        filtered_list = ""
        for char in self.char_list:
            filtered_list += big_to_small(char)
        self.shape_list = [shape_dictionary[char] for char in filtered_list]

    def create_board(self):
        self.board = Board(self.rows, self.cols)
        self.board.wrap = self.wrap
        for row in range(self.rows):
            for col in range(self.cols):
                curr_cell = self.board.grid[row][col]
                curr_cell.set_shape(self.shape_list[self.cols * row + col](curr_cell))

class BrainBashersReader(Reader):

    def __init__(self, month, date, size, wrap):
        if wrap:
            wrap_str = "WRAP"
        else:
            wrap_str = "NOWRAP"
        self.wrap = wrap
        self.rows = size
        self.cols = size
        self.str_date = str(date)
        if len(self.str_date) == 1:
            self.str_date = "0" + self.str_date
        self.url = "https://brainbashers.com/shownetwork.asp?date={0}{1}&size={2}&diff={3}".format(month, self.str_date, size, wrap_str)

    def create_list(self):
        index_lcpuzzle = self.text.index("lcpuzzle =")
        text = self.text[index_lcpuzzle:]
        index_quote = text.index('\"')
        text = text[index_quote + 1:]
        self.char_list = text[:(self.rows * self.cols)]
        assert len(self.char_list) == self.rows * self.cols


class LogicGamesOnlineReader(Reader):

    do_create_list = True

    def __init__(self, puzzle_id = None):
        if puzzle_id == None:
            self.wrap = True
            self.rows = 9
            self.cols = 9
            self.url = "http://www.logicgamesonline.com/netwalk/daily.php"
        else:
            self.do_open = False
            self.do_create_list = False
            num_cells = len(puzzle_id)
            self.rows = int(num_cells ** 0.5)
            self.cols = int(num_cells ** 0.5)
            self.wrap = False
            if self.rows == 9:
                self.wrap = True
            self.char_list = puzzle_id

    def create_list(self):
        if self.do_create_list:
            index_puzzle = self.text.index("puzzle =")
            text = self.text[index_puzzle:]
            index_quote = text.index('\"')
            text = text[index_quote + 1:]
            self.char_list = text[:(self.rows * self.cols)]
            assert len(self.char_list) == self.rows * self.cols

class SimonTathamReader(Reader):

    def __init__(self, puzzle_id):

        self.do_open = False

        index_x = puzzle_id.index('x')
        self.cols = int(puzzle_id[:index_x])
        puzzle_id = puzzle_id[index_x + 1:]
        index_after_rows = puzzle_id.index(':')
        if 'w' in puzzle_id:
            self.wrap = True
            index_after_rows = puzzle_id.index('w')
        else:
            self.wrap = False
        self.rows = int(puzzle_id[:index_after_rows])
        index_colon = puzzle_id.index(':')
        self.char_list = puzzle_id[index_colon + 1:]
        self.remove_barriers()

    def remove_barriers(self):
        filtered = ""
        for char in self.char_list:
            if char in shape_dictionary:
                filtered += char
        self.char_list = filtered

    def create_list(self):
        return

def user_input():
    print('this program solves \"network\" logic puzzles')
    print('it genereates a url, finds the puzzle data in the html file, and applies a recursive algorithm to solve the puzzle')
    site = input('enter site (brainbashers, logicgamesonline, simontatham): ')
    if site == 'brainbashers':
        month = input('enter month (integer): ')
        date = input('enter date (integer): ')
        size = input('enter size (6, 9, 12): ')
        wrap = input('wrap? (Yes/No): ')
        return BrainBashersReader(int(month), int(date), int(size), wrap.upper() == 'YES' or wrap.upper() == 'Y')
    elif site == 'logicgamesonline':
        default = input('daily expert puzzle? (Yes/No): ')
        if default.upper() == 'YES' or default.upper() == 'Y':
            return LogicGamesOnlineReader()
        else:
            puzzle_id = input('enter puzzle id: ')
            return LogicGamesOnlineReader(puzzle_id)
    elif site == 'simontatham':
        puzzle_id = input('enter game id: ')
        return SimonTathamReader(puzzle_id)

def run():
    reader = user_input()
    reader.open()
    reader.create_list()
    reader.list_to_shapes()
    reader.create_board()

    solver = Solver(reader.board)
    return solver.strategy()

run()