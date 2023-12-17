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
ST_LOCALE="locale"
ST_DEPLOYED="deployed"
ST_MANUAL="manual entry"
deployedAddressKnown, deployedAPIAddress = p7STF.deployedAPIAddress()
if deployedAddressKnown:
    deployedAddressOptions = [ST_LOCALE, ST_DEPLOYED, ST_MANUAL]
else:
    deployedAddressOptions = [ST_LOCALE, ST_MANUAL]
ipAddressSelection = st.sidebar.radio(label="Select API",
                                      options=deployedAddressOptions)
apiIpAddressDefaultValue = p7STF.LOCALE_API_IPADDRESS
if ST_LOCALE == ipAddressSelection:
    apiIpAddressDefaultValue = p7STF.LOCALE_API_IPADDRESS
if ST_DEPLOYED == ipAddressSelection:
    apiIpAddressDefaultValue = deployedAPIAddress
if ST_MANUAL == ipAddressSelection:
    apiIpAddressDefaultValue = p7STF.ROOT_IPADDRESS

apiIpAddress = st.sidebar.text_input("API IP Address",
                                     value=apiIpAddressDefaultValue)

#Customer type

custTypeStr = st.sidebar.radio("Type of customer",
                               p7STF.orderedCustomerTypes())

# Persistency
if "apiIpAddress" not in st.session_state:
    st.session_state["apiIpAddress"] = apiIpAddress
listLength = len(p7STF.streamlitIdList(customerType=custTypeStr))
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
    idList = p7STF.streamlitIdList(customerType=custTypeStr)
    st.session_state["idList"] = idList
else:
    idList = st.session_state["idList"]


# Customer Id (sidebar)
title = f"Customer Id (among {len(idList)})"
whichItem = st.sidebar.selectbox(title, idList)


# Dashboard

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

    goOn = p7STF.ROOT_IPADDRESS != apiIpAddress
    if goOn:
        score, granted, defaulted = p7STF.itemRequest(apiurl=apiIpAddress,
                                                      whichItem=whichItem,
                                                      amount=amount)
        goOn &= (score is not None)
        goOn &= (granted is not None)
        goOn &= (defaulted is not None)
    if goOn:
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
    _ = st.dataframe(fDf, hide_index=True)

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

    description = descriptionsDict.get(displayedFeature)
    if description is None:
        description = "No description available"
    st.markdown(centeredText(text=f"{displayedFeature} : {description}",
                             color="grey", whichH="5"),
                unsafe_allow_html=True)
    override_ = None
    if displayedFeature == p7dS.H_SHARED_AMOUNT:
        override_ = amount
    st.image(p7STF.positioningImg(id_=whichItem,
                                  displayedFeature=displayedFeature,
                                  override_=override_).resize((600, 300)))
