from math import nan
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.util import constants

def load_log_from_CSV(path):
    df = pd.read_csv(path)
    df = dataframe_utils.convert_timestamp_columns_in_df(df)
    stream = log_conversion.apply(df, variant=log_conversion.TO_EVENT_STREAM)
    log = log_conversion.apply(
        stream,
        parameters={
            constants.PARAMETER_CONSTANT_CASEID_KEY: "concept:instance",
            constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "concept:name",
            constants.PARAMETER_CONSTANT_TIMESTAMP_KEY: "time:timestamp",
            constants.PARAMETER_CONSTANT_RESOURCE_KEY: "org:resource",
        },
    )
    return remove_NaN_to_allow_no_resources(log)

def remove_NaN_to_allow_no_resources(log):
    for trace in log:
        for event in trace:
            if event["org:resource"] != event["org:resource"]:
                event["org:resource"] = None
    
    return log
