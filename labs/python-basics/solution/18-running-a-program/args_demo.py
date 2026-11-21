# Chapter 18: what does a program receive from the command line? Run it with some words after its name.
import sys

print("program:", sys.argv[0])
print("arguments:", sys.argv[1:])
