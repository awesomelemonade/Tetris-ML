import Color

PieceTemplate = namedtuple('PieceTemplate', ['template', 'color'])
Piece = namedtuple('Piece', ['x', 'y', 'type', 'rotation']) # rotation is an index of template

class TetrisConstants:
	TEMPLATE_WIDTH = 5
	TEMPLATE_HEIGHT = 5

	PIECES = {'S': PieceTemplate(S_SHAPE_TEMPLATE, Color.YELLOW),
		  'Z': PieceTemplate(Z_SHAPE_TEMPLATE, Color.WHITE),
		  'J': PieceTemplate(J_SHAPE_TEMPLATE, Color.GREEN),
		  'L': PieceTemplate(L_SHAPE_TEMPLATE, Color.RED),
		  'I': PieceTemplate(I_SHAPE_TEMPLATE, Color.PURPLE),
		  'O': PieceTemplate(O_SHAPE_TEMPLATE, Color.ORANGE),
		  'T': PieceTemplate(T_SHAPE_TEMPLATE, Color.BLUE)}

	S_SHAPE_TEMPLATE = [['.....',
		             '.....',
		             '..OO.',
		             '.OO..',
		             '.....'],
		            ['.....',
		             '..O..',
		             '..OO.',
		             '...O.',
		             '.....']]

	Z_SHAPE_TEMPLATE = [['.....',
		             '.....',
		             '.OO..',
		             '..OO.',
		             '.....'],
		            ['.....',
		             '..O..',
		             '.OO..',
		             '.O...',
		             '.....']]

	I_SHAPE_TEMPLATE = [['..O..',
		             '..O..',
		             '..O..',
		             '..O..',
		             '.....'],
		            ['.....',
		             '.....',
		             'OOOO.',
		             '.....',
		             '.....']]

	O_SHAPE_TEMPLATE = [['.....',
		             '.....',
		             '.OO..',
		             '.OO..',
		             '.....']]

	J_SHAPE_TEMPLATE = [['.....',
		             '.O...',
		             '.OOO.',
		             '.....',
		             '.....'],
		            ['.....',
		             '..OO.',
		             '..O..',
		             '..O..',
		             '.....'],
		            ['.....',
		             '.....',
		             '.OOO.',
		             '...O.',
		             '.....'],
		            ['.....',
		             '..O..',
		             '..O..',
		             '.OO..',
		             '.....']]

	L_SHAPE_TEMPLATE = [['.....',
		             '...O.',
		             '.OOO.',
		             '.....',
		             '.....'],
		            ['.....',
		             '..O..',
		             '..O..',
		             '..OO.',
		             '.....'],
		            ['.....',
		             '.....',
		             '.OOO.',
		             '.O...',
		             '.....'],
		            ['.....',
		             '.OO..',
		             '..O..',
		             '..O..',
		             '.....']]

	T_SHAPE_TEMPLATE = [['.....',
		             '..O..',
		             '.OOO.',
		             '.....',
		             '.....'],
		            ['.....',
		             '..O..',
		             '..OO.',
		             '..O..',
		             '.....'],
		            ['.....',
		             '.....',
		             '.OOO.',
		             '..O..',
		             '.....'],
		            ['.....',
		             '..O..',
		             '.OO..',
		             '..O..',
		             '.....']]
