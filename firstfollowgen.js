const firstFollow = require('first-follow');

const rules = [
    // Program
    { left: 'Program', right: ['Declaration-list'] },
  
    // Declaration-list
    { left: 'Declaration-list', right: ['Declaration', 'Declaration-list'] },
    { left: 'Declaration-list', right: [null] },
  
    // Declaration
    { left: 'Declaration', right: ['Declaration-initial', 'Declaration-prime'] },
  
    // Declaration-initial
    { left: 'Declaration-initial', right: ['Type-specifier', 'ID'] },
  
    // Declaration-prime
    { left: 'Declaration-prime', right: ['Fun-declaration-prime'] },
    { left: 'Declaration-prime', right: ['Var-declaration-prime'] },
  
    // Var-declaration-prime
    { left: 'Var-declaration-prime', right: ['[', 'NUM', ']', ';'] },
    { left: 'Var-declaration-prime', right: [';'] },
  
    // Fun-declaration-prime
    { left: 'Fun-declaration-prime', right: ['(', 'Params', ')', 'Compound-stmt'] },
  
    // Type-specifier
    { left: 'Type-specifier', right: ['int'] },
    { left: 'Type-specifier', right: ['void'] },
  
    // Params
    { left: 'Params', right: ['int', 'ID', 'Param-prime', 'Param-list'] },
    { left: 'Params', right: ['void'] },
  
    // Param-list
    { left: 'Param-list', right: [',', 'Param', 'Param-list'] },
    { left: 'Param-list', right: [null] },
  
    // Param
    { left: 'Param', right: ['Declaration-initial', 'Param-prime'] },
  
    // Param-prime
    { left: 'Param-prime', right: ['[', ']'] },
    { left: 'Param-prime', right: [null] },
  
    // Compound-stmt
    { left: 'Compound-stmt', right: ['{', 'Declaration-list', 'Statement-list', '}'] },
  
    // Statement-list
    { left: 'Statement-list', right: ['Statement', 'Statement-list'] },
    { left: 'Statement-list', right: [null] },
  
    // Statement
    { left: 'Statement', right: ['Expression-stmt'] },
    { left: 'Statement', right: ['Compound-stmt'] },
    { left: 'Statement', right: ['Selection-stmt'] },
    { left: 'Statement', right: ['Iteration-stmt'] },
    { left: 'Statement', right: ['Return-stmt'] },
  
    // Expression-stmt
    { left: 'Expression-stmt', right: ['Expression', ';'] },
    { left: 'Expression-stmt', right: ['break', ';'] },
    { left: 'Expression-stmt', right: [';'] },
  
    // Selection-stmt
    { left: 'Selection-stmt', right: ['if', '(', 'Expression', ')', 'Statement', 'Else-stmt'] },
  
    // Else-stmt
    { left: 'Else-stmt', right: ['else', 'Statement'] },
    { left: 'Else-stmt', right: [null] },
  
    // Iteration-stmt
    { left: 'Iteration-stmt', right: ['for', '(', 'Expression', ';', 'Expression', ';', 'Expression', ')', 'Compound-stmt'] },
  
    // Return-stmt
    { left: 'Return-stmt', right: ['return', 'Return-stmt-prime'] },
  
    // Return-stmt-prime
    { left: 'Return-stmt-prime', right: ['Expression', ';'] },
    { left: 'Return-stmt-prime', right: [';'] },
  
    // Expression
    { left: 'Expression', right: ['Simple-expression-zegond'] },
    { left: 'Expression', right: ['ID', 'B'] },
  
    // B
    { left: 'B', right: ['=', 'Expression'] },
    { left: 'B', right: ['[', 'Expression', ']', 'H'] },
    { left: 'B', right: ['Simple-expression-prime'] },
  
    // H
    { left: 'H', right: ['=', 'Expression'] },
    { left: 'H', right: ['G', 'D', 'C'] },
  
    // Simple-expression-zegond
    { left: 'Simple-expression-zegond', right: ['Additive-expression-zegond', 'C'] },
  
    // Simple-expression-prime
    { left: 'Simple-expression-prime', right: ['Additive-expression-prime', 'C'] },
  
    // C
    { left: 'C', right: ['Relop', 'Additive-expression'] },
    { left: 'C', right: [null] },
  
    // Relop
    { left: 'Relop', right: ['=='] },
    { left: 'Relop', right: ['<'] },
  
    // Additive-expression
    { left: 'Additive-expression', right: ['Term', 'D'] },
  
    // Additive-expression-prime
    { left: 'Additive-expression-prime', right: ['Term-prime', 'D'] },
  
    // Additive-expression-zegond
    { left: 'Additive-expression-zegond', right: ['Term-zegond', 'D'] },
  
    // D
    { left: 'D', right: ['Addop', 'Term', 'D'] },
    { left: 'D', right: [null] },
  
    // Addop
    { left: 'Addop', right: ['+'] },
    { left: 'Addop', right: ['-'] },
  
    // Term
    { left: 'Term', right: ['Signed-factor', 'G'] },
  
    // Term-prime
    { left: 'Term-prime', right: ['Factor-prime', 'G'] },
  
    // Term-zegond
    { left: 'Term-zegond', right: ['Signed-factor-zegond', 'G'] },
  
    // G
    { left: 'G', right: ['*', 'Signed-factor', 'G'] },
    { left: 'G', right: ['/', 'Signed-factor', 'G'] },
    { left: 'G', right: [null] },
  
    // Signed-factor
    { left: 'Signed-factor', right: ['+', 'Factor'] },
    { left: 'Signed-factor', right: ['-', 'Factor'] },
    { left: 'Signed-factor', right: ['Factor'] },
  
    // Signed-factor-zegond
    { left: 'Signed-factor-zegond', right: ['+', 'Factor'] },
    { left: 'Signed-factor-zegond', right: ['-', 'Factor'] },
    { left: 'Signed-factor-zegond', right: ['Factor-zegond'] },
  
    // Factor
    { left: 'Factor', right: ['(', 'Expression', ')'] },
    { left: 'Factor', right: ['ID', 'Var-call-prime'] },
    { left: 'Factor', right: ['NUM'] },
  
    // Var-call-prime
    { left: 'Var-call-prime', right: ['(', 'Args', ')'] },
    { left: 'Var-call-prime', right: ['Var-prime'] },
  
    // Var-prime
    { left: 'Var-prime', right: ['[', 'Expression', ']'] },
    { left: 'Var-prime', right: [null] },
  
    // Factor-prime
    { left: 'Factor-prime', right: ['(', 'Args', ')'] },
    { left: 'Factor-prime', right: [null] },
  
    // Factor-zegond
    { left: 'Factor-zegond', right: ['(', 'Expression', ')'] },
    { left: 'Factor-zegond', right: ['NUM'] },
  
    // Args
    { left: 'Args', right: ['Arg-list'] },
    { left: 'Args', right: [null] },
  
    // Arg-list
    { left: 'Arg-list', right: ['Expression', 'Arg-list-prime'] },
  
    // Arg-list-prime
    { left: 'Arg-list-prime', right: [',', 'Expression', 'Arg-list-prime'] },
    { left: 'Arg-list-prime', right: [null] }
  ];


// Correct way to use the library
const result = firstFollow(rules);

// Destructure the result correctly
const { firstSets, followSets, predictSets } = result;

// Now log the sets
console.log('FIRST sets:', firstSets);
console.log('FOLLOW sets:', followSets);
console.log('PREDICT sets:', predictSets);