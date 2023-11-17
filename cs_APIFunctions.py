import cs_Settings as p7dS
import cs_UsefulFunctions as p7uSF


def loadModel(directory, filename, verbose):
    return p7uSF.loadDict(directory=directory,
                          filename=filename,
                          verbose=verbose)


def finalModelFilename(full):
    directory=f"{p7uSF.refPath()}{p7dS.SHAREDRESOURCESMODELDIR}"
    filename = (f"apiModel_{p7dS.STREAMLITNBCUSTOMERS}"
                f"_{p7dS.APINBFEATURES}"
                f"_{p7dS.FINALMODELTHRESHOLDPCT}.pkl")
    return p7uSF.filenameGeneric(directory=directory,
                                 filename=filename,
                                     full=full)
    

def finalModel():
    directory, filename = finalModelFilename(full=False)
    return loadModel(directory=directory,
                     filename=filename,
                     verbose=False)

# model=finalModel()

def apiDataFilename(full):
    directory=f"{p7uSF.refPath()}{p7dS.APIDATADIR}"
    filename = f"apiData_{p7dS.STREAMLITNBCUSTOMERS}.json"
    return p7uSF.filenameGeneric(directory=directory,
                                 filename=filename,
                                 full=full)


def apiDfFunc():
    directory, filename = apiDataFilename(full=False)
    return p7uSF.dfFromJson(directory=directory,
                            filename=filename,
                            verbose=False)

# apiDf = apiDfFunc()


def predictionDict(item_id, predictProba, granted):
    return {
        p7dS.APIITEMIDHEADER: item_id,
        p7dS.APISCOREHEADER: str(predictProba),
        p7dS.APIGRANTEDHEADER: str(granted)
    }




def main():
    pass


if __name__ == "__main__":
    main()
