import os
import json
import pandas as pd
import pickle
import cs_Settings as p7dS


def keepAllButFunc(excluded):
    def filterFunc(h):
        return h not in excluded
    return filterFunc


def keepAllInFunc(kept):
    def filterFunc(h):
        return h in kept
    return filterFunc


def refPath():
    full_path = os.path.realpath(__file__)
    path, _ = os.path.split(full_path)
    return f"{path}/"


def filenameGeneric(directory, filename, full):
    if full:
        return None, f"{directory}{filename}"
    return directory, filename


def fileAlreadyExists(directory, filename, verbose):
    if not os.path.isdir(directory):
        if verbose:
            print(f"{directory} doesn't exist or is not a directory.")
        return False
    if filename not in os.listdir(directory):
        if verbose:
            print(f"{filename} doesn't exist in {directory}.")
        return False
    result = os.path.isfile(f"{directory}{filename}")
    if verbose:
        suffix = "and is" if result else "but is not"
        print(f"{filename} exists in {directory} {suffix} a file.")
    return result


def loadDict(directory, filename, verbose):
    if not fileAlreadyExists(directory=directory,
                             filename=filename,
                             verbose=verbose):
        if verbose:
            message = (f"{filename} doesn't exist in {directory}.")
            print(message)
        return None
    if verbose:
        message = (f"Loading {filename} in {directory}.")
        print(message)
    with open(f"{directory}{filename}", 'rb') as f:
        return pickle.load(f)


def dataTypesFilename(full):
    directory = f"{refPath()}{p7dS.SHAREDRESOURCESTYPESDIR}"
    return filenameGeneric(directory=directory,
                           filename=p7dS.MAINDATATYPESFILENAME,
                           full=full)


def mainDataTypes(verbose):
    directory, filename = dataTypesFilename(full=False)
    d = loadDict(directory=directory,
                 filename=filename,
                 verbose=verbose)
    d[p7dS.H_SHARED_TARGET] = "int32"
    return d


TYPEDICT = mainDataTypes(verbose=False)


def adjustTypes(df, verbose):
    for h in df.columns:
        dtype = TYPEDICT.get(h)
        if verbose:
            if dtype is None:
                print(f"{h} doesn't exist in in {df.columns}.")
        assert dtype is not None
        df[h] = df[h].astype(dtype)
    return df


def dfFromJson(directory, filename, verbose):
    if filename not in os.listdir(directory):
        if verbose:
            print(f"{filename} doesn't exist in {directory}.")
        return None
    fullFilename = f"{directory}{filename}"
    with open(fullFilename, "r", encoding="utf8") as f:
        d = json.load(f)
    df = pd.read_json(d)
    if "index" in df.columns:
        del df["index"]
    return adjustTypes(df=df, verbose=verbose)


def main():
    pass


if __name__ == '__main__':
    main()
