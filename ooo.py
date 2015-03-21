from joy.godelish import *


S0 = text_to_expression('0')
S1 = text_to_expression('1')
Si = text_to_expression('23')
E = 9, (18, (Si, (S1, (S0, (ifte, (44, ()))))))
s = E, ((1, ()), (3, (4, ())))
e = infra, (7, (8, ()))
print_trace(J((), E, ())[0], ())








