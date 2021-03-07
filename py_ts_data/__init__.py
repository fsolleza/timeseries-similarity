import os
import json
import numpy as np

PATH = os.path.realpath("./data")
print("TS-Data path: {}".format(PATH))

def data_info(name):
    """
    Returns JSON containing dataset information
    """
    dirname = os.path.join(PATH, name)
    with open(os.path.join(dirname, "meta"))as f:
        info = json.load(f)
    return info

def load_data(name, variables_as_channels=False):
    """
    Required arguments:
    name: Name of the dataset to load. Get the valid names from py_ts_data.list_datasets()

    Optional arguments:
    variables_as_channels (default False). If true, instead of shape = (x,y,z), the shape
    is given as (x,z,y).

    Returns tuple with 5 elements: X_train, y_train, X_test, y_train, info

    X_train and X_test return numpy arrays with shape: (x, y, z) where:
    x = number of timeseries in the dataset
    y = number of variables in each time series
    z = length of each series.

    If the dataset has variable lenght series, z = length of the longest series. Shorter
    series are filled with np.nan

    """

    info = data_info(name)
    train_file = os.path.join(PATH, name, "train")
    test_file = os.path.join(PATH, name, "test")

    X_train, y_train = parse_file(train_file, info)
    X_test, y_test = parse_file(test_file, info)

    if variables_as_channels:
        X_train = X_train.transpose(0, 2, 1)
        X_test = X_test.transpose(0, 2, 1)

    return X_train, y_train, X_test, y_test, info

def list_datasets():
    """
    Returns list of datasets available from py_ts_data.PATH
    """
    return os.listdir(PATH)

def parse_line(line):
    parts = line.rstrip().split(":")
    data = parts[0]
    label = parts[1]

    variables = data.split(";")
    ts = []
    for var in variables:
        ts.append([float(x) for x in var.split(" ")])
    return np.array(ts), label


def parse_variable_length_file(filepath, info):
    data = []
    labels = []
    max_len = float('-inf')
    nvars = info["n_variables"]
    with open(filepath) as f:
        for line in f:
            ts, label = parse_line(line)
            labels.append(label)
            assert nvars == ts.shape[0]
            if ts.shape[1] > max_len:
                max_len = ts.shape[1]
            data.append(ts)

    final_dataset = []
    for ts in data:
        final = np.empty((nvars, max_len))
        final[:] = np.nan
        final[:ts.shape[0], :ts.shape[1]] = ts
        final_dataset.append(final)

    return np.array(final_dataset), np.array(labels)

def parse_fixed_length_file(filepath, info):
    data = []
    labels = []
    nvars = info["n_variables"]
    with open(filepath) as f:
        for line in f:
            ts, label = parse_line(line)
            assert nvars == ts.shape[0]
            data.append(ts)
            labels.append(label)
    return np.array(data), np.array(labels)

def parse_file(filepath, info):
    data = []
    labels = []
    max_len = float('-inf')
    nvars = info["n_variables"]
    with open(filepath) as f:
        for line in f:
            ts, label = parse_line(line)
            labels.append(label)
            assert nvars == ts.shape[0]
            if ts.shape[1] > max_len:
                max_len = ts.shape[1]
            data.append(ts)

    final_dataset = data
    if info["n_timestamps"] == -1:
        final_dataset = []
        for ts in data:
            final = np.empty((nvars, max_len))
            final[:] = np.nan
            final[:ts.shape[0], :ts.shape[1]] = ts
            final_dataset.append(final)
    
    return np.array(data), np.array(labels)


