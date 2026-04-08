"""
Broken application example for testing the healing system.
This app contains deliberate errors that will trigger the healing mechanism.
"""


def calculate_average(numbers):
    """Calculate average of a list of numbers."""
    total = sum(numbers)
    count = len(numbers)
    # Deliberate bug: division by zero when empty list
    return total / count


def get_user_data(user_id):
    """Fetch user data from a mock database."""
    users = {
        1: {"name": "Alice", "age": 30},
        2: {"name": "Bob", "age": 25},
    }
    # Deliberate bug: KeyError when user_id doesn't exist
    return users[user_id]


def process_data():
    """Main processing function with multiple error scenarios."""
    print("Starting data processing...")
    
    # Scenario 1: ZeroDivisionError
    try:
        result = calculate_average([])
        print(f"Average: {result}")
    except ZeroDivisionError as e:
        print(f"Error calculating average: {e}")
    
    # Scenario 2: KeyError
    try:
        user = get_user_data(999)
        print(f"User: {user}")
    except KeyError as e:
        print(f"Error fetching user: {e}")
    
    # Scenario 3: Successful operation
    result = calculate_average([10, 20, 30, 40, 50])
    print(f"Valid average: {result}")
    
    user = get_user_data(1)
    print(f"Valid user: {user}")


if __name__ == "__main__":
    process_data()

# Made with Bob
