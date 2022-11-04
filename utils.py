import sys
import json
import logging

import pytz
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


def emit_state(state: Dict) -> None:
    """
    Write state in stdout
    :param state:
    :return: write state in stdout
    """
    if state is not None:
        line = json.dumps(state)
        logger.debug("Emitting state {}".format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()


def convert_to_timestamp_millis(dt) -> int:
    """
    Convert DateTime object to epoch DateTime in milliseconds
    :param dt: DateTime object
    :return: epoch DateTime in milliseconds
    """
    dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S+00:00").replace(tzinfo=pytz.utc)
    return int(dt.timestamp()) * 1000


def to_float(value) -> float:
    """
    enforce value to be float
    :param value: to be casted
    :return: value casted to float
    """
    return float(value)


def callback_function(event, code, message=None) -> None:
    """
    A callback function
    :param event: the event that triggered this callback
    :param code: status code of request response
    :param message: a optional string message for more detailed information
    :return: None
    """
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(
        "upload time {}\n event {}\n response code: {}\n response message: {}".format(
            now, event, code, message
        )
    )
