from notebook_preamble import J, D, DefinitionWrapper, V

#J('[0 swap [dup [pop 14811] [] branch dup [3 &] dip 2 >>] dip rest cons] 466 [x] times pop enstacken sum')


DefinitionWrapper.add_definitions('''

  direco == dip rest cons
  G == [direco] cons [swap] swoncat cons

  PE1.1 == dup [3 &] dip 2 >>
  PE1.1.check == dup [pop 14811] [] branch
  PE1.2 == + dup [+] dip

  PE1 == 0 0 0 [PE1.1.check PE1.1] G 466 [x [PE1.2] dip] times popop

  ''', D)

V('PE1')


# If the cleave combinator is built-in then this should be faster:
#
#    PE1.1 ==  [3 &] [2 >>] cleave
