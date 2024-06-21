from django.test import TestCase

#Sual 2
# def determine_quadrant(x, y):
#     if x > 0 and y > 0:
#         return "1-ci rüb"
#     elif x < 0 and y > 0:
#         return "2-ci rüb"
#     elif x < 0 and y < 0:
#         return "3-cü rüb"
#     elif x > 0 and y < 0:
#         return "4-cü rüb"
#     else:
#         return "Nöqtə oxlardan birinin üzərindədir"

# x = int(input("x dəyərini daxil edin: "))
# y = int(input("y dəyərini daxil edin: "))
# print(determine_quadrant(x, y))

#Sual 3
# def replace_with_indices(input_string):
#     result = ''
#     for i, char in enumerate(input_string):
#         if char.isalpha():
#             result += str(i)
#         else:
#             result += char
#     return result

# input_string = input("Mətni daxil edin: ")
# print(replace_with_indices(input_string))

#Sual 1
# def calculate_series(n):
#     S = 0
#     for i in range(1, n + 1):
#         term = (-1)**i * 2 * i
#         S += term
#     return S

# n = int(input("n-i daxil et: "))
# print(calculate_series(n))