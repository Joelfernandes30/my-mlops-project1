from src.logger import get_logger
from src.custom_exception import CustomException

import sys

logger = get_logger(__name__)


def divide_numbers(num1, num2):
    try:
        result =  num1 / num2
        logger.info(f"Divided {num1} by {num2} successfully.") 
        return result 
    except ZeroDivisionError as e:
        logger.error(f"ZeroDivisionError: {e}")
        raise CustomException("Attempted to divide by zero Joel", sys) from e
    
if __name__ == "__main__":
    try:
        logger.info("Starting division operation.")
        print(divide_numbers(10, 0))
    except CustomException as e:
        logger.error(f"CustomException caught: {e}")
        print(e)