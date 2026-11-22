# Chapter 2: two functions that look alike. One prints, one returns. Run it and compare a and b.
def shout_print(word):
    print(word.upper() + "!")


def shout_return(word):
    return word.upper() + "!"


a = shout_print("hello")
b = shout_return("hello")
print("a is", a)
print("b is", b)
