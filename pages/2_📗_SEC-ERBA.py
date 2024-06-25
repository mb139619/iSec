import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mtick
import datetime as dt
import seaborn as sns

st.title("SEC-ERBA RW Calculator")

st.markdown(
    """This page allows the calculation of ***Risk Weights*** with the **SEC-ERBA** model starting from the inputs entered on the Home page. 
            
*Add the following inputs related to this specific model*:"""
)


def SEC_ERBA_RW(rwTable, CqS, long_short, AttachmentPoints, DetachmentPoints, maturity):

    RW = dict.fromkeys(list(attachAmounts.keys()))
    RW = dict.fromkeys(list(attachAmounts.keys()))

    for key in RW.keys():

        # tickness
        T = DetachmentPoints[key] - AttachmentPoints[key]

        if long_short == "short":
            RW_M = float(
                rwTable.loc[rwTable["Credit Quality Step"] == CqS]["Risk Weight"]
            )
        else:
            if (key == "Senior") or (key == "Senior 1") or (key == "Senior 2"):
                RW1 = float(
                    rwTable.loc[rwTable["Credit Quality Step"] == CqS]["1 year senior"]
                )
                RW5 = float(
                    rwTable.loc[rwTable["Credit Quality Step"] == CqS]["5 years senior"]
                )
            else:
                RW1 = float(
                    rwTable.loc[rwTable["Credit Quality Step"] == CqS][
                        "1 year non-senior"
                    ]
                )
                RW5 = float(
                    rwTable.loc[rwTable["Credit Quality Step"] == CqS][
                        "5 years non-senior"
                    ]
                )

            RW_M = RW1 + (maturity - 1) * (RW5 - RW1) / 4

        if (key == "Senior") or (key == "Senior 1") or (key == "Senior 2"):
            RW[key] = RW_M * 100
        else:
            RW[key] = RW_M * (1 - min(T, 0.5)) * 100

        # check floor

        floor = 15

        if RW[key] < floor:
            RW[key] = floor
        else:
            pass

    # check "the resulting risk weights shall be no lower than the Risk Weight corresponding to a hypothetical senior tranche of the same securitisation with the same credit assessment and maturity"

    if list(RW.values()) == sorted(list(RW.values()), reverse=True):
        pass
    else:
        lunghezza = len(list(RW.keys()))
        list1 = list(reversed(list(RW.values())))
        key_list = list(reversed(list(RW.keys())))
        for i in range(1, lunghezza):
            if list1[i] < list1[i - 1]:
                RW[key_list[i]] = RW[key_list[i - 1]]
                list1[i] = list1[i - 1]
            else:
                pass

    return RW


try:
    # Home input

    collateralAmount = st.session_state["collateralAmount"]
    trancheNum = st.session_state["trancheNum"]
    secType = st.session_state["secType"]
    paymentType = st.session_state["paymentType"]
    propertiesDict = st.session_state["propertiesDict"]
    num_subpool = st.session_state["num_subpool"]

    # Attachment e Detachment calcolati in Attachment_Detachment

    A = st.session_state["Attachment"]
    D = st.session_state["Detachment"]

    attachAmounts = {key: value * collateralAmount for key, value in A.items()}
    detachAmounts = {key: value * collateralAmount for key, value in D.items()}

    attachAmounts = pd.DataFrame([attachAmounts], index=["Attachment Point"])
    detachAmounts = pd.DataFrame([detachAmounts], index=["Detachment Point"])
    adAmounts = pd.concat([attachAmounts, detachAmounts])

    vec = ["long", "short"]

    long_short = st.selectbox(label="Select Long or Short", options=vec)

    # calcolo maturity

    maturity = st.date_input(
        label="Maturity",
        value="default_value_today",
        min_value=None,
        max_value=None,
        key=None,
        help=None,
        on_change=None,
        args=None,
        kwargs=None,
        format="YYYY/MM/DD",
        disabled=False,
        label_visibility="visible",
    )

    oggi = dt.date.today()

    ML = maturity - oggi
    ML = ML.days / 365

    # aggiustamento maturity

    if ML < 1:
        MT = 1
    elif ML > 5:
        MT = 5
    else:
        MT = 1 + (ML - 1) * 0.8

    # scelta tabella RW in base al tipo di cartolarizzazione

    with st.form("SecProperties"):

        if secType == "STS":
            if long_short == "long":
                rwTable = pd.read_excel("long_STS.xlsx")
            else:
                rwTable = pd.read_excel("short_STS.xlsx")

        elif secType == "Standard":
            if long_short == "long":
                rwTable = pd.read_excel("long_std.xlsx")
            else:
                rwTable = pd.read_excel("short_std.xlsx")

        creditQualityStep = st.selectbox(
            label="Select Credit Quality Step", options=rwTable["Credit Quality Step"]
        )
        submitted = st.form_submit_button("Calculate")

    try:

        st.markdown(
            "Below you can see the table and graph of the risk weights calculated for each individual tranche:"
        )

        # calcolo RW
        secRW = SEC_ERBA_RW(rwTable, creditQualityStep, long_short, A, D, MT)

        # tabella RW
        dfRW = pd.DataFrame(list((secRW.items())), columns=["Seniority", "Risk Weight"])

        st.dataframe(
            dfRW,
            hide_index=True,
            column_config={
                "Risk Weight": st.column_config.NumberColumn(format="%.2f %%")
            },
        )

        # grafico RW
        palette = sns.color_palette("Greens_r")

        fig, ax = plt.subplots()
        ax.bar(list(secRW.keys()), secRW.values(), color=palette)
        ax.set_title("Risk Weights SEC-ERBA")
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())

        st.pyplot(fig)

    except:
        pass

except:
    st.markdown("**Insert inputs in Home page.**")
