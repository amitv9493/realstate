import logging
from functools import wraps
from time import perf_counter

from realstate_new.task.models import ThirdPartyCall

logger = logging.getLogger(__name__)


def log_api(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        response = func(*args, **kwargs)
        end_time = perf_counter() - start_time
        msg = f"calling {response.url} in {end_time:.2f} seconds"
        logger.info(msg)
        ThirdPartyCall.objects.create(
            status_code=response.status_code,
            request_body=response.request.body,
            response_body=response.text,
            endpoint=response.url,
            time_taken=end_time,
        )
        return response

    return wrapper
