# Donya Jafari 401101524 - Nika Ghaderi 401106328
import os
import sys
from anytree import Node as AnyNode, RenderTree

# Increase recursion depth just in case
sys.setrecursionlimit(3000)

# ==========================================
#        CUSTOM NODE CLASS (The Fix)
# ==========================================
class Node(AnyNode):
    """
    Wrapper around anytree.Node to support .add_child() 
    and maintain compatibility with the parser code.
    """
    def add_child(self, child):
        if child:
            child.parent = self

# ==========================================
#              PHASE 1: SCANNER
# ==========================================
class Scanner:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line_number = 1
        self.symbol_table = {}
        self.errors = []
        
        self.keywords = [
            'break', 'else', 'if', 'for', 'int', 
            'return', 'void'
        ]
        
        for idx, keyword in enumerate(sorted(self.keywords), start=1):
            self.symbol_table[keyword] = idx
    
    def skip_whitespace(self):
        while self.pos < len(self.code) and self.code[self.pos] in ' \n\r\t\v\f':
            if self.code[self.pos] == '\n':
                self.line_number += 1
            self.pos += 1

    def get_next_token(self):
        self.skip_whitespace()
        
        if self.pos >= len(self.code):
            return ('SYMBOL', '$')
        
        if self.pos < len(self.code) - 1 and self.code[self.pos:self.pos+2] == '*/':
            self.errors.append({
                'line': self.line_number, 'error_str': '*/', 'message': 'Stray closing comment'
            })
            self.pos += 2
            return self.get_next_token()
        
        if self.pos < len(self.code):
            if self.pos < len(self.code) - 1:
                two_char = self.code[self.pos:self.pos+2]
                if two_char == '//':
                    self.pos += 2
                    while self.pos < len(self.code) and self.code[self.pos] != '\n':
                        self.pos += 1
                    return self.get_next_token()
                elif two_char == '/*':
                    start_line = self.line_number
                    self.pos += 2
                    closed = False
                    while self.pos < len(self.code):
                        if self.pos < len(self.code)-1 and self.code[self.pos:self.pos+2] == '*/':
                            self.pos += 2
                            closed = True
                            break
                        if self.code[self.pos] == '\n':
                            self.line_number += 1
                        self.pos += 1
                    if not closed:
                        self.errors.append({'line': start_line, 'error_str': '/*', 'message': 'Open comment at EOF'})
                        return ('SYMBOL', '$')
                    return self.get_next_token()
                elif two_char == '==':
                    self.pos += 2
                    return ('SYMBOL', '==')
            
            ch = self.code[self.pos]
            if ch in ';:,[](){}+-*/=<':
                self.pos += 1
                return ('SYMBOL', ch)
        
        if self.code[self.pos].isdigit():
            num_str = ''
            while self.pos < len(self.code) and self.code[self.pos].isdigit():
                num_str += self.code[self.pos]
                self.pos += 1
            return ('NUM', num_str)

        if self.code[self.pos].isalpha() or self.code[self.pos] == '_':
            id_str = ''
            while self.pos < len(self.code) and (self.code[self.pos].isalnum() or self.code[self.pos] == '_'):
                id_str += self.code[self.pos]
                self.pos += 1
            if id_str in self.keywords:
                return ('KEYWORD', id_str)
            return ('ID', id_str)

        self.errors.append({
            'line': self.line_number, 'error_str': self.code[self.pos], 'message': 'Illegal character'
        })
        self.pos += 1
        return self.get_next_token()

# ==========================================
#              PHASE 2: PARSER
# ==========================================

class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.current_token = None   
        self.token_val = None       
        self.token_tuple = None     
        self.syntax_errors = []
        self.root = None
        self.advance()

    def advance(self):
        self.token_tuple = self.scanner.get_next_token()
        token_type, token_value = self.token_tuple
        self.token_val = token_value
        
        if token_type in ['KEYWORD', 'SYMBOL']:
            self.current_token = token_value
        elif token_type in ['ID', 'NUM']:
            self.current_token = token_type
        elif token_value == '$':
            self.current_token = '$'

    def match(self, expected_token):
        if self.current_token == expected_token:
            if self.token_tuple[1] == '$':
                return Node("$")
            else:
                return Node(f"({self.token_tuple[0]}, {self.token_tuple[1]})")
            self.advance()
            return None # Return None when match is successful (node created manually if needed)
        else:
            self.report_error(f"missing {expected_token}")
            return None 

    # Override match to return the node created
    def match(self, expected_token):
        if self.current_token == expected_token:
            if self.token_tuple[1] == '$':
                node = Node("$")
            else:
                node = Node(f"({self.token_tuple[0]}, {self.token_tuple[1]})")
            self.advance()
            return node
        else:
            self.report_error(f"missing {expected_token}")
            return None

    def report_error(self, message):
        self.syntax_errors.append(f"#{self.scanner.line_number} : syntax error, {message}")

    # --- FIRST & FOLLOW SETS ---
    FIRST = {
        'Program': ['int', 'void', 'EPSILON'],
        'Declaration-list': ['int', 'void', 'EPSILON'],
        'Declaration': ['int', 'void'],
        'Declaration-initial': ['int', 'void'],
        'Declaration-prime': ['(', '[', ';'],
        'Var-declaration-prime': ['[', ';'],
        'Fun-declaration-prime': ['('],
        'Type-specifier': ['int', 'void'],
        'Params': ['int', 'void'],
        'Param-list': [',', 'EPSILON'],
        'Param': ['int', 'void'],
        'Param-prime': ['[', 'EPSILON'],
        'Compound-stmt': ['{'],
        'Statement-list': ['{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', 'EPSILON'],
        'Statement': ['{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM'],
        'Expression-stmt': ['break', ';', 'ID', '+', '-', '(', 'NUM'],
        'Selection-stmt': ['if'],
        'Else-stmt': ['else', 'EPSILON'],
        'Iteration-stmt': ['for'],
        'Return-stmt': ['return'],
        'Return-stmt-prime': [';', 'ID', '+', '-', '(', 'NUM'],
        'Expression': ['ID', '+', '-', '(', 'NUM'],
        'B': ['=', '[', '(', '*', '/', '+', '-', '==', '<', 'EPSILON'],
        'H': ['=', '*', '/', 'EPSILON', '+', '-', '==', '<'],
        'Simple-expression-zegond': ['+', '-', '(', 'NUM'],
        'Simple-expression-prime': ['(', '*', '/', '+', '-', '==', '<', 'EPSILON'],
        'C': ['==', '<', 'EPSILON'],
        'Relop': ['==', '<'],
        'Additive-expression': ['+', '-', '(', 'ID', 'NUM'],
        'Additive-expression-prime': ['(', '*', '/', '+', '-', 'EPSILON'],
        'Additive-expression-zegond': ['+', '-', '(', 'NUM'],
        'D': ['+', '-', 'EPSILON'],
        'Addop': ['+', '-'],
        'Term': ['+', '-', '(', 'ID', 'NUM'],
        'Term-prime': ['(', '*', '/', 'EPSILON'],
        'Term-zegond': ['+', '-', '(', 'NUM'],
        'G': ['*', '/', 'EPSILON'],
        'Signed-factor': ['+', '-', '(', 'ID', 'NUM'],
        'Signed-factor-zegond': ['+', '-', '(', 'NUM'],
        'Factor': ['(', 'ID', 'NUM'],
        'Var-call-prime': ['(', '[', 'EPSILON'],
        'Var-prime': ['[', 'EPSILON'],
        'Factor-prime': ['(', 'EPSILON'],
        'Factor-zegond': ['(', 'NUM'],
        'Args': ['ID', '+', '-', '(', 'NUM', 'EPSILON'],
        'Arg-list': ['ID', '+', '-', '(', 'NUM'],
        'Arg-list-prime': [',', 'EPSILON']
    }

    FOLLOW = {
        'Program': ['$'],
        'Declaration-list': ['$', '{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}'],
        'Declaration': ['int', 'void', '$', '{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}'],
        'Declaration-initial': ['(', '[', ';', ',', ')'],
        'Declaration-prime': ['int', 'void', '$', '{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}'],
        'Var-declaration-prime': ['int', 'void', '$', '{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}'],
        'Fun-declaration-prime': ['int', 'void', '$', '{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}'],
        'Type-specifier': ['ID'],
        'Params': [')'],
        'Param-list': [')'],
        'Param': [',', ')'],
        'Param-prime': [',', ')'],
        'Compound-stmt': ['int', 'void', '$', '{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'],
        'Statement-list': ['}'],
        'Statement': ['{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'],
        'Expression-stmt': ['{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'],
        'Selection-stmt': ['{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'],
        'Else-stmt': ['{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'],
        'Iteration-stmt': ['{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'],
        'Return-stmt': ['{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'],
        'Return-stmt-prime': ['{', 'break', ';', 'if', 'for', 'return', 'ID', '+', '-', '(', 'NUM', '}', 'else'],
        'Expression': [';', ')', ']', ','],
        'B': [';', ')', ']', ','],
        'H': [';', ')', ']', ','],
        'Simple-expression-zegond': [';', ')', ']', ','],
        'Simple-expression-prime': [';', ')', ']', ','],
        'C': [';', ')', ']', ','],
        'Relop': ['+', '-', '(', 'ID', 'NUM'],
        'Additive-expression': [';', ')', ']', ','],
        'Additive-expression-prime': ['==', '<', ';', ')', ']', ','],
        'Additive-expression-zegond': ['==', '<', ';', ')', ']', ','],
        'D': ['==', '<', ';', ')', ']', ','],
        'Addop': ['+', '-', '(', 'ID', 'NUM'],
        'Term': ['+', '-', ';', ')', '==', '<', ']', ','],
        'Term-prime': ['+', '-', '==', '<', ';', ')', ']', ','],
        'Term-zegond': ['+', '-', '==', '<', ';', ')', ']', ','],
        'G': ['+', '-', '==', '<', ';', ')', ']', ','],
        'Signed-factor': ['*', '/', '+', '-', ';', ')', '==', '<', ']', ','],
        'Signed-factor-zegond': ['*', '/', '+', '-', '==', '<', ';', ')', ']', ','],
        'Factor': ['*', '/', '+', '-', ';', ')', '==', '<', ']', ','],
        'Var-call-prime': ['*', '/', '+', '-', ';', ')', '==', '<', ']', ','],
        'Var-prime': ['*', '/', '+', '-', ';', ')', '==', '<', ']', ','],
        'Factor-prime': ['*', '/', '+', '-', '==', '<', ';', ')', ']', ','],
        'Factor-zegond': ['*', '/', '+', '-', '==', '<', ';', ')', ']', ','],
        'Args': [')'],
        'Arg-list': [')'],
        'Arg-list-prime': [')']
    }

    def check_error(self, non_terminal, follow_override=None):
        first_set = self.FIRST[non_terminal]
        follow_set = follow_override if follow_override is not None else self.FOLLOW[non_terminal]
        
        # 1. Success cases
        if self.current_token in first_set:
            return False
        if 'EPSILON' in first_set:
            if self.current_token in follow_set:
                return False
        
        # 2. Check FOLLOW (Missing Non-Terminal) - PRIORITIZE THIS
        if self.current_token in follow_set:
            self.report_error(f"missing {non_terminal}")
            return True # Caller should handle as epsilon/missing
        
        # 3. Illegal Token (Panic: Skip ONE token)
        self.report_error(f"illegal {self.current_token}")
        self.advance()
        
        # We skipped one token. Caller must try again or handle consequences.
        return False

    # --- GRAMMAR FUNCTIONS ---

    def parse_program(self):
        node = Node("Program")
        # Test 4 Fix: top_level=True
        child = self.parse_declaration_list(top_level=True)
        if child: child.parent = node
        
        if self.current_token == '$':
             Node("$", parent=node)
        
        with open('parse_tree.txt', 'w', encoding='utf-8') as f:
            for pre, fill, n in RenderTree(node):
                f.write("%s%s\n" % (pre, n.name))
            
        with open('syntax_errors.txt', 'w', encoding='utf-8') as f:
            if not self.syntax_errors:
                f.write("No syntax errors found.\n")
            else:
                for err in self.syntax_errors:
                    f.write(err + "\n")
        return node

    def parse_declaration_list(self, top_level=False):
        node = Node("Declaration-list")
        if self.current_token in self.FIRST['Declaration']: 
            node.add_child(self.parse_declaration())
            node.add_child(self.parse_declaration_list(top_level))
        elif self.current_token in self.FOLLOW['Declaration-list']:
            # Test 4 Fix: If at top level, '}' is NOT valid end
            if top_level and self.current_token == '}':
                self.report_error(f"illegal {self.current_token}")
                self.advance()
                # Recursion Guard
                if self.current_token in self.FIRST['Declaration']:
                    node.add_child(self.parse_declaration())
                    node.add_child(self.parse_declaration_list(top_level))
                else:
                    node.add_child(Node("epsilon"))
            else:
                node.add_child(Node("epsilon"))
        else:
            if not self.check_error('Declaration-list'):
                 # Recursion Guard
                 if self.current_token in self.FIRST['Declaration']:
                     node.add_child(self.parse_declaration())
                     node.add_child(self.parse_declaration_list(top_level))
                 else:
                     node.add_child(Node("epsilon"))
            else:
                 node.add_child(Node("epsilon"))
        return node

    def parse_declaration(self):
        node = Node("Declaration")
        if self.check_error('Declaration'): return node
        node.add_child(self.parse_declaration_initial())
        node.add_child(self.parse_declaration_prime())
        return node

    def parse_declaration_initial(self):
        node = Node("Declaration-initial")
        if self.check_error('Declaration-initial'): return node
        node.add_child(self.parse_type_specifier())
        node.add_child(self.match('ID'))
        return node

    def parse_declaration_prime(self):
        node = Node("Declaration-prime")
        if self.check_error('Declaration-prime'): return node
        if self.current_token in self.FIRST['Fun-declaration-prime']: 
            node.add_child(self.parse_fun_declaration_prime())
        elif self.current_token in self.FIRST['Var-declaration-prime']:
            node.add_child(self.parse_var_declaration_prime())
        else:
            self.report_error("Invalid declaration prime")
        return node

    def parse_var_declaration_prime(self):
        node = Node("Var-declaration-prime")
        if self.check_error('Var-declaration-prime'): return node
        if self.current_token == '[':
            node.add_child(self.match('['))
            node.add_child(self.match('NUM'))
            node.add_child(self.match(']'))
            node.add_child(self.match(';'))
        elif self.current_token == ';':
            node.add_child(self.match(';'))
        return node

    def parse_fun_declaration_prime(self):
        node = Node("Fun-declaration-prime")
        if self.check_error('Fun-declaration-prime'): return node
        node.add_child(self.match('('))
        node.add_child(self.parse_params())
        node.add_child(self.match(')'))
        node.add_child(self.parse_compound_stmt())
        return node

    def parse_type_specifier(self):
        node = Node("Type-specifier")
        if self.check_error('Type-specifier'): return node
        if self.current_token == 'int':
            node.add_child(self.match('int'))
        elif self.current_token == 'void':
            node.add_child(self.match('void'))
        return node

    def parse_params(self):
        node = Node("Params")
        if self.check_error('Params'): return node
        if self.current_token == 'int':
            node.add_child(self.match('int'))
            node.add_child(self.match('ID'))
            node.add_child(self.parse_param_prime())
            node.add_child(self.parse_param_list())
        elif self.current_token == 'void':
            node.add_child(self.match('void'))
        return node

    def parse_param_list(self):
        node = Node("Param-list")
        if self.current_token == ',':
            node.add_child(self.match(','))
            node.add_child(self.parse_param())
            node.add_child(self.parse_param_list())
        elif self.current_token in self.FOLLOW['Param-list']:
            node.add_child(Node("epsilon"))
        else:
            if not self.check_error('Param-list'):
                if self.current_token == ',':
                    node.add_child(self.match(','))
                    node.add_child(self.parse_param())
                    node.add_child(self.parse_param_list())
                else:
                    node.add_child(Node("epsilon"))
            else:
                node.add_child(Node("epsilon"))
        return node

    def parse_param(self):
        node = Node("Param")
        if self.check_error('Param'): return node
        node.add_child(self.parse_declaration_initial())
        node.add_child(self.parse_param_prime())
        return node

    def parse_param_prime(self):
        node = Node("Param-prime")
        if self.current_token == '[':
            node.add_child(self.match('['))
            node.add_child(self.match(']'))
        elif self.current_token in self.FOLLOW['Param-prime']:
             node.add_child(Node("epsilon"))
        else:
            if not self.check_error('Param-prime'):
                if self.current_token == '[':
                    node.add_child(self.match('['))
                    node.add_child(self.match(']'))
                else:
                    node.add_child(Node("epsilon"))
            else:
                node.add_child(Node("epsilon"))
        return node

    def parse_compound_stmt(self):
        node = Node("Compound-stmt")
        if self.check_error('Compound-stmt'): return node
        node.add_child(self.match('{'))
        node.add_child(self.parse_declaration_list())
        node.add_child(self.parse_statement_list())
        node.add_child(self.match('}'))
        return node

    def parse_statement_list(self):
        node = Node("Statement-list")
        if self.current_token in self.FIRST['Statement']:
            node.add_child(self.parse_statement())
            node.add_child(self.parse_statement_list())
        elif self.current_token in self.FOLLOW['Statement-list']:
            node.add_child(Node("epsilon"))
        else:
            if not self.check_error('Statement-list'):
                if self.current_token in self.FIRST['Statement']:
                    node.add_child(self.parse_statement())
                    node.add_child(self.parse_statement_list())
                else:
                    node.add_child(Node("epsilon"))
            else:
                node.add_child(Node("epsilon"))
        return node

    def parse_statement(self):
        node = Node("Statement")
        if self.check_error('Statement'): return node
        if self.current_token in self.FIRST['Expression-stmt']:
            node.add_child(self.parse_expression_stmt())
        elif self.current_token in self.FIRST['Compound-stmt']:
            node.add_child(self.parse_compound_stmt())
        elif self.current_token in self.FIRST['Selection-stmt']:
            node.add_child(self.parse_selection_stmt())
        elif self.current_token in self.FIRST['Iteration-stmt']:
            node.add_child(self.parse_iteration_stmt())
        elif self.current_token in self.FIRST['Return-stmt']:
            node.add_child(self.parse_return_stmt())
        else:
             self.report_error("Invalid statement")
        return node

    def parse_expression_stmt(self):
        node = Node("Expression-stmt")
        if self.check_error('Expression-stmt'): return node
        if self.current_token == 'break':
            node.add_child(self.match('break'))
            node.add_child(self.match(';'))
        elif self.current_token == ';':
            node.add_child(self.match(';'))
        else:
            node.add_child(self.parse_expression())
            node.add_child(self.match(';'))
        return node

    def parse_selection_stmt(self):
        node = Node("Selection-stmt")
        if self.check_error('Selection-stmt'): return node
        node.add_child(self.match('if'))
        node.add_child(self.match('('))
        node.add_child(self.parse_expression())
        node.add_child(self.match(')'))
        node.add_child(self.parse_statement())
        node.add_child(self.parse_else_stmt())
        return node

    def parse_else_stmt(self):
        node = Node("Else-stmt")
        if self.current_token == 'else':
            node.add_child(self.match('else'))
            node.add_child(self.parse_statement())
        elif self.current_token in self.FOLLOW['Else-stmt']:
            node.add_child(Node("epsilon"))
        else:
            if not self.check_error('Else-stmt'):
                if self.current_token == 'else':
                    node.add_child(self.match('else'))
                    node.add_child(self.parse_statement())
                else:
                    node.add_child(Node("epsilon"))
            else:
                node.add_child(Node("epsilon"))
        return node

    def parse_iteration_stmt(self):
        node = Node("Iteration-stmt")
        if self.check_error('Iteration-stmt'): return node
        node.add_child(self.match('for'))
        node.add_child(self.match('('))
        node.add_child(self.parse_expression())
        node.add_child(self.match(';'))
        node.add_child(self.parse_expression())
        node.add_child(self.match(';'))
        node.add_child(self.parse_expression())
        node.add_child(self.match(')'))
        node.add_child(self.parse_compound_stmt())
        return node

    def parse_return_stmt(self):
        node = Node("Return-stmt")
        if self.check_error('Return-stmt'): return node
        node.add_child(self.match('return'))
        node.add_child(self.parse_return_stmt_prime())
        return node

    def parse_return_stmt_prime(self):
        node = Node("Return-stmt-prime")
        if self.check_error('Return-stmt-prime'): return node
        if self.current_token == ';':
            node.add_child(self.match(';'))
        else:
            node.add_child(self.parse_expression())
            node.add_child(self.match(';'))
        return node

    def parse_expression(self):
        node = Node("Expression")
        if self.check_error('Expression'): return node
        if self.current_token == 'ID':
            node.add_child(self.match('ID'))
            node.add_child(self.parse_b())
        elif self.current_token in self.FIRST['Simple-expression-zegond']:
            node.add_child(self.parse_simple_expression_zegond())
        else:
             self.report_error("Invalid expression start")
        return node

    def parse_b(self):
        node = Node("B")
        if self.current_token == '=':
            node.add_child(self.match('='))
            node.add_child(self.parse_expression())
        elif self.current_token == '[':
            node.add_child(self.match('['))
            node.add_child(self.parse_expression())
            node.add_child(self.match(']'))
            node.add_child(self.parse_h())
        elif self.current_token in self.FIRST['Simple-expression-prime'] or self.current_token in self.FOLLOW['B']:
            node.add_child(self.parse_simple_expression_prime())
        else:
            # Fallback for B if nothing matches (it is nullable)
            node.add_child(self.parse_simple_expression_prime())
        return node

    def parse_h(self):
        node = Node("H")
        if self.current_token == '=':
            node.add_child(self.match('='))
            node.add_child(self.parse_expression())
        else:
            node.add_child(self.parse_g())
            node.add_child(self.parse_d())
            node.add_child(self.parse_c())
        return node

    def parse_simple_expression_zegond(self):
        node = Node("Simple-expression-zegond")
        if self.check_error('Simple-expression-zegond'): return node
        node.add_child(self.parse_additive_expression_zegond())
        node.add_child(self.parse_c())
        return node

    def parse_simple_expression_prime(self):
        node = Node("Simple-expression-prime")
        if self.current_token in self.FIRST['Additive-expression-prime']:
            node.add_child(self.parse_additive_expression_prime())
            node.add_child(self.parse_c())
        elif self.current_token in self.FOLLOW['Simple-expression-prime']:
             node.add_child(self.parse_additive_expression_prime())
             node.add_child(self.parse_c())
        else:
            if not self.check_error('Simple-expression-prime'):
                 node.add_child(self.parse_additive_expression_prime())
                 node.add_child(self.parse_c())
        return node

    def parse_c(self):
        node = Node("C")
        if self.current_token in self.FIRST['Relop']: 
            node.add_child(self.parse_relop())
            node.add_child(self.parse_additive_expression())
        elif self.current_token in self.FOLLOW['C']:
            node.add_child(Node("epsilon"))
        else:
            if not self.check_error('C'):
                if self.current_token in self.FIRST['Relop']:
                    node.add_child(self.parse_relop())
                    node.add_child(self.parse_additive_expression())
                else:
                    node.add_child(Node("epsilon"))
            else:
                node.add_child(Node("epsilon"))
        return node

    def parse_relop(self):
        node = Node("Relop")
        if self.check_error('Relop'): return node
        if self.current_token == '==':
            node.add_child(self.match('=='))
        elif self.current_token == '<':
            node.add_child(self.match('<'))
        return node

    def parse_additive_expression(self):
        if self.check_error('Additive-expression'): 
            return None
            
        node = Node("Additive-expression")
        node.add_child(self.parse_term())
        node.add_child(self.parse_d())
        return node

    def parse_additive_expression_prime(self):
        node = Node("Additive-expression-prime")
        node.add_child(self.parse_term_prime())
        node.add_child(self.parse_d())
        return node

    def parse_additive_expression_zegond(self):
        node = Node("Additive-expression-zegond")
        if self.check_error('Additive-expression-zegond'): return node
        node.add_child(self.parse_term_zegond())
        node.add_child(self.parse_d())
        return node

    def parse_d(self):
        node = Node("D")
        if self.current_token in self.FIRST['Addop']:
            node.add_child(self.parse_addop())
            node.add_child(self.parse_term())
            node.add_child(self.parse_d())
        elif self.current_token in self.FOLLOW['D']:
            node.add_child(Node("epsilon"))
        else:
            if not self.check_error('D'):
                if self.current_token in self.FIRST['Addop']:
                    node.add_child(self.parse_addop())
                    node.add_child(self.parse_term())
                    node.add_child(self.parse_d())
                else:
                    node.add_child(Node("epsilon"))
            else:
                node.add_child(Node("epsilon"))
        return node

    def parse_addop(self):
        node = Node("Addop")
        if self.check_error('Addop'): return node
        if self.current_token == '+':
            node.add_child(self.match('+'))
        elif self.current_token == '-':
            node.add_child(self.match('-'))
        return node

    def parse_term(self):
        node = Node("Term")
        if self.check_error('Term'): return node
        node.add_child(self.parse_signed_factor())
        node.add_child(self.parse_g())
        return node

    def parse_term_prime(self):
        node = Node("Term-prime")
        node.add_child(self.parse_factor_prime())
        node.add_child(self.parse_g())
        return node

    def parse_term_zegond(self):
        node = Node("Term-zegond")
        if self.check_error('Term-zegond'): return node
        node.add_child(self.parse_signed_factor_zegond())
        node.add_child(self.parse_g())
        return node

    def parse_g(self):
        node = Node("G")
        if self.current_token == '*':
            node.add_child(self.match('*'))
            node.add_child(self.parse_signed_factor())
            node.add_child(self.parse_g())
        elif self.current_token == '/':
            node.add_child(self.match('/'))
            node.add_child(self.parse_signed_factor())
            node.add_child(self.parse_g())
        elif self.current_token in self.FOLLOW['G']:
            node.add_child(Node("epsilon"))
        else:
             if not self.check_error('G'):
                 if self.current_token in ['*', '/']:
                     if self.current_token == '*':
                         node.add_child(self.match('*'))
                     else:
                         node.add_child(self.match('/'))
                     node.add_child(self.parse_signed_factor())
                     node.add_child(self.parse_g())
                 else:
                     node.add_child(Node("epsilon"))
             else:
                 node.add_child(Node("epsilon"))
        return node

    def parse_signed_factor(self):
        node = Node("Signed-factor")
        if self.check_error('Signed-factor'): return node
        if self.current_token == '+':
            node.add_child(self.match('+'))
            node.add_child(self.parse_factor())
        elif self.current_token == '-':
            node.add_child(self.match('-'))
            node.add_child(self.parse_factor())
        else:
            node.add_child(self.parse_factor())
        return node

    def parse_signed_factor_zegond(self):
        node = Node("Signed-factor-zegond")
        if self.check_error('Signed-factor-zegond'): return node
        if self.current_token == '+':
            node.add_child(self.match('+'))
            node.add_child(self.parse_factor())
        elif self.current_token == '-':
            node.add_child(self.match('-'))
            node.add_child(self.parse_factor())
        else:
            node.add_child(self.parse_factor_zegond())
        return node

    def parse_factor(self):
        node = Node("Factor")
        if self.check_error('Factor'): return node
        if self.current_token == '(':
            node.add_child(self.match('('))
            node.add_child(self.parse_expression())
            node.add_child(self.match(')'))
        elif self.current_token == 'ID':
            node.add_child(self.match('ID'))
            node.add_child(self.parse_var_call_prime())
        elif self.current_token == 'NUM':
            node.add_child(self.match('NUM'))
        else:
            self.report_error("Invalid factor")
        return node

    def parse_var_call_prime(self):
        node = Node("Var-call-prime")
        if self.current_token == '(':
            node.add_child(self.match('('))
            node.add_child(self.parse_args())
            node.add_child(self.match(')'))
        else:
            node.add_child(self.parse_var_prime())
        return node

    def parse_var_prime(self):
        node = Node("Var-prime")
        if self.current_token == '[':
            node.add_child(self.match('['))
            node.add_child(self.parse_expression())
            node.add_child(self.match(']'))
        elif self.current_token in self.FOLLOW['Var-prime']:
            node.add_child(Node("epsilon"))
        else:
            if not self.check_error('Var-prime'):
                if self.current_token == '[':
                    node.add_child(self.match('['))
                    node.add_child(self.parse_expression())
                    node.add_child(self.match(']'))
                else:
                    node.add_child(Node("epsilon"))
            else:
                node.add_child(Node("epsilon"))
        return node

    def parse_factor_prime(self):
        node = Node("Factor-prime")
        if self.current_token == '(':
            node.add_child(self.match('('))
            node.add_child(self.parse_args())
            node.add_child(self.match(')'))
        elif self.current_token in self.FOLLOW['Factor-prime']:
            node.add_child(Node("epsilon"))
        else:
             if not self.check_error('Factor-prime'):
                 if self.current_token == '(':
                     node.add_child(self.match('('))
                     node.add_child(self.parse_args())
                     node.add_child(self.match(')'))
                 else:
                     node.add_child(Node("epsilon"))
             else:
                 node.add_child(Node("epsilon"))
        return node

    def parse_factor_zegond(self):
        node = Node("Factor-zegond")
        if self.check_error('Factor-zegond'): return node
        if self.current_token == '(':
            node.add_child(self.match('('))
            node.add_child(self.parse_expression())
            node.add_child(self.match(')'))
        elif self.current_token == 'NUM':
            node.add_child(self.match('NUM'))
        return node

    def parse_args(self):
        node = Node("Args")
        if self.current_token in self.FIRST['Arg-list']:
            node.add_child(self.parse_arg_list())
        elif self.current_token in self.FOLLOW['Args']:
            node.add_child(Node("epsilon"))
        else:
             if not self.check_error('Args'):
                  if self.current_token in self.FIRST['Arg-list']:
                      node.add_child(self.parse_arg_list())
                  else:
                      node.add_child(Node("epsilon"))
             else:
                  node.add_child(Node("epsilon"))
        return node

    def parse_arg_list(self):
        node = Node("Arg-list")
        if self.check_error('Arg-list'): return node
        node.add_child(self.parse_expression())
        node.add_child(self.parse_arg_list_prime())
        return node

    def parse_arg_list_prime(self):
        node = Node("Arg-list-prime")
        if self.current_token == ',':
            node.add_child(self.match(','))
            node.add_child(self.parse_expression())
            node.add_child(self.parse_arg_list_prime())
        elif self.current_token in self.FOLLOW['Arg-list-prime']:
            node.add_child(Node("epsilon"))
        else:
            if not self.check_error('Arg-list-prime'):
                 if self.current_token == ',':
                     node.add_child(self.match(','))
                     node.add_child(self.parse_expression())
                     node.add_child(self.parse_arg_list_prime())
                 else:
                     node.add_child(Node("epsilon"))
            else:
                 node.add_child(Node("epsilon"))
        return node

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'input.txt')
    
    if not os.path.exists(input_file):
        print(f"Error: input.txt not found in {script_dir}")
        return
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading input.txt: {e}")
        return
    
    scanner = Scanner(code)
    parser = Parser(scanner)
    parser.parse_program()
    # print("Compilation completed.")

if __name__ == '__main__':
    main()