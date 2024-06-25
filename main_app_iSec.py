import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mtick

       

def propertiesMapper(tranches, propertiesDictionary):
   

   if tranches == 2:
      newdict = dict.fromkeys(["Junior", "Senior"])
      newdict.update(propertiesDict)
   elif tranches == 3:
      newdict = dict.fromkeys(["Junior", "Mezzanine" ,"Senior",])
      newdict.update(propertiesDict)
   else:
      newdict = dict.fromkeys(["Junior", "Mezzanine 2", "Mezzanine 1" ,"Senior 2", "Senior 1"])
      newdict.update(propertiesDict)

   newdict = {key: value for key, value in newdict.items() if value != None}

   return(newdict)


def ADcalculator(collateral, secStructure, paymentPriority, creditEnhancements, insuranceCoverage, maximumCoveredAmount):
    
    ceEuros = sum(creditEnhancements)*collateral
    coveredAmount = insuranceCoverage * maximumCoveredAmount    
    
    attachmentDict = dict.fromkeys(list(secStructure.keys()))
    detachmentDict = dict.fromkeys(list(secStructure.keys()))
    
    if paymentPriority == "Sequential":

        tmp  = []

        for k in list(secStructure.keys()):
            
            attachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral + ceEuros + coveredAmount)
            attachmentDict[k] = attachmentP

            tmp.append(k)

            detachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
            detachmentDict[k] = detachmentP

        return attachmentDict, detachmentDict
    
    elif paymentPriority == "Prorata Mezzanine":

        tmp = []
        prorataTranches = ["Mezzanine 2", "Mezzanine 1"]

        for k in list(secStructure.keys()):            

            if k in prorataTranches:
                
                #tmp = ["Junior"]
                tmp = [tranche for tranche in tmp if tranche not in prorataTranches]
                
                attachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                attachmentDict[k] = attachmentP

                tmp.extend(prorataTranches)
                tmp = list(set(tmp))

                detachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                detachmentDict[k] = detachmentP

            else:

                attachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                attachmentDict[k] = attachmentP

                tmp.append(k)

                detachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                detachmentDict[k] = detachmentP

        return attachmentDict, detachmentDict
    
    elif paymentPriority == "Prorata Senior":

        tmp = []
        prorataTranches = ["Senior 2", "Senior 1"]

        for k in list(secStructure.keys()):
         
            if k in prorataTranches:
                
                tmp = [tranche for tranche in tmp if tranche not in prorataTranches]
                
                attachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                attachmentDict[k] = attachmentP

                tmp.extend(prorataTranches)
                tmp = list(set(tmp))

                detachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                detachmentDict[k] = detachmentP

            else:

                attachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                attachmentDict[k] = attachmentP

                tmp.append(k)

                detachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                detachmentDict[k] = detachmentP

        return attachmentDict, detachmentDict

    elif paymentPriority == "Prorata Senior and Mezzanine":

        tmp = []
        prorataTranches = ["Mezzanine 2", "Mezzanine 1"]
        prorataTranches2 = ["Senior 2", "Senior 1"]

        for k in list(secStructure.keys()):

            if k in prorataTranches:
                
                tmp = [tranche for tranche in tmp if tranche not in prorataTranches]
                
                attachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                attachmentDict[k] = attachmentP

                tmp.extend(prorataTranches)
                tmp = list(set(tmp))

                detachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                detachmentDict[k] = detachmentP

            elif k in prorataTranches2:

                tmp = [tranche for tranche in tmp if tranche not in prorataTranches2]
                
                attachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                attachmentDict[k] = attachmentP

                tmp.extend(prorataTranches2)
                tmp = list(set(tmp))

                detachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                detachmentDict[k] = detachmentP

            else:

                attachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                attachmentDict[k] = attachmentP

                tmp.append(k)

                detachmentP = (sum([secStructure[x] for x in tmp])+ceEuros+coveredAmount)/(collateral+ceEuros+coveredAmount)
                detachmentDict[k] = detachmentP

        return attachmentDict, detachmentDict


def kssfaCalculator(AttachmentPoint, DetachmentPoint, Ka, rho):

    a = -1/(rho*Ka)
    u = DetachmentPoint - Ka
    l = max(AttachmentPoint-Ka, 0)

    return (np.exp(a*u)-np.exp(a*l))/(a*(u-l))

def SEC_SA_RW(secTypology, AttachmentPoints, DetachmentPoints, RWstd, delinquencyInfo, delinquencyRatio):

    if secTypology == "STS":
        p = 0.5
    elif secTypology == "Resecuritisation":
        p = 1.5
        delinquencyRatio = 0
    else:
        p = 1
    
    Ksa = RWstd * 0.08
    kWunknown = 1 - delinquencyInfo
    if secTypology == "Resecuritisation":
        kWknown = delinquencyInfo * Ksa 
    else:
        kWknown = delinquencyInfo * ((1- delinquencyRatio)*Ksa + delinquencyRatio * 0.5)
    KaTotal = kWunknown + kWknown

    
    kssfa = dict.fromkeys(list(attachAmounts.keys()))
    RW_prev = dict.fromkeys(list(attachAmounts.keys()))
    RW = dict.fromkeys(list(attachAmounts.keys()))

    for key in kssfa.keys():
        
        if (RWstd == 0) & ((key == "Senior") or (key == "Senior 1") or (key == "Senior 2")):
            floor = 0
        elif secTypology == "Resecuritisation":
            floor = 1
        elif (secTypology == "STS") & ((key == "Senior") or (key == "Senior 1") or (key == "Senior 2")):
            floor = 0.1
        else:
            floor = 0.15


        if (secTypology == "Resecuritisation") & ((key == "Senior") or (key == "Senior 1") or (key == "Senior 2")):
            cap = RWstd
        else:
            cap = -1
        
        
        if RWstd == 0:
            kssfa[key] = 0
        else:
            kssfa[key] = kssfaCalculator(AttachmentPoint=AttachmentPoints[key],DetachmentPoint= DetachmentPoints[key], Ka=KaTotal, rho = p)
        
        if KaTotal<=AttachmentPoints[key] :
            RW_prev[key] = kssfa[key]*12.5
        elif (KaTotal>AttachmentPoints[key]) & (KaTotal<DetachmentPoints[key]):
            RW_prev[key] = ((KaTotal-AttachmentPoints[key])/(DetachmentPoints[key]-AttachmentPoints[key])*12.5) + ((DetachmentPoints[key]-KaTotal)/(DetachmentPoints[key]-AttachmentPoints[key])*12.5*kssfa[key])
        else:
            RW_prev[key] = 12.5
        
        print(RWstd, floor, secTypology, key)

        if (RWstd<floor) & (secTypology != "Resecuritisation") & ((key == "Senior") or (key == "Senior 1") or (key == "Senior 2")):
            RW[key] = RWstd*100
        elif RW_prev[key] < floor:
            RW[key] = floor*100
        else:
            if (cap != -1) & (RW_prev[key]>cap) & (RW_prev[key]<12.5):
                RW[key] = cap*100
            else:
                RW[key] = RW_prev[key]*100
        
    return RW
    


st.title("SecSA Securitization RW Calculator")

collateralAmount = st.number_input("Collateral Amount", min_value = 0, step = 1000)

trancheNum = st.slider("Set the tranches number" , min_value = 2, max_value = 5, step = 1)

rwTable = pd.read_excel(".RWtableSECSA.xlsx")

underlyingTypology = st.selectbox(label = "Select Underlying typology", options=rwTable["DEAL_TYPE"])

secType = st.selectbox(
    'Securitisation Typology',
    ('Standard', 'STS', 'Resecuritisation'))

c1, c2 = st.columns(2)
with c1:
    DI = st.number_input("Delinquency Info %",  min_value=0.00, value = 0.00, max_value=1.00)
with c2:
    W = st.number_input("Delinquency Ratio %",  min_value=0.00, value = 0.00, max_value=1.00)


ceFlag = st.checkbox('Credit Enhancements')

with st.form("SecProperties"):
   
   c1, c2, c3 = st.columns(3)
   
   seniority_dict={}
   amount_dict   ={}
   outstanding_dict = {}

   with c1:
      
      st.text("Tranche Seniority")
      
      if trancheNum == 2:
         for i in range(0,trancheNum):
            seniority_dict[i]= st.selectbox(f'Tranche Seniority {i+1}', ("Senior", 'Junior'), label_visibility = "hidden")
      elif trancheNum == 3:
         for i in range(0,trancheNum):
            seniority_dict[i]= st.selectbox(f'Tranche Seniority {i+1}', ('Senior', 'Mezzanine', 'Junior'), label_visibility = "hidden")
      else:
         for i in range(0,trancheNum):
            seniority_dict[i]= st.selectbox(f'Tranche Seniority {i+1}', ('Senior 1', 'Senior 2', 'Mezzanine 1', 'Mezzanine 2', 'Junior'), label_visibility = "hidden")
   with c2:
      
      st.text("Tranche Amount")

      for i in range(0,trancheNum):
         amount_dict[i]= st.number_input(f'Tranche {i+1} Amount', min_value = 0, step = 1000, label_visibility = "hidden")

   with c3:
      
      st.text("Oustanding %")
      for i in range(0,trancheNum):
         outstanding_dict[i]= st.number_input(f'Tranche {i+1} Oustanding %',min_value=0.00,value = 100.00, max_value=100.00, label_visibility = "hidden")
       
      
   if trancheNum == 4:
       paymentType = st.radio("Payment Priority", ["Sequential", "Prorata Mezzanine", "Prorata Senior"]) 
   elif trancheNum == 5:
       paymentType = st.radio("Payment Priority", ["Sequential", "Prorata Mezzanine", "Prorata Senior", "Prorata Senior and Mezzanine"]) 
   else:
       paymentType = st.radio("Payment Priority", ["Sequential"])

    
   if ceFlag:
       
       co1, co2, co3 = st.columns(3)
       
       with co1:
           creditDisc = st.number_input('Credit Discount %', min_value=0.00, value = 0.00, max_value=100.00)/100
           excessSpread = st.number_input('Excess Spread %', min_value=0.00, value = 0.00, max_value=100.00)/100
       with co2:
           finDisc = st.number_input('Financial Discount %', min_value=0.00,value = 0.00, max_value=100.00)/100
           cashReserve = st.number_input('Cash Reserve %', min_value=0.00,value = 0.00, max_value=100.00)/100
       with co3:
           overcollateral = st.number_input('Overcollateral %', min_value=0.00,value = 0.00, max_value=100.00)/100

       col1, col2 = st.columns(2)

       with col1:
           coveredAmount = st.number_input('Covered Amount %', min_value=0.00,value = 0.00, max_value=100.00)/100
       with col2:
           maxCoveredAmount = st.number_input('Maximum Covered Amount', min_value=0, value = 0, step = 1000, max_value=collateralAmount)
   else:
       creditDisc = 0.00
       excessSpread = 0.00
       finDisc = 0.00
       cashReserve = 0.00
       overcollateral = 0.00
       coveredAmount = 0.00
       maxCoveredAmount = 0

   submitted = st.form_submit_button("Save properties")


ceArray = np.array([creditDisc, excessSpread, finDisc, cashReserve, overcollateral])


oustandingAmount = {k : np.array(v, dtype=float) * np.array(outstanding_dict[k]/100, dtype = float) for k, v in amount_dict.items() if k in outstanding_dict}

propertiesDict = {}

for el1, el2 in zip(seniority_dict.values(), oustandingAmount.values()):
     propertiesDict[el1] = el2

propertiesDict = propertiesMapper(tranches=trancheNum, propertiesDictionary=propertiesDict)


A, D = ADcalculator(collateral= collateralAmount, secStructure=propertiesDict, paymentPriority=paymentType, creditEnhancements=ceArray, insuranceCoverage=coveredAmount, maximumCoveredAmount=maxCoveredAmount)

attachAmounts = {key:value *collateralAmount for key, value in A.items()}
detachAmounts = {key:value *collateralAmount for key, value in D.items()}

attachAmounts = pd.DataFrame([attachAmounts], index = ["Attachment Point"])
detachAmounts = pd.DataFrame([detachAmounts], index = ["Detachment Point"])
adAmounts = pd.concat([attachAmounts, detachAmounts])


if paymentType == "Sequential":
    toplot = adAmounts.diff().dropna()
elif paymentType == "Prorata Mezzanine":
    toplot = adAmounts.diff().dropna()
    toplot = pd.concat([toplot]*2)
    toplot["Mezzanine 2"].iloc[0] = 0
    toplot["Mezzanine 1"].iloc[1] = 0
elif paymentType == "Prorata Senior":
    toplot = adAmounts.diff().dropna()
    toplot = pd.concat([toplot]*2)
    toplot["Senior 2"].iloc[0] = 0
    toplot["Senior 1"].iloc[1] = 0
else:
    toplot = adAmounts.diff().dropna()
    toplot = pd.concat([toplot]*2)
    toplot["Senior 2"].iloc[0] = 0
    toplot["Senior 1"].iloc[1] = 0
    toplot["Mezzanine 2"].iloc[0] = 0
    toplot["Mezzanine 1"].iloc[1] = 0


try: 
    fig, ax = plt.subplots(1, 2)
    ax[0].get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    toplot.plot(kind = "bar", stacked=True, bottom = adAmounts.iloc[0]["Junior"], ax = ax[0], legend=False, width=1.0, colormap="winter", xticks=[])
    ax[0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=2)
    ax[0].set_title("Attachment & Detachment Points")
    ax[1].bar(propertiesDict.keys(), propertiesDict.values())
    ax[1].set_title("Tranches Amounts")
    ax[1].bar_label(ax[1].containers[0], label_type='edge', fmt='{:,.0f}', size = 6)
    ax[1].set_axisbelow(True)
    ax[1].get_yaxis().set_visible(False)
    plt.xticks(rotation=90)

    st.pyplot(fig) 


    RWstd = float(rwTable.loc[rwTable["DEAL_TYPE"] == underlyingTypology]["RW_STD"])
    secRW = SEC_SA_RW(secTypology=secType, AttachmentPoints=A, DetachmentPoints=D, RWstd=RWstd, delinquencyInfo=DI, delinquencyRatio=W)

    dfRW = pd.DataFrame(list((secRW.items())), columns=['Seniority', 'Risk Weight'])

    st.dataframe(dfRW)

    fig,  ax = plt.subplots()
    ax.plot(list(secRW.keys()), secRW.values(), marker = "o")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())


    st.pyplot(fig) 
except:
    pass

