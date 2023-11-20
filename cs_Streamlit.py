import streamlit as st
# from datetime import datetime
import cs_StreamlitFunctions as p7STF
import cs_Settings as p7dS
import math

paidBackImages = p7STF.paidBackImages
masterDf = p7STF.masterDf
positioningDf = p7STF.positioningDf
descriptionsDict = p7STF.descriptionsDict

# st.write(f"{masterDf.shape=}")
# st.write(f"{positioningDf.shape=}")

# apiIpAddress = st.sidebar.text_input("IP Address",
#                                      value=p7dS.LOCALE_API)
st.sidebar.image(paidBackImages.get(True))

ipAddress = st.sidebar.radio("IP Address",
                             ["locale", "remote"])
apiIpAddress = p7dS.AZURE_API if ipAddress == "remote" else p7dS.LOCALE_API

allButTarget = list(filter(lambda h: h not in
                           {p7dS.H_SHARED_TARGET, p7dS.H_SHARED_UID},
                           positioningDf.columns))
options = p7STF.mergeWithPriority(source=allButTarget,
                                  priorities=p7STF. DEFAULT_STREAMLIT_FEATS,
                                  verbose=True)
displayedFeature = st.sidebar.selectbox(label="Feature",
                                        options=options)

custTypeStr = st.sidebar.radio("Type of customer",
                               p7STF.orderedCustomerTypes())
listLength = p7STF.maxValue(customerType=custTypeStr)
# listLength = max(st.sidebar.slider(label="List size",
#                                    min_value=0,
#                                    max_value=maxVal,
#                                    value=20,
#                                    step=10), 1)
updateIdList = False


if "listLength" not in st.session_state:
    updateIdList = True
    st.session_state["listLength"] = listLength
elif listLength != st.session_state["listLength"]:
    updateIdList = True
    st.session_state["listLength"] = listLength

if "custTypeStr" not in st.session_state:
    updateIdList = True
    st.session_state["custTypeStr"] = custTypeStr
elif custTypeStr != st.session_state["custTypeStr"]:
    updateIdList = True
    st.session_state["custTypeStr"] = custTypeStr

if updateIdList:
    idList = p7STF.idList(customerType=custTypeStr, maxSize=listLength)
    st.session_state["idList"] = idList
else:
    idList = st.session_state["idList"]
title = f"Customer Id (among {len(idList)})"
whichItem = st.sidebar.selectbox(title, idList)
# st.title(f"Credit scorer, customer #{whichItem}")


def centeredText(text, color, whichH):
    return (f"<h{whichH} style='text-align: center; color: {color};'>"
            f"{text}</h{whichH}>")


title = f"Credit scorer, customer #{whichItem}"
st.markdown(centeredText(text=title, color="grey", whichH="1"),
            unsafe_allow_html=True)
currentAmount = p7STF.getAmount(id_=whichItem)
amount = st.sidebar.slider(p7dS.H_SHARED_AMOUNT,
                           min_value=0,
                           max_value=currentAmount,
                           value=currentAmount)
# whichItem = st.sidebar.radio("Item", list(range(1, 5)))
#now = datetime.now().strftime("%d %b %Y %H:%M:%S")


# htmlTable = p7STF.paramDf(id_=whichItem,
#                           displayedFeature=displayedFeature)
description = descriptionsDict.get(displayedFeature)
if description is None:
    description = "No description available"
# st.write(f"{displayedFeature} : {description}")
st.markdown(centeredText(text=f"{displayedFeature} : {description}",
                         color="grey", whichH="3"),
            unsafe_allow_html=True)

score, granted, defaulted = p7STF.itemRequest(apiurl=apiIpAddress,
                                              whichItem=whichItem,
                                              amount=amount)
# st.write(htmlTable, unsafe_allow_html=True)
override = None
if displayedFeature == p7dS.H_SHARED_AMOUNT:
    override = amount
fValue = p7STF.featureValue(id_=whichItem, displayedFeature=displayedFeature)
st.image(p7STF.positioning(id_=whichItem,
                           displayedFeature=displayedFeature,
                           override=override))
fvStr = (f"Value: {fValue}")
st.markdown(centeredText(text=fvStr,
                         color="grey", whichH="3"),
            unsafe_allow_html=True)
# st.write(fvStr)
if score is not None and granted is not None and defaulted is not None:
    # col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    # with col1:
    with col3:
        grantedStr = "" if granted else "not "
        scoreStr = f"Score:{score:.2f}</br>Credit {grantedStr}granted"
        color = "green" if granted else "red"
        # st.markdown(f"### Score:{score:.2f} => {grantedStr}granted")
        st.markdown(centeredText(text=scoreStr, color=color, whichH="3"),
                    unsafe_allow_html=True)

    with col4:
        repaid = "not " if defaulted else ""
        repaidStr = f"Credit</br>{repaid}repaid"
        color = "red" if repaid else "green"
        st.markdown(centeredText(text=repaidStr, color=color, whichH="3"),
                    unsafe_allow_html=True)
        # st.markdown(f"### Credit repaid? : {repaid}")
    with col5:
        if score is not None:
            img = p7STF.generateGauge(score=score)
            img = img.resize((300, 150))
            # caption = f"Score for customer number {whichItem} : {score:.2f}"

            st.image(img)
    # with col2:
    #     if granted is not None:
    #         if granted:
    #             caption = f"Credit granted to customer number {whichItem}"
    #             st.image(greenLightImage, caption=caption)
    #         else:
    #             caption = f"Credit denied to customer number {whichItem}"
    #             st.image(redLightImage, caption=caption)
    # with col2:
    with col6:
        img = paidBackImages.get(not defaulted)
        st.image(img)
        # if defaulted:
        #     caption = f"Customer number {whichItem} has defaulted"
        #     st.image(redLightImage, caption=caption)
        # else:
        #     caption = f"Customer number {whichItem} hasn't defaulted"
        #     st.image(greenLightImage, caption=caption)
else:
    st.markdown("## No answer from API")
