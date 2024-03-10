import os
import re
import shutil

INPUT_FOLDER = "DEPD Documents Library/KH/cars/"
OUTPUT_FOLDER = "output_pdf"

def convertPDFsToText(input, output, year, space):
  path = input
  folder_name = os.path.basename(path)
  print("%s%s" % (space, folder_name))
  if year is None and len(folder_name) == 4 and re.match("\d+", folder_name, re.I):
    year = int(folder_name)
  
  if os.path.exists(path):
    sum_folder = None
    for f in sorted(os.listdir(path)):
      full_path = os.path.join(path, f)
      if sum_folder is None and os.path.isdir(full_path) and re.match(".*sum.*", f, re.I):
        sum_folder = f
    if sum_folder:
      full_path = os.path.join(path, sum_folder)
      if os.path.isdir(full_path):
        convertPDFsToText(full_path, output, year,space + "   ")
    else: 
      for f in sorted(os.listdir(path)):
        full_path = os.path.join(path, f)
        if os.path.isdir(full_path):
          convertPDFsToText(full_path, output, year, space + "   ")
        elif(f.lower().endswith(".pdf")):
          print("   %s%s: %s" % (space, year, f))
          copyPdf(full_path, year)

def copyPdf(input, year_folder):
  output_dir = os.path.join(OUTPUT_FOLDER, str(year_folder))
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)

  shutil.copy(input, output_dir)


convertPDFsToText(INPUT_FOLDER, OUTPUT_FOLDER, None, "")
