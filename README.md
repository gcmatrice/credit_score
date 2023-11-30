#  Credit Scorer

## Description

This project contains all the resources required for:

- a dashboard
- an API

### The dashboard

The dashboard is developed using [Streamlit](https://streamlit.io/). It provides the user with information and computation for a selection of 500 customers who apply for a credit (test set). Half of them did repay their credit, the other half did not. Please notice that the API **doesn't have** this information.

On the sidebar on the left, one can:

- input the IP address of the API: http://127.0.0.1:8000/, in general, if run locally, the API IP address otherwise,

- choose if one wants to select all applicants (500), or those who repaid their credit (250), or those who didn't (250),

- finally, select one particular customer.

Three tabs are available:

    1. Credit Scorer: it shows the credit score of the selected customer and whether the credit would be granted or not. The amount of the credit can be adjusted; the credit score is dynamically recomputed by the API. The final result, hence whether the credit was repaid or not, is also displayed. Again, this information is not provided by the API.
    
    2. Features Values: it displays all the pieces of information (40) used by the API to compute the score.
    
    3. Feature Positioning: one can select one among the 40 pieces of information used by the model. The position of the particular customer is shown relative to the distribution in the whole population used during the training of the model (train set).

### The API

The API is developed using [FastAPI](https://fastapi.tiangolo.com/)

It returns the credit score, and therefore whether the credit application will be accepted or denied, for a particular customer (**item_id**). If an **amount** for the credit is specified, it will be used, instead of the default one.

The API also returns the whole list of **item_id** it knows (500).

### How to use it (locally)

1. First, launch the API: `uvicorn cs_FastAPI:app`. 

2. When the API is up and running, launch the dashboard: `streamlit run cs_Streamlit.py`. If the API IP address is not http://127.0.0.1:8000/, use the one provided at step 1.
