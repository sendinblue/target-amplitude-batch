
# target-amplitude

This is a [Singer](https://singer.io) target that reads JSON-formatted data from Google BigQuery and send it to Amplitude APIs.
following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

[![Python package](https://github.com/adswerve/target-bigquery/actions/workflows/python-package.yml/badge.svg)](https://github.com/HichemELB/target-amplitude-batch/blob/main/.github/workflows/python-publish.yml)


## Contents

- [Install target-amplitude-batch](#dependencies)
- [How to use it](#how-to-use-it)
    - [Step 1: Set up tap-bigquery](#step-1-set-up-tap-bigquery)
    - [Step 2: Add tap config file](#step-2-add-tap-config-file)
    - [Step 3: Create catalog](#step-3-create-catalog)
    - [Step 3: Run](#step-4-run)
- [State](#State)


## Install target-amplitude-batch

1. Run the following command. 
It runs *setup.py* and installs target-amplitude-batch into the virtual prepared env, 
**-e** emulates how a user of the package would install requirements.

```
pip install -e .
```
2. Add the config.json file in the working directory, following config.sample.json:
```json
{
  "api_key": "Amplitude api_key of the projectID to which we want to send the data",
  "flush_queue_size": 10000,
  "flush_interval_millis": 1000,
  "flush_max_retries": 12,
  "use_batch": true,
  "is_batch_identify": false,
  "is_schemaless": false
}
```

## How to use it

### Step 1: Set up tap-bigquery
1. Please follow the description [here](https://github.com/anelendata/tap-bigquery#installation)

### Step 2: Add tap config file
Create a file called tap_config.json in the working directory:
```JSON
{
  "streams": [
      {"name": "<some_schema_name>",
       "table": "`<project>.<dataset>.<table>`",
       "columns": ["<col_name_0>", "<col_name_1>", "<col_name_2>"],
       "datetime_key": "<your_key>",
       "filters": ["country='us'", "state='CA'",
                   "registered_on>=DATE_ADD(current_date, INTERVAL -7 day)"
                  ] // also optional: these are parsed in 'WHERE' clause
      }
    ],
  "start_datetime": "2017-01-01T00:00:00Z", // This can be set at the command line argument
  "end_datetime": "2017-02-01T00:00:00Z", // end_datetime is optional
  "limit": 100,
  "start_always_inclusive": false // default is false, optional
}
```
- The required parameters is at least one stream (one bigquery table/view) to copy. 
  - It is not a recommended BigQuery practice to use `*` to specify the columns as it may blow up the cost for a table with a large number of columns.

  - `filters` are optional but strongly recommend using this over a large partitioned table to control the cost. LIMIT (The authors of tap-bigquery is not responsible for the cost incurred by running this program. Always test thoroughly with small data set first.
  - `start_datetime` must also be set in the config file or as the command line argument (See the next step).
  - `limit` will limit the number of results, but it does not result in reduce the query cost.

The table/view is expected to have a column to indicate the creation or update date and time so the tap sends the query with `ORDER BY and use the column to record the bookmark (See State section).

### Step 3: Create catalog
Run tap-bigquery in discovery mode to let it create json schema file and then run them together, 
piping the output of ***tap-bigquery*** to ***target-amplitude-batch***:
```shell
tap-bigquery -c tap_config.json -d > catalog.json
```

### Step 4: Run
```shell
tap-bigquery -c tap_config.json \
    --catalog catalog.json --start_datetime '2020-08-01T00:00:00Z' \
    --end_datetime '2020-08-02T01:00:00Z' | target-amplitude-batch --config target_config.json \
    > state.json
```

## State
This target emits [state](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#state-file). 
The command also takes a state file input with `--state <file-name>` option. 
If the state is set, `start_datetime` config and command line argument are ignored and the datetime value from `last_update` key is used as the resuming point.

To avoid the data duplication, start datetime is exclusive `start_datetime < datetime_column` when the target runs with state option.
If you fear a data loss because of this, just use the `--start_datetime` option instead of state.

The tap itself does not output a state file.
It anticipate the target program or a downstream process to finalize the state safetly and produce a state file.

---
Copyright &copy; 2022 DTSL