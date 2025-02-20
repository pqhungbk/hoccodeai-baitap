
def sum_three_numbers():
    """
    This function prompts the user to input three numbers and calculates their sum.
    It also includes input validation to ensure that the inputs are numeric.
    """

    # Initialize an empty list to store the numbers
    numbers = []

    # Loop until we have three valid numbers
    while len(numbers) < 3:
        # Prompt the user to enter a number
        user_input = input(f"Nhập số {len(numbers) + 1}/3: ")

        # Validate input
        try:
            # Convert input to float and append to the list
            number = float(user_input)
            numbers.append(number)
        except ValueError:
            print("Giá trị không hợp lệ. Vui lòng nhập một số.")

    # Calculate the sum of the three numbers
    total_sum = sum(numbers)

    # Output the result
    print(f"Tổng của ba số là: {total_sum}")

# Call the function to execute the program
if __name__ == "__main__":
    sum_three_numbers()
