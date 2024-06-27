import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mtick

st.set_page_config(page_title="Multipage App", page_icon="Casa")

st.title("iSEC")
st.sidebar.success("Select a page above.")

multi = """This tool executes the calculation of Risk-Weights (RWs) for securitisation exposure under two key methodologies: *Standardized Approach for Credit Risk - Standardized Approach* (***SEC-SA***) and *Standardized Approach for Credit Risk - External Ratings-Based Approach* (***SEC-ERBA***), in compliance with the industry regulations set out in the Capital Requirements Regulation (CRR).
"""
st.markdown(multi)

st.markdown(
    "*Here you can insert the input parameters related to the securitisation exposure*"
)


def propertiesMapper(tranches, propertiesDictionary):

    if tranches == 2:
        newdict = dict.fromkeys(["Junior", "Senior"])
        newdict.update(propertiesDict)
    elif tranches == 3:
        newdict = dict.fromkeys(
            [
                "Junior",
                "Mezzanine",
                "Senior",
            ]
        )
        newdict.update(propertiesDict)
    else:
        newdict = dict.fromkeys(
            ["Junior", "Mezzanine 2", "Mezzanine 1", "Senior 2", "Senior 1"]
        )
        newdict.update(propertiesDict)

    newdict = {key: value for key, value in newdict.items() if value != None}

    return newdict


# Input

collateralAmount = st.number_input("Collateral Amount", min_value=0, step=1000)

trancheNum = st.slider("Set the tranches number", min_value=2, max_value=5, step=1)

secType = st.selectbox(
    "Securitisation Typology", ("Standard", "STS", "Resecuritisation")
)

num_subpool = st.number_input("Number of Subpools", min_value=1, step=1)

with st.form("SecProperties"):

    c1, c2 = st.columns(2)

    seniority_dict = {}
    amount_dict = {}

    with c1:

        st.text("Tranche Seniority")

        if trancheNum == 2:
            for i in range(0, trancheNum):
                seniority_dict[i] = st.selectbox(
                    f"Tranche Seniority {i+1}",
                    ("Senior", "Junior"),
                    label_visibility="hidden",
                )
        elif trancheNum == 3:
            for i in range(0, trancheNum):
                seniority_dict[i] = st.selectbox(
                    f"Tranche Seniority {i+1}",
                    ("Senior", "Mezzanine", "Junior"),
                    label_visibility="hidden",
                )
        else:
            for i in range(0, trancheNum):
                seniority_dict[i] = st.selectbox(
                    f"Tranche Seniority {i+1}",
                    ("Senior 1", "Senior 2", "Mezzanine 1", "Mezzanine 2", "Junior"),
                    label_visibility="hidden",
                )
    with c2:

        st.text("Tranche Amount")
        amount = 0
        for i in range(0, trancheNum):
            amount_dict[i] = st.number_input(
                f"Tranche {i+1} Amount",
                min_value=0,
                step=1000,
                label_visibility="hidden",
            )
            amount = amount + amount_dict[i]

    if trancheNum == 4:
        paymentType = st.radio(
            "Payment Priority", ["Sequential", "Prorata Mezzanine", "Prorata Senior"]
        )
    elif trancheNum == 5:
        paymentType = st.radio(
            "Payment Priority",
            [
                "Sequential",
                "Prorata Mezzanine",
                "Prorata Senior",
                "Prorata Senior and Mezzanine",
            ],
        )
    else:
        paymentType = st.radio("Payment Priority", ["Sequential"])

    submitted = st.form_submit_button("Save properties")

propertiesDict = {}

for el1, el2 in zip(seniority_dict.values(), amount_dict.values()):
    propertiesDict[el1] = el2

propertiesDict = propertiesMapper(
    tranches=trancheNum, propertiesDictionary=propertiesDict
)

if amount != collateralAmount:
    st.markdown(
        "WARNING! The total amounts of the tranches must be equal to the collateral"
    )

if len(set(propertiesDict.keys())) != trancheNum:
    if trancheNum == 2:
        st.markdown("WARNING: At least one senior and junior tranche must be included")
    else:
        st.markdown(
            "WARNING: At least one senior, mezzanine and junior tranche must be included"
        )

if trancheNum == 4:
    check = 0
    for i in list(propertiesDict.keys()):
        if i == "Junior":
            check = 1
    if check == 0:
        st.markdown(
            "WARNING: At least one senior, mezzanine and junior tranche must be included"
        )

submit = st.button("Submit")

if submit:
    st.switch_page("pages/1_📙_Attachment_and_Detachment_Points.py")


# salvataggio degli input

if submit:
    st.session_state["collateralAmount"] = collateralAmount
    st.session_state["trancheNum"] = trancheNum
    st.session_state["secType"] = secType
    st.session_state["paymentType"] = paymentType
    st.session_state["propertiesDict"] = propertiesDict
    st.session_state["num_subpool"] = num_subpool
    st.session_state["Attachment"] = []
    st.session_state["Detachment"] = []
    st.session_state["Seniority dict"] = seniority_dict
