# MyPL
Implements a made up coding language called MyPL. Includes an interpreter, lexer, parser, and typechecker.

The txt files included are examples of MyPL programs that when run with hw7.py, produces outputs.

mypl_lexer.py, mypl_token.py chops up the MyPL code into "tokens" and creates a token stream.
mypl.parser.py then runs through the token stream and evaluates the syntac by using grammars.
mypl_parser.py and mypl_ast.py then build up an abstract syntax tree.
mypl_typechecker.py checks that the typing of variables is correct.
Finally, mypl_interpreter interprets the code and produces the output.

*Note* that mypl_typechecker is commented out in hw7.py since there was one case in which it produced an error for a test file where it shouldn't have.

To run:
python3 hw7.py hw7_t1.txt (or any of the other txt files)
