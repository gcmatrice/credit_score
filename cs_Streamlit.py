import streamlit as st
# from datetime import datetime
import cs_StreamlitFunctions as p7STF
import cs_Settings as p7dS
import math


# greenLightImage = Image.open(f"{p7dS.STREAMLITPICTURESDIR}paidbacksuccess.png")
# greenLightImage = greenLightImage.resize((200, 150))
# redLightImage = Image.open(f"{p7dS.STREAMLITPICTURESDIR}paidbackfailure.png")
# redLightImage = redLightImage.resize((200, 150))
# masterDf = p7STF.streamlitDfFunc()
# positioningDf = p7STF.positioningDfFunc()


paidBackSuccessImage = p7STF.paidBackSuccessImage
paidBackFailureImage = p7STF.paidBackFailureImage
masterDf = p7STF.masterDf
positioningDf = p7STF.positioningDf




#st.set_option('deprecation.showPyplotGlobalUse', False)

custTypeStr = st.sidebar.radio("Type of customer",
                               p7STF.orderedCustomerTypes())
maxVal = p7STF.maxValue(customerType=custTypeStr)
listLength = max(st.sidebar.slider(label="List size",
                                   min_value=0,
                                   max_value=maxVal,
                                   value=20,
                                   step=10), 1)
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
title = f"Choose one customer Id among {len(idList)}"
whichItem = st.sidebar.selectbox(title, idList)
st.title(f"Credit scorer, customer #{whichItem}")
currentAmount = p7STF.getAmount(id_=whichItem)
amount = st.sidebar.slider(p7dS.H_SHARED_AMOUNT,
                           min_value=0,
                           max_value=currentAmount,
                           value=currentAmount)
# whichItem = st.sidebar.radio("Item", list(range(1, 5)))
#now = datetime.now().strftime("%d %b %Y %H:%M:%S")


try:
    st.image(p7STF.positioning(id_=whichItem))
    score, granted, defaulted = p7STF.itemRequest(whichItem=whichItem,
                                            amount=amount)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"Granted? (score:{score:.2f})")
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
    with col2:
        st.markdown(f"Credit repaid?")
        img = paidBackFailureImage if defaulted else paidBackSuccessImage
        st.image(img)
        # if defaulted:
        #     caption = f"Customer number {whichItem} has defaulted"
        #     st.image(redLightImage, caption=caption)
        # else:
        #     caption = f"Customer number {whichItem} hasn't defaulted"
        #     st.image(greenLightImage, caption=caption)
except Exception as e:
    st.markdown(f"An exception occured: {str(e)}")
