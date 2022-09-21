import io
import sys

import singer
from adjust_precision_for_schema import adjust_decimal_precision_for_schema
from jsonschema.validators import Draft4Validator

import unittestcore


class MyTestCase(unittestcore.BaseUnitTest):
    def test_schema_validation(self):
        self.init_config('chargebee_stream.json')

        tap_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        count_lines = 0
        state = None
        schemas = {}
        key_properties = {}
        validators = {}
        for message in tap_stream:
            o = singer.parse_message(message).asdict()
            message_type = o["type"]

            if message_type == "RECORD":
                if o["stream"] not in schemas:
                    self.assertError(
                        "A record for stream {}"
                        "was encountered before a corresponding schema ".format(
                            o["stream"]
                        )
                    )

                validators[o["stream"]].validate((o["record"]))

                # Build event
                event_raw = o["record"]
            elif message_type == "STATE":
                print("Setting state to {}".format(o["value"]))
                state = o["value"]
            elif message_type == "SCHEMA":
                stream = o["stream"]
                schemas[stream] = o["schema"]
                adjust_decimal_precision_for_schema(schemas[stream])
                validators[stream] = Draft4Validator((o["schema"]))
                key_properties[stream] = o["key_properties"]
            else:
                print(
                    "Unknown message type {} in message {}".format(o["type"], o)
                )
        #self.assertEqual(True, False)  # add assertion here

