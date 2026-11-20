# Chapter 3: making decisions.


def grade(marks: int) -> str:
    if marks < 0 or marks > 100:
        return "Invalid"
    if marks >= 80:
        return "A"
    elif marks >= 60:
        return "B"
    elif marks >= 40:
        return "C"
    else:
        return "F"


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
