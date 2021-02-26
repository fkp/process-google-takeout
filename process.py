import sys, os, argparse, re
from zipfile import ZipFile

fileNameMatches = [ re.compile('.*IMG_(\d\d\d\d)(\d\d)(\d\d)_\d\d\d\d\d\d.*'), re.compile('.*IMG-(\d\d\d\d)(\d\d)(\d\d)-WA\d\d\d\d.*'), re.compile('.*VID-(\d\d\d\d)(\d\d)(\d\d)-WA\d\d\d\d.*'), re.compile('.*VID_(\d\d\d\d)(\d\d)(\d\d)_\d\d\d\d\d\d.*')]

def DeriveDirectoryName(fileName):

	for fileNameMatch in fileNameMatches:
		
		matches = fileNameMatch.match(fileName)
		
		if matches:
			return True, f"{matches.group(1)}\{matches.group(1)}-{matches.group(2)}"
	
	return False,''

parser = argparse.ArgumentParser(description='A script to extract Google Take out information')

parser.add_argument("destinationDirectory", help="The destination directory to output to")
parser.add_argument("sourceZipFiles", nargs='+', help="The Google Takeout zip files to extract from")
parser.add_argument("--extensions", default='', help="The file extension(s) to extract from the zip file - e.g. '.jpg;.jpeg;.png'")
args = parser.parse_args()

for zipFile in args.sourceZipFiles:

	skippedFilesExtension = 0
	skippedFilesRegEx = 0
	fileExtensions = args.extensions.split(';')
	
	with open("ignored.log", 'w', buffering=1) as ignoredFiles:
	
		if os.path.isfile(zipFile):
			print ("About to process zip file: " + zipFile)
			
			with ZipFile(zipFile,'r') as zipObj:
				listOfFileInfos = zipObj.infolist()
				
				for file in listOfFileInfos:
					if any(isinstance(s, str) and file.filename.lower().endswith(s.lower()) for s in fileExtensions):
					
						fileMatched, fileDestination = DeriveDirectoryName(file.filename)
						
						if fileMatched:
							sourceDirectory, sourcefilename = os.path.split(file.filename)
							
							print(os.path.join(args.destinationDirectory, fileDestination, sourcefilename))
							
							if (not(os.path.isdir(os.path.join(args.destinationDirectory, fileDestination)))):
								os.makedirs(os.path.join(args.destinationDirectory, fileDestination))
							
							writeTo = os.path.join(args.destinationDirectory, fileDestination, sourcefilename)
							
							if (os.path.isfile(writeTo)):
								if (not(file.file_size == os.path.getsize(writeTo))):
									raise Exception("File " + file.filename + " already exists but its size is different - looks partially written")
								else:
									print ("Skipping " + writeTo + " as file exists...")
							else:
								with open(writeTo, 'wb') as outFile:
									outFile.write(zipObj.read(file))
							
						else:
							ignoredFiles.write("Regex: " + file.filename + "\n")
							skippedFilesRegEx +1
						
					else:
						ignoredFiles.write("Extension: " + file.filename + "\n")
						skippedFilesExtension += 1
				
				
		else:
			print ("Can't find zip file: " + zipFile)
		
	print ("Skipped " + str(skippedFilesExtension) + " files on extension and " + str(skippedFilesRegEx) + " on failed filename parse")
	
	
	