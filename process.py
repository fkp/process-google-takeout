import sys, os, argparse, re
from zipfile import ZipFile

fileNameMatches = [ re.compile('.*IMG_(\d\d\d\d)(\d\d)(\d\d)_\d\d\d\d\d\d.*'), re.compile('.*IMG-(\d\d\d\d)(\d\d)(\d\d)-WA\d\d\d\d.*')]

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
	
	if os.path.isfile(zipFile):
		print ("About to process zip file: " + zipFile)
		
		with ZipFile(zipFile,'r') as zipObj:
			listOfFiles = zipObj.namelist()
			
			for file in listOfFiles:
				if any(isinstance(s, str) and file.lower().endswith(s.lower()) for s in fileExtensions):
				
					fileMatched, fileDestination = DeriveDirectoryName(file)
					
					if fileMatched:
						sourceDirectory, filename = os.path.split(file)
						
						print("File " + file + ", destination location: " + os.path.join(args.destinationDirectory, fileDestination, filename))
						
						if (not(os.path.isdir(os.path.join(args.destinationDirectory, fileDestination)))):
							os.makedirs(os.path.join(args.destinationDirectory, fileDestination))
						
						with open(os.path.join(args.destinationDirectory, fileDestination, filename), 'wb') as outFile:
							outFile.write(zipObj.read(file))
						
					else:
						skippedFilesRegEx +1
					
				else:
					skippedFilesExtension += 1
				
				
	else:
		print ("Can't find zip file: " + zipFile)
		
	print ("Skipped " + str(skippedFilesExtension) + " files on extension and " + str(skippedFilesRegEx) + " on failed filename parse")
	
	
	