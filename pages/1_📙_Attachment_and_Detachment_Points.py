import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mtick
import seaborn as sns

st.title("Attachment and Detachment Points")
st.write("### Securitisation Structure")


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


def ADcalculator(collateral, secStructure, paymentPriority):
    # funzione per calcolo attachment e detachment point

    attachmentDict = dict.fromkeys(list(secStructure.keys()))
    detachmentDict = dict.fromkeys(list(secStructure.keys()))

    if paymentPriority == "Sequential":

        tmp = []

        for k in list(secStructure.keys()):

            attachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
            attachmentDict[k] = attachmentP

            tmp.append(k)

            detachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
            detachmentDict[k] = detachmentP

        return attachmentDict, detachmentDict

    elif paymentPriority == "Prorata Mezzanine":

        tmp = []
        prorataTranches = ["Mezzanine 2", "Mezzanine 1"]

        for k in list(secStructure.keys()):

            if k in prorataTranches:

                # tmp = ["Junior"]
                tmp = [tranche for tranche in tmp if tranche not in prorataTranches]

                attachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                attachmentDict[k] = attachmentP

                tmp.extend(prorataTranches)
                tmp = list(set(tmp))

                detachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                detachmentDict[k] = detachmentP

            else:

                attachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                attachmentDict[k] = attachmentP

                tmp.append(k)

                detachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                detachmentDict[k] = detachmentP

        return attachmentDict, detachmentDict

    elif paymentPriority == "Prorata Senior":

        tmp = []
        prorataTranches = ["Senior 2", "Senior 1"]

        for k in list(secStructure.keys()):

            if k in prorataTranches:

                tmp = [tranche for tranche in tmp if tranche not in prorataTranches]

                attachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                attachmentDict[k] = attachmentP

                tmp.extend(prorataTranches)
                tmp = list(set(tmp))

                detachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                detachmentDict[k] = detachmentP

            else:

                attachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                attachmentDict[k] = attachmentP

                tmp.append(k)

                detachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                detachmentDict[k] = detachmentP

        return attachmentDict, detachmentDict

    elif paymentPriority == "Prorata Senior and Mezzanine":

        tmp = []
        prorataTranches = ["Mezzanine 2", "Mezzanine 1"]
        prorataTranches2 = ["Senior 2", "Senior 1"]

        for k in list(secStructure.keys()):

            if k in prorataTranches:

                tmp = [tranche for tranche in tmp if tranche not in prorataTranches]

                attachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                attachmentDict[k] = attachmentP

                tmp.extend(prorataTranches)
                tmp = list(set(tmp))

                detachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                detachmentDict[k] = detachmentP

            elif k in prorataTranches2:

                tmp = [tranche for tranche in tmp if tranche not in prorataTranches2]

                attachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                attachmentDict[k] = attachmentP

                tmp.extend(prorataTranches2)
                tmp = list(set(tmp))

                detachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                detachmentDict[k] = detachmentP

            else:

                attachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                attachmentDict[k] = attachmentP

                tmp.append(k)

                detachmentP = (sum([secStructure[x] for x in tmp])) / (collateral)
                detachmentDict[k] = detachmentP

        return attachmentDict, detachmentDict


# input trasferiti da Home

try:
    st.markdown(
        "This section summarizes the inputs entered and presents the structure of the securitisation that you want to analyse:"
    )

    collateralAmount = st.session_state["collateralAmount"]
    secType = st.session_state["secType"]
    paymentType = st.session_state["paymentType"]
    num_subpool = st.session_state["num_subpool"]
    propertiesDict = st.session_state["propertiesDict"]
    seniority_dict = st.session_state["Seniority dict"]

    st.write("***Collateral Amount***: ", collateralAmount)
    st.write("***Type of Securitisation***: ", secType)
    st.write("***Payment Type***: ", paymentType)
    st.write("***Number of subpools***: ", num_subpool)

    st.write("***Table representing the tranche amount***:")
    tranche_val = pd.DataFrame(
        list((propertiesDict.items())), columns=["Seniority", "Tranche Amount"]
    )

    st.dataframe(data=tranche_val, hide_index=True)

    # calcolo attachment e detachment point

    A, D = ADcalculator(
        collateral=collateralAmount,
        secStructure=propertiesDict,
        paymentPriority=paymentType,
    )

    attachAmounts = {key: value * collateralAmount for key, value in A.items()}
    detachAmounts = {key: value * collateralAmount for key, value in D.items()}

    attachAmounts = pd.DataFrame([attachAmounts], index=["Attachment Point"])
    detachAmounts = pd.DataFrame([detachAmounts], index=["Detachment Point"])
    adAmounts = pd.concat([attachAmounts, detachAmounts])

    st.session_state["Attachment"] = A
    st.session_state["Detachment"] = D

    if paymentType == "Sequential":
        toplot = adAmounts.diff().dropna()
    elif paymentType == "Prorata Mezzanine":
        toplot = adAmounts.diff().dropna()
        toplot = pd.concat([toplot] * 2)
        toplot["Mezzanine 2"].iloc[0] = 0
        toplot["Mezzanine 1"].iloc[1] = 0
    elif paymentType == "Prorata Senior":
        toplot = adAmounts.diff().dropna()
        toplot = pd.concat([toplot] * 2)
        toplot["Senior 2"].iloc[0] = 0
        toplot["Senior 1"].iloc[1] = 0
    else:
        toplot = adAmounts.diff().dropna()
        toplot = pd.concat([toplot] * 2)
        toplot["Senior 2"].iloc[0] = 0
        toplot["Senior 1"].iloc[1] = 0
        toplot["Mezzanine 2"].iloc[0] = 0
        toplot["Mezzanine 1"].iloc[1] = 0

    st.write("***Table representing the Attachment and Detachment Points %***:")
    AD_amounts = st.dataframe(
        adAmounts / collateralAmount * 100,
        column_config={
            "Junior": st.column_config.NumberColumn(format="%.2f %%"),
            "Senior": st.column_config.NumberColumn(format="%.2f %%"),
            "Senior 1": st.column_config.NumberColumn(format="%.2f %%"),
            "Senior 2": st.column_config.NumberColumn(format="%.2f %%"),
            "Mezzanine": st.column_config.NumberColumn(format="%.2f %%"),
            "Mezzanine 1": st.column_config.NumberColumn(format="%.2f %%"),
            "Mezzanine 2": st.column_config.NumberColumn(format="%.2f %%"),
        },
    )

    st.write("### Charts")
    st.write(
        "*The graph on the left represents how attachment and detachment points are distributed based on the seniority of the tranches. The chart on the right shows the tranche amounts.*"
    )

    # plot grafico attachment e detachment point

    try:
        palette = sns.color_palette("Oranges_r")
        fig, ax = plt.subplots(1, 2)
        ax[0].get_yaxis().set_major_formatter(
            mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ","))
        )
        toplot.plot(
            kind="bar",
            stacked=True,
            bottom=adAmounts.iloc[0]["Junior"],
            ax=ax[0],
            legend=False,
            width=1.0,
            color=palette,
            xticks=[],
        )
        ax[0].legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.05),
            fancybox=True,
            shadow=True,
            ncol=2,
        )
        ax[0].set_title("Attachment & Detachment Points")
        ax[1].bar(propertiesDict.keys(), propertiesDict.values(), color=palette)
        ax[1].set_title("Tranches Amounts")
        ax[1].bar_label(ax[1].containers[0], label_type="edge", fmt="{:,.0f}", size=6)
        ax[1].set_axisbelow(True)
        ax[1].get_yaxis().set_visible(False)
        plt.xticks(rotation=90)

        st.pyplot(fig)
    except:
        pass

    st.session_state["Attachment"] = A
    st.session_state["Detachment"] = D

except:
    st.markdown("**Insert inputs in Home page.**")
