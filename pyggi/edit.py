"""

This module contains Edit class which is an abstact base class,
and several classes inherit the Edit class.
The classes are provided as examples of custom edit operator.

"""
from abc import ABCMeta, abstractmethod
from .atomic_operator import AtomicOperator

class Edit(metaclass=ABCMeta):
    """
    Edit is an abstact class which is designed to be used
    as a basic structure of custom edit operators.

    Every class that inherits Edit class must override the
    methods marked with ``@abstractmethod`` to create instances.

    * :py:meth:`__str__`
    * :py:meth:`length_of_args`
    * :py:meth:`atomic_operators`
    """
    def __init__(self, *args):
        if len(args) != self.length_of_args:
            raise Exception("{} takes {} positional argument but {} were given.".format(
                self.__class__.__name__, self.length_of_args, len(args)))
        self.args = args
        assert isinstance(self.atomic_operators, list)
        assert all(isinstance(op, AtomicOperator) for op in self.atomic_operators)

    def __eq__(self, other):
        return self.atomic_operators == other.atomic_operators

    @property
    def detail(self) -> str:
        """
        :return: The detail of this custom edit
        :rtype: str

        .. note::
            If the edit is ``LineMoving(('Triangle.java', 4), ('Triangle.java', 10))``

            returns::

                1) Insert ('Triangle.java', 4) into ('Triangle.java', 10)
                2) Replace ('Triangle.java', 4) with None
        """
        return "\n".join(
            list(
                map(lambda x: "{}) {}".format(x[0] + 1, x[1]),
                    enumerate(self.atomic_operators))))

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def is_valid_for(self, program):
        """
        :param program: The program instance to which this edit will be applied
        :type program: :py:class:`.Program`
        :return: Whether the edit is able to be applied to the program
        :rtype: bool
        """
        pass

    @property
    @abstractmethod
    def length_of_args(self):
        """
        :return: The length of args the edit operator should take
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def atomic_operators(self):
        """
        :return: The list of instances of AtomicOperator.
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        pass

class LineDeletion(Edit):
    """
    LineDeletion: Delete x
    
    It replaces the code line with an empty line.
    """
    def __str__(self):
        return "Delete {}".format(self.x)

    def is_valid_for(self, program):
        from .program import MnplLevel
        if program.manipulation_level == MnplLevel.LINE:
            return True
        return False

    @property
    def x(self):
        """
        Delete **x**

        :return: The file path and the index of target line to be deleted.
        :rtype: tuple(str, int)
        """
        return self.args[0]

    @property
    def length_of_args(self):
        """
        :return: ``1``
        :rtype: int
        """
        return 1

    @property
    def atomic_operators(self):
        """
        :return: ``[LineReplacement(self.x, None)]``
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        from .atomic_operator import LineReplacement
        return [LineReplacement(self.x, None)]

    @classmethod
    def create(cls, program, line_file=None):
        """
        :param program: The program instance to which the random edit will be applied.
        :type program: :py:class:`.Program`
        :param str line_file: Line is the target line to delete.
          If line_file is specified, the target line will be chosen within the file.
        :return: The LineDeletion instance with the randomly-selected line index.
        :rtype: :py:class:`.edit.LineDeletion`
        """
        import random
        line_file = line_file or random.choice(program.target_files)
        line = (
            line_file,
            program.select_modification_point(line_file, 'random')
        )
        return cls(line)

class LineMoving(Edit):
    """
    LineMoving: Move x [before|after] y
    """
    def __str__(self):
        return "Move {} {} {}".format(self.x, self.direction, self.y)

    def is_valid_for(self, program):
        from .program import MnplLevel
        if program.manipulation_level == MnplLevel.LINE:
            return True
        return False

    @property
    def x(self):
        """
        Move **x** [before|after] y

        :return: The file path and the index of target line to be moved.
        :rtype: tuple(str, int)
        """
        return self.args[0]

    @property
    def y(self):
        """
        Move x [before|after] **y**

        :return: The file path and the index of the point to which line x is inserted.
        :rtype: tuple(str, int)
        """
        return self.args[1]

    @property
    def direction(self):
        """
        Move x **[before|after]** y

        :return: **'before'** or **'after'**
        :rtype: str
        """
        return self.args[2]

    @property
    def length_of_args(self):
        """
        :return: ``3``
        :rtype: int
        """
        return 3

    @property
    def atomic_operators(self):
        """
        :return: ``[LineInsertion(self.y, self.x), LineReplacement(self.x, None)]``
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        from .atomic_operator import LineInsertion, LineReplacement
        return [LineInsertion(self.y, self.x, self.direction), LineReplacement(self.x, None)]

    @classmethod
    def create(cls, program, line_file=None, ingr_file=None, direction='before'):
        """
        :param program: The program instance to which the random edit will be applied.
        :type program: :py:class:`.Program`
        :param str line_file: Line means the modification point of the edit. If line_file is specified, the line will be chosen within the file.
        :param str ingr_file: Ingredient is the line to be moved.
          If ingr_file is specified, the ingredient line will be chosen within the file.
        :return: The LineMoving instance with the randomly-selected line & ingr.
        :rtype: :py:class:`.edit.LineMoving`
        """
        import random
        line_file = line_file or random.choice(program.target_files)
        ingr_file = ingr_file or random.choice(program.target_files)
        line = (
            line_file,
            program.select_modification_point(line_file, 'random')
        )
        ingredient = (
            ingr_file,
            program.select_modification_point(ingr_file, 'random')
        )
        return cls(ingredient, line, direction)

class StmtDeletion(Edit):
    """
    StmtDeletion: Delete x (Actually, Replace x with an empty statement)
    """
    def __str__(self):
        return "Delete {}".format(self.x)

    def is_valid_for(self, program):
        from .program import MnplLevel
        if program.manipulation_level == MnplLevel.AST:
            return True
        return False

    @property
    def x(self):
        """
        Delete **x**

        :return: The file path and the position of target stmt to be deleted.
        :rtype: tuple(str, list(tuple(str, int)))
        """
        return self.args[0]

    @property
    def length_of_args(self):
        """
        :return: ``1``
        :rtype: int
        """
        return 1

    @property
    def atomic_operators(self):
        """
        :return: ``[StmtReplacement(self.x, None)]``
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        from .atomic_operator import StmtReplacement
        return [StmtReplacement(self.x, None)]

    @classmethod
    def create(cls, program, stmt_file=None):
        """
        :param program: The program instance to which the random edit will be applied.
        :type program: :py:class:`.Program`
        :param str stmt_file: stmt is the target statement to delete.
          If stmt_file is specified, the target statement will be chosen within that file.
        :return: The StmtDeletion instance with the randomly-selected modification point.
        :rtype: :py:class:`.edit.StmtDeletion`
        """
        import random
        stmt_file = stmt_file or random.choice(program.target_files)
        stmt = (
            stmt_file,
            program.select_modification_point(stmt_file, 'random')
        )
        return cls(stmt)
