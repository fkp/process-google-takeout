import sys, os, argparse, re, datetime
from zipfile import ZipFile
import exifread
import shutil

parser = argparse.ArgumentParser(description='A script to extract iCloud information')

parser.add_argument("destinationDirectory", help="The destination directory to output to")
parser.add_argument("tempDirectory", help="The temp directory to use while extracting")
parser.add_argument("sourceZipFiles", nargs='+', help="The iCloud zip files to extract from")

args = parser.parse_args()

# The exif parameter we will use to determine the date of the image
exifParameter = "EXIF DateTimeOriginal"

with open("ignorediCloud" + datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S") + ".log", 'w', buffering=1) as ignoredFiles:

	for zipFile in args.sourceZipFiles:
	
		if os.path.isfile(zipFile):
			print ("About to process zip file: " + zipFile)
			
			# Create a temp subdirectory in the temp folder nominated
			tempextract = os.path.join(args.tempDirectory, "icloudtemp" + datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
			
			os.makedirs(tempextract)
			
			with ZipFile(zipFile,'r') as zipObj:
				zipObj.extractall(tempextract)
				
			extractedDirectory = os.path.join(tempextract,"iCloud Photos")
			
			for file in os.listdir(extractedDirectory):
			
				# Get the exif data
				fullFile = os.path.join(extractedDirectory,file)
				with open(fullFile, 'rb') as exifdata:
					tags = exifread.process_file(exifdata)

				if exifParameter in tags.keys():
		
					targetDirectory = os.path.join(args.destinationDirectory,f"{tags[exifParameter].printable[0:4]}\{tags[exifParameter].printable[0:4]}_{tags[exifParameter].printable[5:7]}")
					
					if (not(os.path.isdir(targetDirectory))):
						os.makedirs(targetDirectory)
						
					targetFile = os.path.join(targetDirectory, file)
					
					if (os.path.isfile(targetFile)):
						if (not(os.path.getsize(targetFile) == os.path.getsize(fullFile))):
							ignoredFiles.write("File " + targetFile + " already exists but its size is different - looks partially written (" + str(os.path.getsize(targetFile)) + " in destination, extracted as " + str(os.path.getsize(fullFile)) + " on disk)\n")
							
						print ("Skipping " + targetFile + " as file exists...")
					else:
						print ("Moving " + fullFile + " to " + targetFile)
						shutil.move(fullFile, targetFile)
				else:
					print ("No tag " + exifParameter)
		else:
			print ("Can't find zip file: " + zipFile)
		