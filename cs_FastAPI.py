from typing import Union
from operator import getitem
import fastapi
import time
import cs_APIFunctions as p7APIF
import cs_Settings as p7dS

description = """
## items

You can **get** credit scores and probability of 
default for a selection of customers (**items**).

## itemlist

You can **get** the list of available customers (**items**).
"""
summary = "Credit score and probability of default API."

app = fastapi.FastAPI(title="Credit Score API",
                      description=description,
                      summary=summary)


model = p7APIF.p7FinalModel(verbose=False)
apiDf = p7APIF.apiDfFunc()


def allItems():
    return sorted(apiDf[p7dS.H_SHARED_UID].tolist())


def scoreDict(id_, amount=None):
    try:
        oneLineDf = apiDf[apiDf[p7dS.H_SHARED_UID] == id_]
    except Exception as e:
        return p7APIF.predictionDict(item_id=id_,
                                     predictProba=None,
                                     granted=None)
    inputNbRows, _ = oneLineDf.shape
    if 1 != inputNbRows:
        return p7APIF.predictionDict(item_id=id_,
                                     predictProba=None,
                                     granted=None)

    featuresDf = (oneLineDf[model.feature_name_]
                  .copy()
                  .reset_index(drop=True))
    if amount is not None:
        if isinstance(amount, (int, float)):
            if p7dS.H_SHARED_AMOUNT in model.feature_name_:
                featuresDf.at[0, p7dS.H_SHARED_AMOUNT] = amount

    prediction = model.predict(featuresDf,
                               num_iteration=model.best_iteration_)
    prediction = getitem(prediction, 0)
    granted = (prediction == 0)

    proba = model.predict_proba(featuresDf,
                                num_iteration=model.best_iteration_)
    proba = getitem(proba[:, 1], 0)

    return p7APIF.predictionDict(item_id=id_,
                                 predictProba=proba,
                                 granted=granted)


@app.get("/")
def connection_check():
    """
    Connection check
    """
    return {"connection": "OK"}


@app.get("/items/{item_id}")
def score(item_id: int, amount: Union[str, None] = None):
    """
    Returns the estimated probability of default for customer 
    **item_id** and therefore whether the credit should be 
    granted or not.

    If an **amount** for the credit is provided, 
    it will be used for the estimation. 
    """
    if amount is None:
        return scoreDict(id_=item_id)
    return scoreDict(id_=item_id, amount=float(amount))


@app.get("/itemlist/")
def all_items():
    """
    Returns the whole list of available customers
    """
    return {"items": allItems()}
