import io
import os
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from operator import itemgetter, getitem
from PIL import Image
import math
import numpy as np
import cs_Settings as p7dS
import cs_UsefulFunctions as p7uSF

#Features to appear first in the list of features

DEFAULT_STREAMLIT_FEATS = [
    "EXT_SOURCE_3",
    "EXT_SOURCE_2",
    "DAYS_BIRTH",
    p7dS.H_SHARED_AMOUNT
]


PAIDBACKIMGSIZE = (2000, 1500)

WHICH_CUSTOMER_DEFAULT = "Defaulted"
WHICH_CUSTOMER_NO_DEFAULT = "Didn't default"
WHICH_CUSTOMER_ALL = "All"

CUSTOMER_TYPES = {
    WHICH_CUSTOMER_DEFAULT: (2, 1),  # rank 2 in streamlit, 1 => default
    WHICH_CUSTOMER_NO_DEFAULT: (1, 0),  # rank 1 in streamlit, 0 => no default
    WHICH_CUSTOMER_ALL: (0, None)  # rank 0 in streamlit, void
}

POSing_RESULT = "RESULT"
FLAG_DEFAULTED = "DEFAULTED"
FLAG_REPAID = "REPAID"


def orderedCustomerTypes():
    l1 = [(r, t) for t, (r, _) in CUSTOMER_TYPES.items()]
    return list(map(itemgetter(1), sorted(l1, key=itemgetter(0))))


def urlRequest(apiurl, identifier, item_id):
    return f"{apiurl}{identifier}/{item_id}"


def apiRequest(apiurl, identifier, item_id, queries):
    url = urlRequest(apiurl=apiurl,
                     identifier=identifier,
                     item_id=item_id)
    result = requests.get(url, params=queries)
    return result


def descriptionsFilename(full):
    directory = f"{p7uSF.refPath()}{p7dS.STREAMLITDATADIR}"
    filename = f"featuresDescriptions.json"
    return p7uSF.filenameGeneric(directory=directory,
                                 filename=filename,
                                 full=full)


def descriptionsDictFunc():
    directory, filename = descriptionsFilename(full=False)
    return p7uSF.loadDict(directory=directory,
                          filename=filename,
                          verbose=False)


descriptionsDict = descriptionsDictFunc()


def streamlitDataFilename(full):
    directory = f"{p7uSF.refPath()}{p7dS.STREAMLITDATADIR}"
    filename = f"streamlitData_{p7dS.STREAMLITNBCUSTOMERS}.json"
    return p7uSF.filenameGeneric(directory=directory,
                                 filename=filename,
                                 full=full)


def streamlitDfFunc():
    directory, filename = streamlitDataFilename(full=False)
    if filename not in os.listdir(directory):
        return None
    df = p7uSF.dfFromJson(directory=directory,
                          filename=filename,
                          verbose=False)
    if "index" in df.columns:
        del df["index"]
    return df

masterDf = streamlitDfFunc()
masterDf[POSing_RESULT] = masterDf[p7dS.H_SHARED_TARGET].astype(int)
masterDf[POSing_RESULT].replace(1, FLAG_DEFAULTED, inplace=True)
masterDf[POSing_RESULT].replace(0, FLAG_REPAID, inplace=True)

def streamlitPositioningFilename(full):
    directory = f"{p7uSF.refPath()}{p7dS.STREAMLITDATADIR}"
    filename = f"streamlitPositioning_{p7dS.APINBFEATURES}.json"
    return p7uSF.filenameGeneric(directory=directory,
                                 filename=filename,
                                 full=full)


def positioningDfFunc():
    directory, filename = streamlitPositioningFilename(
        full=False)
    if filename not in os.listdir(directory):
        return None
    return p7uSF.dfFromJson(directory=directory,
                            filename=filename,
                            verbose=False)

positioningDf = positioningDfFunc()
positioningDf[POSing_RESULT] = positioningDf[p7dS.H_SHARED_TARGET].astype(int)
positioningDf[POSing_RESULT].replace(1, FLAG_DEFAULTED, inplace=True)
positioningDf[POSing_RESULT].replace(0, FLAG_REPAID, inplace=True)






def needleFilename(full):
    directory = f"{p7uSF.refPath()}{p7dS.STREAMLITPICTURESDIR}"
    filename = "needle.png"
    return p7uSF.filenameGeneric(directory=directory,
                                 filename=filename,
                                 full=full)


def gaugeFilename(thresholdH, full):
    directory = f"{p7uSF.refPath()}{p7dS.STREAMLITPICTURESDIR}"
    filename = f"gauge_{thresholdH}.png"
    return p7uSF.filenameGeneric(directory=directory,
                                 filename=filename,
                                 full=full)


def generateGauge(score):
    percent = 1.0-score
    loc = (825, 825)
    rotation = 90.0 - 180.0 * percent
    _, needlefn = needleFilename(full=True)
    dial = Image.open(needlefn)
    dial = dial.rotate(rotation, resample=Image.BICUBIC, center=loc)
    thresholdH = p7dS.FINALMODELTHRESHOLDPCT
    _, filename = gaugeFilename(thresholdH=thresholdH,
                                full=True)
    gauge = Image.open(filename)
    gauge.paste(dial, mask=dial)
    return gauge


def floatStrToFloat(floatStr):
    if floatStr is None:
        return None
    try:
        result = float(floatStr)
    except Exception:
        return None
    return result


def boolStrToBool(boolStr):
    if boolStr is None:
        return None
    if boolStr not in {"False", "True"}:
        return None
    return "True" == boolStr


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    return Image.open(buf)


def logoImageFunc():
    directory = f"{p7uSF.refPath()}{p7dS.STREAMLITPICTURESDIR}"
    filename = "pretadepenserlogo.png"
    return Image.open(f"{directory}{filename}")


logoImage = logoImageFunc()


def paidBackImgFilename(hasPaidBack, full):
    directory = f"{p7uSF.refPath()}{p7dS.STREAMLITPICTURESDIR}"
    suffix = "success" if hasPaidBack else "failure"
    filename = f"paidback{suffix}square.png"
    return p7uSF.filenameGeneric(directory=directory,
                                 filename=filename,
                                 full=full)


def paidBackImage(hasPaidBack):
    _, filename = paidBackImgFilename(hasPaidBack=hasPaidBack,
                                      full=True)
    return Image.open(filename).resize(PAIDBACKIMGSIZE)


paidBackImages = {t: paidBackImage(hasPaidBack=t) for t in [False, True]}


excludedFeatures = {
    p7dS.H_SHARED_TARGET,
    p7dS.H_SHARED_UID,
    POSing_RESULT
}
filterFunc = p7uSF.keepAllButFunc(excluded=excludedFeatures)
possibleFeatures = list(filter(filterFunc, positioningDf.columns))
assert len(possibleFeatures) == p7dS.APINBFEATURES


def oneLineDf(id_):
    mask = masterDf[p7dS.H_SHARED_UID] == id_
    return masterDf[mask].reset_index(drop=True)

def featureValue(id_, displayedFeature):
    df = oneLineDf(id_)
    df = df[[displayedFeature]].copy()
    df.reset_index(inplace=True)
    nbRows, _ = df.shape
    if nbRows != 1:
        return None
    return df.at[0, displayedFeature]


def trueOutcome(id_):
    df = oneLineDf(id_=id_)
    s = df[p7dS.H_SHARED_TARGET].tolist()
    assert 1 == len(s)
    return getitem(s, 0)


def itemRequest(whichItem, apiurl, amount=None):
    try:
        queries = {}
        # print(f"{amount=}")
        if amount is not None:
            queries = {"amount": amount}
        response = apiRequest(apiurl=apiurl,
                              identifier="items",
                              item_id=whichItem,
                              queries=queries)
        score = response.json().get(p7dS.APISCOREHEADER)
        if score is not None:
            score = floatStrToFloat(score)
        hasBeenGranted = response.json().get(p7dS.APIGRANTEDHEADER)
        if hasBeenGranted is not None:
            hasBeenGranted = boolStrToBool(hasBeenGranted)
        hasDefaulted = (trueOutcome(id_=whichItem) == 1)
        return score, hasBeenGranted, hasDefaulted
    except Exception as e:
        print(str(e))
        return None, None, None


def idList(customerType=WHICH_CUSTOMER_ALL):
    if WHICH_CUSTOMER_ALL==customerType:
        return masterDf[p7dS.H_SHARED_UID].tolist()
    target = 1 if WHICH_CUSTOMER_DEFAULT == customerType else 0
    df = masterDf[masterDf[p7dS.H_SHARED_TARGET] == target]
    return df[p7dS.H_SHARED_UID].tolist()


def getAmount(id_):
    df = oneLineDf(id_=id_)
    s = df[p7dS.H_SHARED_AMOUNT].tolist()
    if 1 != len(s):
        return 0
    return int(math.floor(getitem(s, 0)))




def positioningImg(id_, displayedFeature, override_=None):
    thisIdHeader = "ThisId"
    # print(f"{positioningDf.columns=}")
    df = positioningDf[[displayedFeature,
                        p7dS.H_SHARED_TARGET,
                        p7dS.H_SHARED_UID,
                        POSing_RESULT]].copy()
    nbrows, _ = df.shape
    df[thisIdHeader] = [id_]*nbrows
    # oldf = oneLineDf(id_=id_)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.set_theme(style="ticks", palette="pastel")
    # value = oldf.at[0, displayedFeature] if override_ is None else override_
    ax = sns.boxplot(data=df, x=thisIdHeader, y=displayedFeature,
                     hue=POSing_RESULT, orient='v', ax=ax)
    ax.set(xticklabels=[])
    ax.set(xlabel=None)  # a remplacer et jouer sur visibility
    ax.tick_params(bottom=False)  # remove the ticks
    desc = descriptionsDict.get(displayedFeature)
    if desc is not None:
        value=featureValue(id_=id_, displayedFeature=displayedFeature)
        ax.axhline(value, color="black")
        title = f"Value={value}"
        fig.suptitle(title, fontsize=20)
    return fig2img(fig).resize((800, 300))


def mergeWithPriority(source, priorities, verbose):
    if not set(priorities).issubset(set(source)):
        if verbose:
            message = (f"Warning: {set(priorities)-set(source)}"
                       "don't belong to source vector.")
            print(message)
        newPriorities = filter(p7uSF.keepAllInFunc(kept=source), priorities)
        return mergeWithPriority(source=source,
                                 priorities=newPriorities)
    v = list(filter(p7uSF.keepAllInFunc(kept=source), priorities))
    v.extend(filter(p7uSF.keepAllButFunc(excluded=v), source))
    return v


def main():
    pass


if __name__ == '__main__':
    main()
