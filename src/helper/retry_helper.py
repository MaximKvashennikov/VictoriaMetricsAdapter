import time
import logging
from typing import Callable, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class RetryHelper:
    """
    A helper class to execute a function with retry attempts based on specified conditions.
    """

    def __init__(
        self,
        max_retries: int,
        delay: float,
        retry_condition: Optional[Callable[[Exception], bool]] = None,
        on_retry: Optional[Callable[[int, Exception], None]] = None,
    ):
        """
        Initializes the RetryHelper instance.

        :param max_retries: Maximum number of retries.
        :param delay: Delay in seconds between retries.
        :param retry_condition: Function to determine retry eligibility based on exception.
        :param on_retry: Callback for each retry attempt.
        """
        self.max_retries = max_retries
        self.delay = delay
        self.retry_condition = retry_condition
        self.on_retry = on_retry

    def execute(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Executes the provided function with retries.

        :param func: The function to execute.
        :param args: Positional arguments to pass to the function.
        :param kwargs: Keyword arguments to pass to the function.
        :return: The result of the function execution.
        :raises Exception: The last exception raised if retries are exhausted.
        """
        attempt = 0
        while attempt <= self.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries or (self.retry_condition and not self.retry_condition(e)):
                    raise
                attempt += 1
                if self.on_retry:
                    self.on_retry(attempt, e)
                time.sleep(self.delay)


def log_retry(attempt: int, exception: Exception) -> None:
    """
    Logs the retry attempt and exception details.

    :param attempt: The current retry attempt.
    :param exception: The exception that caused the retry.
    """
    message = f"Retry {attempt}: {exception}"
    logging.warning(message)


# Example usage
def example_function(x: int, y: int) -> int:
    """
    A sample function to demonstrate retries.

    :param x: The first integer.
    :param y: The second integer.
    :return: The result of subtracting y from x.
    :raises ValueError: If x is less than y.
    """
    if x < y:
        raise ValueError("x must be greater than or equal to y")
    return x - y


if __name__ == "__main__":
    # Retry helper configuration
    retry_helper = RetryHelper(
        max_retries=3,
        delay=2.0,
        retry_condition=lambda error: isinstance(error, ValueError),
        on_retry=log_retry,
    )

    try:
        result = retry_helper.execute(example_function, 1, 3)
        print(f"Function executed successfully: Result = {result}")
    except Exception as final_exception:
        print(f"Function failed after retries: {final_exception}")
