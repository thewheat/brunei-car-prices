############################ 
# Dependencies
############################
import os
import re
import csv
FOLDER = "output_text"
OUTPUT = "output_csv"
OUTPUT_ALL = os.path.join(OUTPUT, "all.csv")
#
# Issues and observations
# ## Regarding conversion
# - Some PDF to sheet converters have issues with page breaks leading to missing information. They do seem to mostly do column matching well but row matching not so much
# - PDF to text preserves the layout mostly but requires manual parsing. Sometimes row with $ does not have full content has data spans multiple lines so may need to look above and below current row for full info
# - Company names in left column in some older ones, in individual rows in newer oness
# ## Regarding data
# - Columns not all the same counts and orders
# - Data rows are inconsistent lengths. Some have only 1 row some span multiple rows
# - Some have 2 prices: show room price and on the road price
# - Some have only 1 price: show room price

def convertTextFilesToCSV(input, output, space):
  path = input

  if os.path.exists(path):
    for f in sorted(os.listdir(path)):
      full_path = os.path.join(path, f)
      if os.path.isdir(full_path):
        convertTextFilesToCSV(full_path, output, space + "   ")
      elif(f.lower().endswith(".txt")):
        output_dir = os.path.join(OUTPUT, path[len(os.path.join(FOLDER,"")):])
        if not os.path.exists(output_dir):
          os.makedirs(output_dir)

        output = os.path.join(output_dir, f)
        writeJSON(full_path, output)

def writeJSON(input, output):
    output = output + ".csv"
    date = []
    allLines = []
    with open(input, encoding="utf-8") as f:
        for line in f:
            allLines.append(line)
            if len(date) == 0:
                for delimiter in ["as of", "during month of"]:
                    if delimiter in line.lower():
                        date = extractDate(line, delimiter)

    lineNo = -1


    # print(output)

    output_year = os.path.join(OUTPUT, str(date[2]) + ".csv")

    if not os.path.exists(output_year):
       initCSV(output_year)

    with open(OUTPUT_ALL, 'a') as f_all:
      writer_all = csv.writer(f_all)
      with open(output_year, 'a') as f_year:
        writer_year = csv.writer(f_year)
        with open(output, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header())
            with open(input, encoding="utf-8") as f:
              for lineRaw in f:
                lineNo += 1
                line = removeDates(lineRaw, date)
                if "$" in line:
                  lineParts = getParts(line, date, lineNo, allLines)       
                  writer.writerow([date[2], date[1], date[0]] + lineParts)
                  writer_all.writerow([date[2], date[1], date[0]] + lineParts)
                  writer_year.writerow([date[2], date[1], date[0]] + lineParts)



def dateStringToNumber(str):
   if str == "january":
      return 1;
   elif str == "february":
      return 2;
   elif str == "march":
      return 3;
   elif str == "april":
      return 4;
   elif str == "may":
      return 5;
   elif str == "june":
      return 6;
   elif str == "july":
      return 7;
   elif str in ["augu", "ogos"]:
      return 8;
   elif str == "september":
      return 9;
   elif str in ["october", "oktober"]:
      return 10;
   elif str == "november":
      return 11;
   elif str in ["december", "disember"]:
      return 12;
   else:
      print("Unknown month: %s" % str)

# extract date from header text at start of doc
def extractDate(line, delimiter):
  dateComponent = line.lower().split(delimiter)[1]
  dateRaw = re.sub('st |nd |th |rd |hb ',' ', dateComponent).split()
  
  if len(dateRaw) == 2:
    day = None
    month = int(dateStringToNumber(dateRaw[0]))
    year = int(dateRaw[1])
  if len(dateRaw) == 3:
    day = int(dateRaw[0])
    month = int(dateStringToNumber(dateRaw[1]))
    year = int(dateRaw[2])

  return [day, month, year]   

# for a single line, get the important parts
# line with price may have details above and below

def getParts(line, date, lineIndex, allLines):
    lineParts0 = line.split("   ")
    lineParts1 = removeBlanks(lineParts0)
    lineParts2 = combineDollar(lineParts1)
    lineParts3 = removeNumberColumn(lineParts2)
    lineParts4 = removeHigherCost(lineParts3, date, lineIndex, allLines)
    linePartsFinal = lineParts4

    error = False
    if(len(linePartsFinal) > 0):
      if(not '$' in linePartsFinal[len(linePartsFinal)-1]):
        error = True
        print("ERROR!! No price in extracted data")
    else:
      error = True

    if(len(linePartsFinal) == 3):
      if '(' in linePartsFinal[0] or \
        linePartsFinal[1].startswith(linePartsFinal[0].split("-")[0]) or \
        linePartsFinal[1].startswith(linePartsFinal[0].split(" ")[0]):
        # first column is company name or brand name and brand is repeated in second column
        del(linePartsFinal[0])
      elif linePartsFinal[0] == 'YEAR' and date in [[15, 4, 2016], [15, 5, 2016], [15, 6, 2016], [15, 7, 2016], [15, 8, 2016], [30, 4, 2016], [30, 5, 2016], [30, 6, 2016], [30, 7, 2016], [31, 8, 2016]] :
          # weird formating for this PDF so manually override
           linePartsFinal[1] = "VOLV0 V40 T4 2.0L AUTO HATCH BACK PETROL"
           del(linePartsFinal[0])
      else:
        print("ERROR!! Unrecognized 3 column layout")
        print(date)
        print(linePartsFinal)
        error = True

    if(len(linePartsFinal) == 1):
      error = True
      index = lineIndex
      data = []
      while True:
        index -= 1
        if len(allLines[index].strip()) <= 1 or '$' in allLines[index]:
           break
        data.insert(0,allLines[index].strip().replace("\n",""))
        if len(allLines[index].strip()) > 2:
           break

      index = lineIndex
      while True:
        index += 1
        if len(allLines[index].strip()) <= 1 or '$' in allLines[index] or \
          ('showroom' in allLines[index].lower() and date == [15,1,2017]):
           break
        data.append(allLines[index].strip().replace("\n",""))
        if len(allLines[index].strip()) > 2:
           break

      return getParts(" ".join(data) + "   " + linePartsFinal[0], date, lineIndex, allLines)
    if error:
      print((linePartsFinal))
      print("date     : ", date)
      print("raw      : ", allLines[lineIndex])
      print("raw[]    : ", "\n".join(allLines[lineIndex-4:lineIndex]))
      #exit(0)      
    return linePartsFinal

def removeDates(line, date):
    # manually verified all look to be correct
    # of format DD-MMM-YY or DD/MMM/YY
    line1 = re.sub("\\d+-[A-Za-z]+-\\d+", "", line)
    line2 = re.sub("\\d+/[A-Za-z]+/\\d+", "", line1)

    # fix bad formatting
    if date in [[15, 11, 2017], [30, 11, 2017]] :
      return line2.replace("15/11/170", "")
    elif date == [15, 12, 2017]:
      return line2.replace("111/12/18", "")
    elif date in [[30, 9, 2019],[15, 11, 2019],[30, 9, 2019],[31, 10, 2019]] :
      return line2.replace("27/0/2019", "")

    return line2

def removeBlanks(partsArr):
    newParts = []
    for part in partsArr:
      #if(len(part.strip()) > 0 and part.strip() != "\n"):
      if(len(part.strip()) > 0):
        newParts.append(part.strip())
    return newParts

def combineDollar(partsArr):
   return combineEndDollar(combineSingleDollar(partsArr))

def combineEndDollar(partsArr):
    newParts = []
    prefix = False
    for part in partsArr:
      trimmedStr = str(part).strip()
      if trimmedStr.endswith("$"):
        if prefix:
          newParts.append('$' + trimmedStr[:-1].strip())
        else:
          newParts.append(trimmedStr[:-1].strip())
        prefix = True
      else :
        if prefix:
          newParts.append('$' + part)
        else:
          newParts.append(part)
        prefix = False
    return newParts

def combineSingleDollar(partsArr):
    newParts = []
    prefix = False
    for part in partsArr:
      if str(part).strip() == '$':
        prefix = True
      else :
        if prefix:
          newParts.append('$' + part)
        else:
          newParts.append(part)
        prefix = False
    return newParts


# manually fix bad costs
def fixBadCostData(partsArr, date):
    str = " ".join(partsArr)
    if date in [[24, 11, 2022], [19, 1, 2023]] and "MERCEDES BENZ C300" in str:
       for i,part in enumerate(partsArr):
          if '939,433.00' in part:
             partsArr[i] = "$93,943.00"
    elif date == [2, 12, 2021] and "LEXUS ES250 2.5L F-SPORT" in str:
       for i,part in enumerate(partsArr):
          if '77,897.00' in part:
            partsArr[i] = "$78,201.00"
    elif date in [[15, 12, 2020], [22, 12, 2020], [31, 12, 2020]] and "AUDI A6" in str and "BLACK EDITION" in str:
       for i,part in enumerate(partsArr):
          if '83,572.00' in part:
             partsArr[i] = "$86,740.00"              
    return partsArr

def getCost(str):
   return float(re.sub("[ $,]", "", str))
   
def removeHigherCost(partsArrRaw, date, index, lines):
    max = 0
    newParts = []
    dollarColumns = 0
    partsArr = fixBadCostData(partsArrRaw.copy(),date)

    for part in partsArr:
      if '$' in part:
       dollarColumns += 1
       cost = getCost(part)
       if(cost > max):
          max = cost

    if dollarColumns < 2:
       return partsArr


    for i,part in enumerate(partsArr):
      if '$' in part and not max is None:
        if(getCost(part) != max):
          newParts.append(part)
        else:
          if i != len(partsArr) - 1 and getCost(partsArr[len(partsArr)-1]) != max:
             print("2nd price (OTR) more than 1st price (Showroom)")
             print(f"%s %s" % (date, partsArr))
          max = None # sometimes values repeatts, only delete once
      else:
          newParts.append(part)
    return newParts

def removeNumberColumn(partsArr):
    newParts = []
    for part in partsArr:
      if not re.match("\\d+.\\d+", part) and not re.match("#REF!", part, flags=re.I):
        newParts.append(part.strip())
    return newParts


def header():
   return ["Year", "Month", "Day", "Car", "Showroom Price (BND)"]

def initCSV(output):
  with open(output, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header())

def init():
  if not os.path.exists(OUTPUT):
    os.makedirs(OUTPUT)
  initCSV(OUTPUT_ALL)

init()
convertTextFilesToCSV(FOLDER, OUTPUT, "")