import streamlit as st
import cs_StreamlitFunctions as p7STF
import cs_Settings as p7dS

# Pictures
logoImage = p7STF.logoImage.resize((925, 200))
paidBackImages = p7STF.paidBackImages

# Dataframes (for performance purposes)
masterDf = p7STF.masterDf
positioningDf = p7STF.positioningDf

# Dictionary of descriptions of the features
descriptionsDict = p7STF.descriptionsDict

# Tabs
tabScorer, tabFeaturesValues, tabPositioning = st.tabs(
    ["Credit Scorer",
     "Features Values",
     "Feature Positioning"])

# Centered text with adjustable font sizes and color


def centeredText(text, color, whichH):
    return (f"<h{whichH} style='text-align: center; color: {color};'>"
            f"{text}</h{whichH}>")


#Logo (sidebar)
st.sidebar.image(logoImage)

# API Address selection
apiIpAddress = st.sidebar.text_input("API IP Address",
                                     value=p7dS.LOCALE_API)
if "apiIpAddress" not in st.session_state:
    st.session_state["apiIpAddress"] = apiIpAddress

# ipAddress = st.sidebar.radio("IP Address",
#                              ["locale", "remote"])
# apiIpAddress = p7dS.AZURE_API if ipAddress == "remote" else p7dS.LOCALE_API

# Customer type (all, those who repaid or those who defaulted)
custTypeStr = st.sidebar.radio("Type of customer",
                               p7STF.orderedCustomerTypes())

# Required persistency
listLength = len(p7STF.idList(customerType=custTypeStr))
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
    idList = p7STF.idList(customerType=custTypeStr)
    st.session_state["idList"] = idList
else:
    idList = st.session_state["idList"]

# Customer Id (sidebar)
title = f"Customer Id (among {len(idList)})"
whichItem = st.sidebar.selectbox(title, idList)


with tabScorer:  # Score and repayment
    title = f"Credit scorer, customer #{whichItem}"
    st.markdown(centeredText(text=title, color="black", whichH="2"),
                unsafe_allow_html=True)

    # Potention amount adjustment
    currentAmount = p7STF.getAmount(id_=whichItem)
    amount = st.slider(label=f"Adjust {p7dS.H_SHARED_AMOUNT}",
                       min_value=0,
                       max_value=currentAmount,
                       value=currentAmount)

    score, granted, defaulted = p7STF.itemRequest(apiurl=apiIpAddress,
                                                  whichItem=whichItem,
                                                  amount=amount)
    if score is not None and granted is not None and defaulted is not None:
        colGranted, colDefault = st.columns(2)
        colGauge, colPaidbackImg = st.columns(2)
        with colGranted:
            grantedStr = "" if granted else "not "
            scoreStr = f"Score:{score:.2f}</br>Credit {grantedStr}granted"
            color = "green" if granted else "red"
            st.markdown(centeredText(text=scoreStr, color=color, whichH="3"),
                        unsafe_allow_html=True)

        with colDefault:
            repaid = "not " if defaulted else ""
            repaidStr = f"Credit</br>{repaid}repaid"
            color = "red" if repaid else "green"
            st.markdown(centeredText(text=repaidStr, color=color, whichH="3"),
                        unsafe_allow_html=True)
        with colGauge:
            if score is not None:
                img = p7STF.generateGauge(score=score)
                img = img.resize((300, 150))
                st.image(img)
        with colPaidbackImg:
            img = paidBackImages.get(not defaulted)
            st.image(img.resize((300, 150)))
    else:
        st.markdown("## No answer from API")

with tabFeaturesValues:  # features values
    fDf = p7STF.featuresTable(id_=whichItem)
    # _ = st.data_editor(fDf, hide_index=True)
    _ = st.dataframe(fDf, hide_index=True)
    # _ = st.table(fDf, hide_index=True)

with tabPositioning:  # positioning
    title = f"Feature Positioning, customer #{whichItem}"
    st.markdown(centeredText(text=title, color="black", whichH="2"),
                unsafe_allow_html=True)

    # Feature selection for the positioning
    possibleFeatures = p7STF.possibleFeatures
    priorities = p7STF.DEFAULT_STREAMLIT_FEATS
    availableFeatures = p7STF.mergeWithPriority(source=possibleFeatures,
                                                priorities=priorities,
                                                verbose=True)
    displayedFeature = st.selectbox(label="Feature",
                                    options=availableFeatures)

    # Description of the selection feature
    description = descriptionsDict.get(displayedFeature)
    if description is None:
        description = "No description available"
    st.markdown(centeredText(text=f"{displayedFeature} : {description}",
                             color="grey", whichH="5"),
                unsafe_allow_html=True)
    override_ = None
    if displayedFeature == p7dS.H_SHARED_AMOUNT:
        override_ = amount
    # fValue = p7STF.featureValue(id_=whichItem,
    #                             displayedFeature=displayedFeature)
    # st.markdown(centeredText(text=f"Value={fValue}",
    #                          color="black", whichH="5"),
    #             unsafe_allow_html=True)
    st.image(p7STF.positioningImg(id_=whichItem,
                                  displayedFeature=displayedFeature,
                                  override_=override_).resize((600, 300)))

    # st.markdown(centeredText(text=f"To do later",
    #                          color="red", whichH="1"),
    #             unsafe_allow_html=True)
