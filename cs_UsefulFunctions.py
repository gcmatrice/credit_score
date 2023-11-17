import os
import json
import pandas as pd
import pickle
import cs_Settings as p7dS

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
    directory=f"{refPath()}{p7dS.SHAREDRESOURCESTYPESDIR}"
    return filenameGeneric(directory=directory,
                           filename=p7dS.MAINDATATYPESFILENAME,
                           full=full)


def mainDataTypes(verbose):
    directory, filename = dataTypesFilename(full=False)
    return loadDict(directory=directory,
                    filename=filename,
                    verbose=verbose)


def adjustTypes(df, verbose):
    typeDict = mainDataTypes(verbose=verbose)
    for h in df.columns:
        dtype = typeDict.get(h)
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
    fullFilename = f"{directory}{filename}"
    with open(fullFilename, "r", encoding="utf8") as f:
        d = json.load(f)
    df = pd.read_json(d)
    return adjustTypes(df=df, verbose=verbose)



def main():

    print("Path at terminal when executing this file")
    print(os.getcwd() + "\n")

    print("This file path, relative to os.getcwd()")
    print(__file__ + "\n")

    print("This file full path (following symlinks)")
    full_path = os.path.realpath(__file__)
    print(full_path + "\n")

    print("This file directory and name")
    path, filename = os.path.split(full_path)
    print(path + ' --> ' + filename + "\n")

    print("This file directory only")
    print(os.path.dirname(full_path))

if __name__ == '__main__':
    main()
