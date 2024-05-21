import logging
from time import sleep

logger = logging.getLogger(__name__)


def repeat_on_fail(description, try_count=3, sleep_time=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(try_count):
                try:
                    logger.info(f'{description}: Try {attempt + 1} of {try_count}')
                    result = func(*args, **kwargs)
                    logger.info(f'{description} completed')
                    return result
                except Exception as e:
                    logger.warning(f'Error was occurred during {description}: {str(e)}')

                sleep(sleep_time)

            raise RuntimeError(f'Cannot {description}')

        return wrapper
    return decorator
