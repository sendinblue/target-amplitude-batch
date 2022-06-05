#!/usr/bin/env python3

import argparse
import io
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Optional

from jsonschema.validators import Draft4Validator
import singer
from adjust_precision_for_schema import adjust_decimal_precision_for_schema

from amplitude import Amplitude, BaseEvent, Config

logger = logging.getLogger(__name__)


class MessageType(Exception):
    pass


class EventType(Exception):
    pass


class UserIdException(Exception):
    pass


class EventTrack(Exception):
    pass


class BuildEvent(Exception):
    pass


def emit_state(state):
    if state is not None:
        line = json.dumps(state)
        logger.debug("Emitting state {}".format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()


def convert_to_timestamp_millis(dt):
    return int(datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S+00:00").timestamp()) * 1000


def callback_function(event, code, message=None):
    """
    A callback function
    :param event: the event that triggered this callback
    :param code: status code of request response
    :param message: a optional string message for more detailed information
    :return: None
    """
    logger.info("event {}".format(event))
    logger.info("code: {} \n message: {}".format(code, message))


def persist_events(
    messages: io.TextIOWrapper,
    config: Optional[Dict],
) -> Dict:
    state = None
    schemas = {}
    key_properties = {}
    validators = {}

    amp_configuration = Config(
        flush_queue_size=config["flush_queue_size"],
        flush_interval_millis=config["flush_interval_millis"],
        flush_max_retries=config["flush_max_retries"],
        use_batch=config["use_batch"],
        callback=callback_function,
        logger=logger,
    )

    amplitude_client = Amplitude(
        api_key=config["api_key"], configuration=amp_configuration
    )

    for message in messages:
        try:
            o = singer.parse_message(message).asdict()

            message_type = o["type"]
            if message_type == "RECORD":
                if o["stream"] not in schemas:
                    raise MessageType(
                        "A record for stream {}"
                        "was encountered before a corresponding schema ".format(
                            o["stream"]
                        )
                    )

                validators[o["stream"]].validate((o["record"]))

                # Build event
                event_raw = o["record"]

                # check for mandatory fields
                if "user_id" not in event_raw.keys():
                    if "device_id" not in event_raw.keys():
                        raise UserIdException(
                            "user_id or device_id must be specified in: \n{}".format(
                                event_raw
                            )
                        )

                if "event_type" not in event_raw.keys():
                    raise EventType(
                            "event_type must be specified in: \n{}".format(
                                event_raw
                            )
                        )

                if len(event_raw["user_id"]) < 5:
                    raise UserIdException(
                        "A user_id must have a minimum length of 5 characters in: \n{}".format(
                            event_raw
                        )
                    )

                if event_raw["time"]:
                    event_raw["time"] = convert_to_timestamp_millis(event_raw["time"])

                # clean BigQuery meta data
                bq_meta_to_remove = (
                    "_sdc_extracted_at",
                    "_sdc_batched_at",
                    "_etl_tstamp",
                )
                for k in bq_meta_to_remove:
                    event_raw.pop(k, None)

                # Create a BaseEvent instance
                event = BaseEvent(event_type=event_raw["event_type"])

                # Set event attributes
                for key in event_raw.keys():
                    if key not in event.__dict__:
                        raise BuildEvent(
                            "Unexpected event property key: {}".format(key)
                        )

                    event[key] = event_raw[key]

                amplitude_client.track(event)

                state = None
            elif message_type == "STATE":
                logger.debug("Setting state to {}".format(o["value"]))
                state = o["value"]
            elif message_type == "SCHEMA":
                stream = o["stream"]
                schemas[stream] = o["schema"]
                adjust_decimal_precision_for_schema(schemas[stream])
                validators[stream] = Draft4Validator((o["schema"]))
                key_properties[stream] = o["key_properties"]
            else:
                logger.warning(
                    "Unknown message type {} in message {}".format(o["type"], o)
                )

        except json.decoder.JSONDecodeError:
            logger.error("Unable to parse:\n{}".format(message))
            raise
        except MessageType:
            raise
        except UserIdException:
            raise
        except EventType:
            raise
        except BuildEvent:
            raise
        except Exception as err:
            logger.error(err)
            raise
        finally:
            amplitude_client.flush()

    amplitude_client.shutdown()
    return state


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Config file")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as config:
            config = json.load(config)
    else:
        config = {}

    input_messages = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")

    if config is not None:
        state = persist_events(input_messages, config)
        emit_state(state)
        logger.debug("Exiting normally")
    else:
        raise Exception("a config file must be filled in")


if __name__ == "__main__":
    main()
