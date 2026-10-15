# Ask the user for a number
# Use a while loop to keep reversing its digits and adding until the result becomes a palindrome

# First, use an example to understand how adding a number with its reverse can create a Palindrome. Assume that our number is 1389:
# 1389 -> 9831 (not a palindrome)
# 9831 + 1389 = 10239 -> 93201 (not a palindrome)
# 93201 + 10239 = 102630 -> 036201 (not a palindrome)
# 036201 + 102630 = 138831 -> 138831 (a palindrome, bingo!)

# So we just need to keep reversing and adding to the original number until a palindrome is formed.


def is_palindrome(num):
    return str(num) == str(num)[::-1]


def reverse_number(num):
    return int(str(num)[::-1])


def processing_palindrom(num):
    if not is_palindrome(num):
        reverse_num = reverse_number(num)
        num += reverse_num
        print(f"{reverse_num} + {num - reverse_num} = {num}")
        processing_palindrom(num)
    else:
        print(f"Palindrome found: {num}")


number = int(input("Enter a number (at least two digits): "))
# while not is_palindrome(number):
#     reversed_num = reverse_number(number)
#     number += reversed_num
#     print(f"{reversed_num} + {number - reversed_num} = {number}")
# print(f"Palindrome found: {number}")

if number < 10:
    print("Please enter a number with at least two digits.")
else:
    processing_palindrom(number)
