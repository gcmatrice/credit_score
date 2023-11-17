import io
import requests
import random
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import requests
from operator import itemgetter, getitem
import pandas as pd
from PIL import Image
import math
import numpy as np
import cs_Settings as p7dS
import cs_UsefulFunctions as p7uSF

PAIDBACKIMGSIZE=(200, 150)

WHICH_CUSTOMER_DEFAULT = "Defaulted"
WHICH_CUSTOMER_NO_DEFAULT = "Didn't default"
WHICH_CUSTOMER_ALL = "All"

CUSTOMER_TYPES = {
    WHICH_CUSTOMER_DEFAULT: (2, 1),  # rank 2 in streamlit, 1 => default
    WHICH_CUSTOMER_NO_DEFAULT: (1, 0),  # rank 1 in streamlit, 0 => no default
    WHICH_CUSTOMER_ALL: (0, None)  # rank 0 in streamlit, void
}


def orderedCustomerTypes():
    l1 = [(r, t) for t, (r, _) in CUSTOMER_TYPES.items()]
    return list(map(itemgetter(1), sorted(l1, key=itemgetter(0))))


def urlRequest(identifier, item_id):
    return f"{p7dS.URL_API}{identifier}/{item_id}"


def apiRequest(identifier, item_id, queries):
    url = urlRequest(identifier=identifier, item_id=item_id)
    result = requests.get(url, params=queries)
    return result


def streamlitDataFilename(full):
    directory = f"{p7uSF.refPath()}{p7dS.STREAMLITDATADIR}"
    filename = f"streamlitData_{p7dS.STREAMLITNBCUSTOMERS}.json"
    return p7uSF.filenameGeneric(directory=directory,
                                 filename=filename,
                                 full=full)


def streamlitDfFunc():
    directory, filename = streamlitDataFilename(full=False)
    return p7uSF.dfFromJson(directory=directory,
                            filename=filename,
                            verbose=False)


def streamlitPositioningFilename(full):
    directory = f"{p7uSF.refPath()}{p7dS.STREAMLITDATADIR}"
    filename = f"streamlitPositioning_{len(p7dS.H_STREAMLIT_FEATS)}.json"
    return p7uSF.filenameGeneric(directory=directory,
                                 filename=filename,
                                 full=full)


def positioningDfFunc():
    directory, filename = streamlitPositioningFilename(
        full=False)
    return p7uSF.dfFromJson(directory=directory,
                            filename=filename,
                            verbose=False)


def sortedRandomSubList(l, howMany):
    if howMany is None:
        return sorted(l)
    if howMany >= len(l):
        return sorted(l)
    ll = list(l)
    random.shuffle(ll)
    return sorted(ll[:howMany])


def predictionMessage(itemId, predictProba, granted, hasDefaulted=None):
    print(f"{itemId=}")
    print(f"{predictProba=}")
    grantedStr = "unknown"
    if granted in {True, False}:
        grantedStr = "granted" if granted else "refused"
    if predictProba != None:
        score = f"{predictProba:.4f}"
    else:
        score = "unknown"
    result = [(f"Customer number {itemId} "
               f"gets a score of score={score}.")
              ]
    if "unknown" != grantedStr:
        result.append(("As a consequence, his application "
                       f"has been {grantedStr}."))
    else:
        result.append(f"Conclusion : {grantedStr}")
    if hasDefaulted is None:
        return result
    if hasDefaulted not in {True, False}:
        return result
    prefixStr = str(granted ^ hasDefaulted)
    suffix = "Positive" if hasDefaulted else "Negative"
    trueOutcome = "defaulted" if hasDefaulted else "didn't default"
    result.append((f"True outcome : Customer number {itemId} "
                   f"{trueOutcome} ({prefixStr} {suffix})."))
    return result


def isIn(x, y, x0, y0, rm, rM, thetam, thetaM, e):
    assert rm <= rM
    assert rm >= 0
    assert thetam >= 0
    assert thetam <= thetaM
    assert thetaM <= math.pi
    X = y-y0
    Y = x0-x
    r2 = X**2+e*Y**2
    if r2 < rm**2:
        return False
    if r2 > rM**2:
        return False
    theta = math.atan2(Y, X)
    if theta < thetam:
        return False
    if theta > thetaM:
        return False
    return True


def fill(X, rgba, rm, rM, thetam, thetaM, e):
    height, width, _ = X.shape
    x0 = height
    y0 = width//2

    def lIsIn(coords):
        x, y = coords
        return isIn(x=x, y=y, x0=x0, y0=y0,
                    rm=rm, rM=rM, thetam=thetam, thetaM=thetaM, e=e)

    shape = (height, width, 2)
    # XX = np.zeros(shape).astype(int)
    XX = np.copy(X)
    for x in range(height):
        for y in range(width):
            if isIn(x=x, y=y, x0=x0, y0=y0,
                    rm=rm, rM=rM, thetam=thetam, thetaM=thetaM, e=e):
                XX[x, y, :] = rgba
    # XX[:, :, 0] = np.expand_dims(np.arange(height).astype(int), axis=1)
    # XX[:, :, 1] = np.expand_dims(np.arange(width).astype(int), axis=0)
    # mask = np.expand_dims(np.apply_along_axis(lIsIn, axis=2, arr=XX), 2)
    # ifTrue = np.expand_dims(np.array(rgba).astype(int), (0, 1))
    # return np.where(mask, ifTrue, X)
    return XX


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


def paidBackImgFilename(hasPaidBack, full):
    directory = f"{p7uSF.refPath()}{p7dS.STREAMLITPICTURESDIR}"
    suffix = "success" if hasPaidBack else "failure"
    filename = f"paidback{suffix}.png"
    return p7uSF.filenameGeneric(directory=directory,
                                 filename=filename,
                                 full=full)


def paidBackImage(hasPaidBack):
    _, filename = paidBackImgFilename(hasPaidBack=hasPaidBack,
                                      full=True)
    return Image.open(filename).resize(PAIDBACKIMGSIZE)

paidBackSuccessImage = paidBackImage(hasPaidBack=True)
paidBackFailureImage = paidBackImage(hasPaidBack=False)

masterDf = streamlitDfFunc()
positioningDf = positioningDfFunc()


def oneLineDf(id_):
    mask = masterDf[p7dS.H_SHARED_UID] == id_
    return masterDf[mask].reset_index(drop=True)


def trueOutcome(id_):
    df = oneLineDf(id_=id_)
    s = df[p7dS.H_SHARED_TARGET].tolist()
    assert 1 == len(s)
    return getitem(s, 0)


def itemRequest(whichItem, amount=None):
    queries = {}
    # print(f"{amount=}")
    if amount is not None:
        queries = {"amount": amount}
    response = apiRequest(identifier="items",
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


def idList(customerType=WHICH_CUSTOMER_ALL, maxSize=None):
    assert customerType in set(CUSTOMER_TYPES.keys())
    if WHICH_CUSTOMER_ALL == customerType:
        l = masterDf[p7dS.H_SHARED_UID].tolist()
        return sortedRandomSubList(l=l,
                                   howMany=maxSize)
    _, filterType = CUSTOMER_TYPES.get(customerType)
    df = masterDf[masterDf[p7dS.H_SHARED_TARGET] == filterType]
    return sortedRandomSubList(l=df[p7dS.H_SHARED_UID].tolist(),
                               howMany=maxSize)


def allScores():
    l = list(map(itemRequest, idList(customerType=WHICH_CUSTOMER_ALL)))
    return pd.DataFrame(l, columns=["score", "granted", "default"])


def getAmount(id_):
    df = oneLineDf(id_=id_)
    s = df[p7dS.H_SHARED_AMOUNT].tolist()
    assert 1 == len(s)
    return int(math.floor(getitem(s, 0)))


def maxValue(customerType=WHICH_CUSTOMER_ALL):
    return max(len(idList(customerType=customerType, maxSize=None)), 10)


def randomId(customerType=WHICH_CUSTOMER_ALL):
    l = idList(customerType=customerType)
    random.shuffle(l)
    return getitem(l, 0)


def randomOneLineDf(customerType=WHICH_CUSTOMER_ALL):
    return oneLineDf(id_=randomId(customerType=customerType))


def positioning(id_):
    df = positioningDf
    oldf = oneLineDf(id_=id_)
    fig = plt.figure(figsize=(12, 6))
    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 3])
    # refAx=None
    colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    for h, c, g in zip(df.columns, colors[:len(df.columns)], gs):
        # print(f"{h=}")
        # if refAx is None:
        #     ax = plt.subplot(g)
        #     refAx = ax
        # else:
        #     ax = plt.subplot(g,sharey=refAx)
        value = oldf.at[0, h]
        # print(f"{value=}")
        ax = plt.subplot(g)
        g2 = sns.boxplot(y=df[h],  orient='v', ax=ax, color=c)
        g2.set(xticklabels=[])
        g2.set(title=h)
        g2.set(xlabel=None)
        g2.tick_params(bottom=False)  # remove the ticks
        g2.axhline(value)

    return fig2img(fig).resize((800, 300))


def main():
    l = idList()
    random.shuffle(l)
    oneId = l[0]
    df = oneLineDf(id_=oneId)
    # queries = {"q": df.to_json()}
    queries = {"q": "streamlit"}
    response = apiRequest(identifier="items",
                          item_id=oneId,
                          queries=queries)
    print(response.text)


def main2():
    print(f"{idList()=}")
    print(masterDf)
    print(f"{masterDf.dtypes.unique()=}")


if __name__ == '__main__':
    df = allScores().sort_values("score")
    for s, r in zip(df["score"], df["granted"]):
        print(f"{s=}:{r=}")
