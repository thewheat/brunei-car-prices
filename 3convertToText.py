import os
import subprocess

INPUT_FOLDER = "output_pdf"
OUTPUT_FOLDER = "output_text"

def convertPDFsToText(input, output, space):
  path = input
  print("%sRead %s" % (space, path))

  if os.path.exists(path):
    for f in sorted(os.listdir(path)):
      full_path = os.path.join(path, f)
      if os.path.isdir(full_path):
        convertPDFsToText(full_path, output, space + "   ")
      elif(f.lower().endswith(".pdf")):
        print(f"%s   %s" % (space, f))
        output_dir = os.path.join(OUTPUT_FOLDER, path[len(os.path.join(INPUT_FOLDER,"")):])
        if not os.path.exists(output_dir):
          os.makedirs(output_dir)

        output = os.path.join(output_dir, f + ".txt" )
        writePdf(full_path, output)

def writePdf(input, output):
  subprocess.run(["pdftotext", "-layout", input, output])  # doesn't capture output


convertPDFsToText(INPUT_FOLDER, OUTPUT_FOLDER, "")
