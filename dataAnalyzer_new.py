#packages import here

import os
import re
import pandas
import sys
import json
from collections import Counter
import itertools
import csv
import numpy as np
import StringIO


#variable declarations

newDirPointer = {}
customers = {}
masterPatList = {}
finalListWithSelectColumns = []
map_dict = {}
newDict = {}
map_dict_select = {}
new_dict_select = {}
selectColJoin = ''
primaryColumn ={}
primaryColumnPath={}
primaryOutputPath = {}
selectColumns= {}
outputDir = {}
selectColumnValueMap = {}
selectMap = {}
outputColumnDir = {}
selectColumnConditionMap = {}
operationMap = {}
uniqueTotalDF = {}
masterDict = {}
logicalOperatorMap = {}
usecolsMap = {}
summaryJson = {}

rangeVall = np.arange(14, 23)
l3 = list(rangeVall)


range_list = result2 = [str(x) for x in l3]
range_list_str = ', '.join("'{0}'".format(w) for w in range_list)
range_list_icd10 = ['C','D0','D1','D2','D3','D4']
range_list_icd10_str = ', '.join("'{0}'".format(w) for w in range_list_icd10)
summary_header = ["FileName","Total","Percentage"]
def percentage(part, whole):
  return 100 * float(part)/float(whole)
#Read a csv file using pandas
def readCsv(path,primary,select,useColsArr):
    #print primary
    usecols = []
    dtypes = {}
    usecols.append(primary)
    for col in select:
        if col not in usecols:
            usecols.append(col)
    for col in usecols:
        dtypes[col] = str
    if(len(useColsArr)>0):
        if '*' in useColsArr:
            dfcsv = pandas.read_csv(path, dtype=dtypes)
        else:
            for col in useColsArr:
              if col not in usecols:
                  usecols.append(col)
            dfcsv = pandas.read_csv(path, usecols=usecols, dtype=dtypes)
    else:
        dfcsv = pandas.read_csv(path,usecols =usecols,dtype=dtypes)

    return dfcsv

def getUniqueTotalCount(customer,primarycol,primaryPath,outputPath):
    primaryFiles = []
    masterCounter = Counter()

    for filename in os.listdir(primaryPath):
        if re.search(r'(Patient|Diagnosis|SHS_Diagnosis|SHS_Encounter|Encounter|Medorder|Medadmin|Testorder|ClinicalTestResult|CancerAssessment).*\./*',filename, re.IGNORECASE):
            primaryFiles.append(filename)
    for eachFile in primaryFiles:
        fileloc  = primaryPath + eachFile
        ext = os.path.splitext(fileloc)[-1].lower()
        if (ext == ".csv"):
            df = readCsv(fileloc, primarycol, [primarycol],[primarycol])
            df[primarycol] = df[primarycol].astype(str)
            counter = Counter(df[primarycol])
            if (len(masterCounter) > 0):
                masterCounter = masterCounter + counter
            else:
                masterCounter = counter
    masterList = masterCounter.keys()
    masterPatList[customer] = masterList
    with open(outputPath, "wb") as f:
        cw = csv.writer(f, delimiter=" ")
        cw.writerows(itertools.izip(masterList))
    return masterList



with open("config/config_dataAnalyzer.json","r") as f:
 config = json.loads(f.read())
 #print config
 customers = config["CUSTOMERS"]
 for customer in customers:
     #selectMap[customer] = {}
     selectColumnValueMap[customer] = {}
     newDirPointer[customer] = {}
     outputColumnDir[customer] = {}
     masterDict[customer] = {}
     logicalOperatorMap[customer]={}
     usecolsMap[customer] = {}
     #newDict[customer] = {}

     for key,value in customers[customer].items():
         primaryColumn[customer] = customers[customer]["PRIMARY_COLUMN"]
         primaryColumnPath[customer] = customers[customer]["PRIMARY_COLUMN_Path"]
         primaryOutputPath[customer] = customers[customer]["PRIMARY_COLUMN_Output"]
         outputDir[customer] =customers[customer]["OUTPUT"]["DIR"]+customers[customer]["OUTPUT"]["filename"]
         selectMap[customer] = customers[customer]["SELECT"]
         #Add validations to check all parameters exists:
         if(len(selectMap[customer])>0):
             for selectval in selectMap[customer]:
                 #print selectval["Path"]
                 selectColumnValueMap[customer][selectval["DataClass"]] = selectval["COLUMNS"]
                 if "USECOLS" in selectval:
                     if "*" in selectval["USECOLS"]:
                         usecolsMap[customer][selectval["DataClass"]] = []
                         usecolsMap[customer][selectval["DataClass"]].append("*")
                     else:
                         usecolsMap[customer][selectval["DataClass"]] = selectval["USECOLS"]
                 else:
                     usecolsMap[customer][selectval["DataClass"]] = []
                 if "OPERATOR" in selectval:
                    logicalOperatorMap[customer][selectval["DataClass"]] = selectval["OPERATOR"]
                 newDirPointer[customer][selectval["DataClass"]] = selectval["Path"]
                 outputColumnDir[customer][selectval["DataClass"]] = selectval["Output"]

 #get total count to compare with
     with open(outputDir[customer], 'a+') as output:
         writer = csv.writer(output, delimiter=',')
         if output.tell() == 0:
             writer.writerow(summary_header)


         if (primaryColumnPath[customer]!= ""):
            for customer in primaryColumn:
                uniqueTotalDF[customer] = getUniqueTotalCount(customer, primaryColumn[customer], primaryColumnPath[customer],primaryOutputPath[customer])
                writer.writerow([primaryOutputPath[customer],len(uniqueTotalDF[customer]),''])
 #print selectColumnValueMap
 #Do condition mapping here
 #print selectColumnValueMap
         for customer,value in selectColumnValueMap.items():
             selectColumnConditionMap[customer] = {}
             operationMap[customer] = {}
             for dataclass,column in value.items():
                 selectColumnConditionMap[customer][dataclass] = {}
                 operationMap[customer][dataclass] = {}
                 selectColumnConditionMap[customer][dataclass]["columns"] = []
                 for val in column:
                     val_split = val.split(":")

                     if val_split[0] in operationMap[customer][dataclass]:
                         if(len(val_split)>1):
                            operationMap[customer][dataclass][val_split[0]]["operation"][val_split[1]]=val_split[2]
                            #operationMap[customer][dataclass][val_split[0]]["value"].append(val_split[2])
                     else:
                         operationMap[customer][dataclass][val_split[0]] = {}
                         operationMap[customer][dataclass][val_split[0]]["operation"] = {}
                         if (len(val_split) > 1):
                            operationMap[customer][dataclass][val_split[0]]["operation"][val_split[1]]=val_split[2]
                            #operationMap[customer][dataclass][val_split[0]]["value"] = []
                            #operationMap[customer][dataclass][val_split[0]]["value"].append(val_split[2])


         #print operationMap

         #print operationMap["AURORA"]["Diagnosis"].keys()
         #sys.exit()

         files ={}
         for customer in newDirPointer:
             files[customer] = {}
             for dataclass,dir in newDirPointer[customer].items():
                 map_dict={}
                 newDict = {}
                 constraintMap = {}
                 #print dataclass
                 #print "DataClass"+dataclass
                 #masterDict[customer][dataclass] = {}
                 files[customer][dataclass] = []
                 for filename in os.listdir(dir):
                     if re.search(r'(Patient|Diagnosis|SHS_Diagnosis|SHS_Encounter|Encounter|Medorder|Medadmin|Testorder|ClinicalTestResult|CancerAssessment).*\./*',filename, re.IGNORECASE):
                         files[customer][dataclass].append(filename)

                 for f in files[customer][dataclass]:
                     filePath = dir + f
                     print 'reading file: ' + filePath
                     sys.stdout.flush()
                     ext = os.path.splitext(filePath)[-1].lower()
                     if (ext == ".csv"):
                         df = readCsv(filePath, primaryColumn[customer], operationMap[customer][dataclass].keys(),usecolsMap[customer][dataclass])
                     #print df
                     strVal = ""
                     selectColumns = operationMap[customer][dataclass].keys()
                     if(len(operationMap[customer][dataclass])>0):
                         for column,values in operationMap[customer][dataclass].items():
                             #if(len(values["operation"])== 0):

                             if "constraint" in values["operation"]:
                                 constraint = values["operation"]["constraint"]
                                 constraintMap[column] = constraint

                             for key,values in values["operation"].items():

                                 if(key == "range"):
                                     if (strVal != ""):
                                        strVal = strVal +logicalOperatorMap[customer][dataclass] +'(df["' + column + '"].str.startswith((' + range_list_str + ')))'
                                     else:
                                         strVal =strVal+'(df["'+column+'"].str.startswith(('+range_list_str+')))'
                                 elif(key == "startsWith"):
                                    valueArr = eval(values)
                                    valueArrStr =  ', '.join("'{0}'".format(w) for w in valueArr)
                                    #sys.exit()
                                    if(strVal!=""):
                                        strVal=strVal+' '+ logicalOperatorMap[customer][dataclass]+' (df["'+column+'"].str.startswith(('+valueArrStr+')))'
                                    else:
                                        strVal = strVal + '(df["' + column + '"].str.startswith((' + valueArrStr + ')))'

                                 elif(key == "value"):
                                     valuetoCheck = eval(values)
                                     if(len(valuetoCheck)>1):
                                         valuetoCheckStr = ', '.join("'{0}'".format(w) for w in valuetoCheck)
                                         if (strVal != ""):
                                            strVal = strVal +' ' +logicalOperatorMap[customer][dataclass] + ' (df["' + column + '"].isin(['+valuetoCheckStr+']))'
                                         else:
                                            strVal = strVal + '(df["' + column + '"].isin(['+valuetoCheckStr+']))'
                                     else:
                                         valuetoCheck = valuetoCheck[0]
                                         if (strVal != ""):
                                            strVal = strVal +' '+ logicalOperatorMap[customer][dataclass] + ' (df["' + column + '"]=='+'"'+str(valuetoCheck)+'")'
                                         else:
                                            strVal = strVal + '(df["' + column + '"]=='+'"'+str(valuetoCheck)+'")'
                                 else:
                                     #print "Iam here"
                                     pass
                         if(strVal == ""):
                             dfstr = "df = df"
                         else:
                            dfstr = "df = df[("+strVal+")]"

                         if(len(constraintMap)>0):
                             colArray = []
                             for col,constraint in constraintMap.items():
                                colArray.append(col)
                             if(len(colArray)>0):
                                 constraintStr = ""
                                 for col in colArray:
                                     if (constraintStr != ""):
                                         constraintStr = constraintStr + ' ' + logicalOperatorMap[customer][
                                             dataclass] + ' df["' + col + '"].notnull()'
                                     else:
                                         constraintStr = constraintStr + 'df["' + col + '"].notnull()'

                                 dfConststr = "df = df[("+constraintStr+")]"
                                 eval(compile(dfConststr, '<string>', 'exec'))


                         eval(compile(dfstr, '<string>', 'exec'))
                         if (len(map_dict) > 0):
                             newDict = dict(df.set_index(primaryColumn[customer]).groupby(level=0). \
                                            apply(lambda x: x.to_dict(orient='list')))

                             for patientid, value in newDict.items():
                                 for col in selectColumns:
                                     if col == primaryColumn[customer]:
                                         newDict[patientid][col] = list(set(newDict.keys()))
                                     else:
                                        newDict[patientid][col] = list(set(value[col]))
                                        value[col] = list(set(value[col]))

                                 for codetype, codevalue in value.items():
                                     # print "patientid: "+patientid
                                     # print codetype
                                     # print codevalue
                                     if patientid in map_dict:
                                         # print "map_dict value"
                                         # print map_dict[patientid][codetype]
                                         if codetype in map_dict[patientid]:
                                             for code in codevalue:
                                                 if code in map_dict[patientid][codetype]:
                                                     pass
                                                 else:
                                                     map_dict[patientid][codetype] = map_dict[patientid][codetype] + codevalue
                                         else:
                                             map_dict[patientid][codetype] = codevalue
                                     else:
                                         map_dict[patientid] = {}
                                         # map_dict[patientid][codetype] = []
                                         map_dict[patientid][codetype] = codevalue


                         else:

                             map_dict = dict(df.set_index(primaryColumn[customer]).groupby(level=0). \
                                             apply(lambda x: x.to_dict(orient='list')))
                             print selectColumns
                             for key, value in map_dict.items():
                                 for col in selectColumns:
                                     if col == primaryColumn[customer]:
                                         map_dict[key][col] = list(set(map_dict.keys()))
                                     else:
                                        map_dict[key][col] = list(set(value[col]))
                                        value[col] = list(set(value[col]))

                 #print dataclass
                 #print map_dict
                 finalDf = pandas.DataFrame.from_dict(map_dict, orient='index')
                 # print finalDf
                 finalDf.to_csv(outputColumnDir[customer][dataclass], index_label=primaryColumn[customer])
                 percent =percentage(len(finalDf),len(uniqueTotalDF[customer]))
                 writer.writerow([outputColumnDir[customer][dataclass],len(finalDf),str(round(percent, 2))+'%'])







