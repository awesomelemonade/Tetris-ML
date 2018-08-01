from Color import Color
from collections import namedtuple
from recordclass import recordclass

PieceTemplate = recordclass('PieceTemplate', ['template', 'color'])
Piece = recordclass('Piece', ['x', 'y', 'type', 'rotation']) # rotation is an index of template

BLANK = '.'

class TetrisConstants:
	TEMPLATE_WIDTH = 5
	TEMPLATE_HEIGHT = 5
	S_SHAPE_TEMPLATE = [['.....',
		             '.....',
		             '..SS.',
		             '.SS..',
		             '.....'],
		            ['.....',
		             '..S..',
		             '..SS.',
		             '...S.',
		             '.....']]

	Z_SHAPE_TEMPLATE = [['.....',
		             '.....',
		             '.ZZ..',
		             '..ZZ.',
		             '.....'],
		            ['.....',
		             '..Z..',
		             '.ZZ..',
		             '.Z...',
		             '.....']]

	I_SHAPE_TEMPLATE = [['..I..',
		             '..I..',
		             '..I..',
		             '..I..',
		             '.....'],
		            ['.....',
		             '.....',
		             'IIII.',
		             '.....',
		             '.....']]

	O_SHAPE_TEMPLATE = [['.....',
		             '.....',
		             '.OO..',
		             '.OO..',
		             '.....']]

	J_SHAPE_TEMPLATE = [['.....',
		             '.J...',
		             '.JJJ.',
		             '.....',
		             '.....'],
		            ['.....',
		             '..JJ.',
		             '..J..',
		             '..J..',
		             '.....'],
		            ['.....',
		             '.....',
		             '.JJJ.',
		             '...J.',
		             '.....'],
		            ['.....',
		             '..J..',
		             '..J..',
		             '.JJ..',
		             '.....']]

	L_SHAPE_TEMPLATE = [['.....',
		             '...L.',
		             '.LLL.',
		             '.....',
		             '.....'],
		            ['.....',
		             '..L..',
		             '..L..',
		             '..LL.',
		             '.....'],
		            ['.....',
		             '.....',
		             '.LLL.',
		             '.L...',
		             '.....'],
		            ['.....',
		             '.LL..',
		             '..L..',
		             '..L..',
		             '.....']]

	T_SHAPE_TEMPLATE = [['.....',
		             '..T..',
		             '.TTT.',
		             '.....',
		             '.....'],
		            ['.....',
		             '..T..',
		             '..TT.',
		             '..T..',
		             '.....'],
		            ['.....',
		             '.....',
		             '.TTT.',
		             '..T..',
		             '.....'],
		            ['.....',
		             '..T..',
		             '.TT..',
		             '..T..',
		             '.....']]
	PIECES = {'S': PieceTemplate(S_SHAPE_TEMPLATE, Color.YELLOW),
		  'Z': PieceTemplate(Z_SHAPE_TEMPLATE, Color.WHITE),
		  'J': PieceTemplate(J_SHAPE_TEMPLATE, Color.GREEN),
		  'L': PieceTemplate(L_SHAPE_TEMPLATE, Color.RED),
		  'I': PieceTemplate(I_SHAPE_TEMPLATE, Color.PURPLE),
		  'O': PieceTemplate(O_SHAPE_TEMPLATE, Color.ORANGE),
		  'T': PieceTemplate(T_SHAPE_TEMPLATE, Color.BLUE)}
