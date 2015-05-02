from pyparsing import *

salutation     = Word( alphas + "'" )
comma          = Literal(",")
greetee        = Word( alphas )
endPunctuation = Literal("!")

greeting = salutation + comma + greetee + endPunctuation
tests = ("   Hello, World! asd", 
"	 Whattup, Dude!" )

for t in tests:
        print t, "->", greeting.parseString(t)


type = Literal("RV")
docNo = Word(alphas)
separator = White("")
rest = Word(alphanums )
r = type  + separator

 
f = open("rejestr")
rejestr = f.read()
line = rejestr.splitlines()
for line in iter(rejestr.splitlines()):
	print line.split("\t")



class SapRecord:
	docNo
	ref
	date1
	date2
	date3
	taxRate
	gross
	net
	taxVal
