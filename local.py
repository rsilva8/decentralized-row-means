#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 16:08:00 2018 (MDT)

@author: Rogers F. Silva
"""

import json
import os
import sys
import numpy as np
import utils as ut


def local_1(args):

    state = args['state']
    inputs = args['input']
    cache = args['cache']

    file_list = inputs['data'][0]
    file_list = [os.path.join(state["baseDirectory"], file) for file in file_list]
    file_type = inputs['data'][1][0]

    # Read local data files
    datasets = ut.read_data(file_list, file_type, state['clientId'])
    
    # Start local computation:

    # Compute row sums and number of columns per local dataset
    row_sums = {ix:{"row_sum":X.sum(axis=1)[:,None],"num_cols":np.float64(X.shape[1])}
                for (ix,X) in datasets.items()}

    # Compute row sums and number of columns over all local datasets
    row_sum = np.hstack(
        tuple(su['row_sum'] for (ix,su) in row_sums.items())
    ).sum(axis=1)[:,None]
    num_cols = np.array([su['num_cols'] for (ix,su) in row_sums.items()]).sum()

    # Compile results to be transmitted to remote and cached for reuse in next iteration
    computation_output = {
        "output": {
            "row_sum": row_sum.tolist(),
            "num_cols": num_cols,
            "row_sums": {ix:{"row_sum":X['row_sum'].tolist(), "num_cols":X['num_cols']}
                         for (ix,X) in row_sums.items()},
            "computation_phase": 'local_1'
        },
        "cache": dict()
    }

    return computation_output


if __name__ == '__main__':

    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(ut.listRecursive(parsed_args, 'computation_phase'))
    
    if not phase_key:
        computation_output = local_1(parsed_args)
        # Transmit results to remote
        # as file (for large volumes of data, OS overhead):
        # as JSON string (for smaller volumes of data, JSON conversion overhead):
        sys.stdout.write(json.dumps(computation_output))
    else:
        raise ValueError("Error occurred at Local")
