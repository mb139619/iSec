import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mtick
import seaborn as sns

st.title("SEC-SA RW Calculator")

st.markdown(
    """This page allows the calculation of ***Risk Weights*** with the **SEC-SA** model starting from the inputs entered on the Home page. 
            
*Add the following inputs related to this specific model*:"""
)


def kssfaCalculator(AttachmentPoint, DetachmentPoint, Ka, rho):

    # Funzione che calcola il Kssfa

    a = -1 / (rho * Ka)
    u = DetachmentPoint - Ka
    l = max(AttachmentPoint - Ka, 0)

    return (np.exp(a * u) - np.exp(a * l)) / (a * (u - l))


def SEC_SA_RW(
    secTypology,
    AttachmentPoints,
    DetachmentPoints,
    delinquencyInfo,
    delinquencyRatio,
    EAD,
    num_subpool,
    RW_ptf,
    underlyingTypology,
):
    # Funzione per il calcolo dei RW

    if secTypology == "STS":
        p = 0.5
    elif secTypology == "Resecuritisation":
        p = 1.5
        delinquencyRatio = 0
    else:
        p = 1

    Ksa = np.empty(num_subpool)
    for i in range(0, num_subpool, 1):
        Ksa[i] = RW_ptf * 0.08
    kWunknown = 1 - delinquencyInfo
    if secTypology == "Resecuritisation":
        kWknown = delinquencyInfo * Ksa[i]
    else:
        if num_subpool == 1:
            kWknown = delinquencyInfo * (
                (1 - delinquencyRatio[0]) * Ksa[0] + delinquencyRatio[0] * 0.5
            )
        else:
            kWknown_0 = 0
            for i in range(0, num_subpool, 1):
                kWknown_0 = (
                    kWknown_0
                    + EAD[i] * (1 - delinquencyRatio[i]) * Ksa[i]
                    + 0.5 * EAD[i] * delinquencyRatio[i]
                )
            kWknown = kWknown_0 * delinquencyInfo
    KaTotal = kWunknown + kWknown

    kssfa = dict.fromkeys(list(attachAmounts.keys()))
    RW_prev = dict.fromkeys(list(attachAmounts.keys()))
    RW = dict.fromkeys(list(attachAmounts.keys()))

    for key in kssfa.keys():

        # impostazione condizioni sul floor
        if (RW_ptf == 0) & (
            (key == "Senior") or (key == "Senior 1") or (key == "Senior 2")
        ):
            floor = 0
        elif secTypology == "Resecuritisation":
            floor = 1
        elif (secTypology == "STS") & (
            (key == "Senior") or (key == "Senior 1") or (key == "Senior 2")
        ):
            floor = 0.1
        else:
            floor = 0.15

        for i in range(0, num_subpool, 1):
            if (underlyingTypology[i] == "Mortgage Non Performing") or (
                underlyingTypology[i] == "Non Performing"
            ):
                floor = 1

        # impostazione condizioni sul cap
        if (secTypology != "Resecuritisation") & (
            (key == "Senior") or (key == "Senior 1") or (key == "Senior 2")
        ):
            cap = RW_ptf
        else:
            cap = -1

        # calcolo Kssfa
        if RW_ptf == 0:
            kssfa[key] = 0
        else:
            kssfa[key] = kssfaCalculator(
                AttachmentPoint=AttachmentPoints[key],
                DetachmentPoint=DetachmentPoints[key],
                Ka=KaTotal,
                rho=p,
            )

        # calcolo RW con Ka totale condizionato ad attachment e detachment points
        if KaTotal <= AttachmentPoints[key]:
            RW_prev[key] = kssfa[key] * 12.5
        elif (KaTotal > AttachmentPoints[key]) & (KaTotal < DetachmentPoints[key]):
            RW_prev[key] = (
                (KaTotal - AttachmentPoints[key])
                / (DetachmentPoints[key] - AttachmentPoints[key])
                * 12.5
            ) + (
                (DetachmentPoints[key] - KaTotal)
                / (DetachmentPoints[key] - AttachmentPoints[key])
                * 12.5
                * kssfa[key]
            )
        else:
            RW_prev[key] = 12.5

        # calcolo RW con condizioni su cap e floor
        if (
            (RW_ptf < floor)
            & (secTypology != "Resecuritisation")
            & ((key == "Senior") or (key == "Senior 1") or (key == "Senior 2"))
        ):
            RW[key] = RW_ptf * 100
        elif RW_prev[key] < floor:
            RW[key] = floor * 100
        else:
            if (cap != -1) & (RW_prev[key] > cap) & (RW_prev[key] < 12.5):
                RW[key] = cap * 100
            else:
                RW[key] = RW_prev[key] * 100

        # condizione delinquency info < 95% --> il RW della tranche è 1250%
        if delinquencyInfo < 0.95:
            RW[key] = 1250

    return RW


try:
    # input da Home

    collateralAmount = st.session_state["collateralAmount"]
    trancheNum = st.session_state["trancheNum"]
    secType = st.session_state["secType"]
    paymentType = st.session_state["paymentType"]
    propertiesDict = st.session_state["propertiesDict"]
    num_subpool = st.session_state["num_subpool"]

    rwTable = pd.read_excel("RWtableSECSA.xlsx")

    EAD = np.empty(num_subpool)
    W = np.empty(num_subpool)
    underlyingTypology = ["" for x in range(num_subpool)]

    with st.form("SubpoolProperties"):

        c1, c2, c3 = st.columns(3)

        with c1:
            EAD_tot = 0

            for i in range(0, num_subpool, 1):
                EAD[i] = (
                    st.number_input(
                        f"EAD % Subpool {i+1}",
                        min_value=0.00,
                        value=0.00,
                        max_value=100.00,
                        step=1.00,
                    )
                    / 100
                )
                EAD_tot = EAD_tot + EAD[i]
                # controllo EAD
            if EAD_tot != 1:
                st.markdown("WARNING: Sum of Exposure At Default % (EAD%) must be 100%")

        with c2:

            for i in range(0, num_subpool, 1):
                W[i] = (
                    st.number_input(
                        f"Delinquency Ratio % Subpool {i+1}",
                        min_value=0.00,
                        value=0.00,
                        max_value=100.00,
                        step=1.00,
                    )
                    / 100
                )

        with c3:

            for i in range(0, num_subpool, 1):
                underlyingTypology[i] = st.selectbox(
                    label=f"Select {i+1} Underlying typology",
                    options=rwTable["DEAL_TYPE"],
                )
        DI = (
            st.number_input(
                "% of underlying assets for which deliquency status is known",
                min_value=0.00,
                value=0.00,
                max_value=100.00,
                step=1.00,
            )
            / 100
        )

        submitted = st.form_submit_button("Calculate")

    # Attachment e Detachment calcolati in Attachment_Detachment

    A = st.session_state["Attachment"]
    D = st.session_state["Detachment"]

    attachAmounts = {key: value * collateralAmount for key, value in A.items()}
    detachAmounts = {key: value * collateralAmount for key, value in D.items()}

    attachAmounts = pd.DataFrame([attachAmounts], index=["Attachment Point"])
    detachAmounts = pd.DataFrame([detachAmounts], index=["Detachment Point"])
    adAmounts = pd.concat([attachAmounts, detachAmounts])

    # gestione dei subpool per il calcolo della media pesata del RWstd
    RWstd = np.empty(num_subpool)
    RWEA = np.empty(num_subpool)
    defaultRW = np.empty(num_subpool)
    if num_subpool == 1:
        RWstd = float(
            rwTable.loc[rwTable["DEAL_TYPE"] == underlyingTypology[i]]["RW_STD"]
        )
        defaultRW = float(
            rwTable.loc[rwTable["DEAL_TYPE"] == underlyingTypology[i]]["RW_DEF"]
        )
        if (underlyingTypology[i] == "SME Retail") or (
            underlyingTypology[i] == "SME Corporate"
        ):
            RWEA = (
                RWstd
                * (
                    min(collateralAmount, 2500000) * 0.7619
                    + max(collateralAmount - 2500000, 0) * 0.85
                )
                / collateralAmount
            )
        else:
            RWEA = RWstd

        RW_ptf = (RWEA * (1 - W[0]) + defaultRW * W[0]) * EAD[0]
    else:
        RW_ptf = 0
        EAD_tot = 0
        for i in range(0, num_subpool, 1):
            RWstd[i] = float(
                rwTable.loc[rwTable["DEAL_TYPE"] == underlyingTypology[i]]["RW_STD"]
            )
            defaultRW[i] = float(
                rwTable.loc[rwTable["DEAL_TYPE"] == underlyingTypology[i]]["RW_DEF"]
            )
            if (underlyingTypology[i] == "SME Retail") or (
                underlyingTypology[i] == "SME Corporate"
            ):
                RWEA[i] = (
                    RWstd[i]
                    * (
                        min(collateralAmount, 2500000) * 0.7619
                        + max(collateralAmount - 2500000, 0) * 0.85
                    )
                    / collateralAmount
                )
            else:
                RWEA[i] = RWstd[i]
            RW_ptf = RW_ptf + (RWEA[i] * (1 - W[i]) + defaultRW[i] * W[i]) * EAD[i]

    # calcolo RW
    secRW = SEC_SA_RW(
        secType, A, D, DI, W, EAD, num_subpool, RW_ptf, underlyingTypology
    )

    # ricalcolo seniority
    for key in secRW.keys():
        if (key == "Mezzanine") or (key == "Mezzanine1") or (key == "Mezzanine2"):
            if secRW[key] < 25:
                st.markdown(
                    "WARNING: the risk weight for the mezzanine tranche should be recalculated by classifying the tranche as senior"
                )
            if secRW[key] == 1250:
                st.markdown(
                    "WARNING: the risk weight for the mezzanine tranche should be recalculated by classifying the tranche as junior"
                )

    st.markdown(
        "Below you can see the table and graph of the risk weights calculated for each individual tranche:"
    )

    # tabella RW
    dfRW = pd.DataFrame(list((secRW.items())), columns=["Seniority", "Risk Weight"])
    st.dataframe(
        dfRW,
        hide_index=True,
        column_config={"Risk Weight": st.column_config.NumberColumn(format="%.2f %%")},
    )

    # grafico RW
    palette = sns.color_palette("Blues_r")

    fig, ax = plt.subplots()
    ax.bar(list(secRW.keys()), secRW.values(), color=palette)
    ax.set_title("Risk Weights SEC-SA")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

    st.pyplot(fig)

except:
    st.markdown("**Insert inputs in Home page.**")
