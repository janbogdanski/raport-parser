#!/usr/bin/python
# -*- coding: utf-8 -*-
arr = ['text1', 'text2', 'text3']
texts = ['block 1 \nssssssss text2', 'block 2 \nbababa', 'block 3 \n text3']
a = []
for text in texts:
	b = [text for x, y in enumerate(arr) if str(y) in text]
	if len(b) > 0:
		a.append(b)

	
print a
print type(arr)