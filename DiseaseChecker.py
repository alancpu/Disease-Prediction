from Utils.DiseaseUtil import DiseaseUtil
from Utils.UniprotUtil import UniprotUtil
from Utils.Alignment import Alignment
from Utils.HTMLWriter import HTMLWriter
from shutil import copyfile
import webbrowser
import os,os.path
import glob
import argparse
import sys

def main(argv):

	#begin argument parsing options
	parser = argparse.ArgumentParser(description='Analyze disease likelyhood in human DNA.')
	parser.add_argument('--clean', dest='clean', action='store_true', help="Clean the HTML output file for new diseases")
	parser.add_argument('--umls', dest='umls', action='store_true', help='Specify if searching using UMLS code')
	parser.add_argument('--disease-only', dest='diseaseOnly', default=False, action='store_true', help='Specify if wanting to only download the disease clean FASTA file, This option does no comparison')

	parser.set_defaults(clean=False)
	parser.set_defaults(umls=False)
	args = parser.parse_args()
	clean = args.clean

	disease_only = args.diseaseOnly


	#Option for cleaning up the HTML file for a new experience
	if clean:
		os.remove('HTML/clean.html')
		copyfile('HTML/doNotDelete.html', 'HTML/clean.html')
		print 'All cleaned up!'
		return


	search_disease = raw_input('Enter the name or umls of the disease: ')
	umls = args.umls
	if 'umls' in search_disease:
		umls = True

	diseaseU = DiseaseUtil(search_disease, umls=umls)
	uniprot = UniprotUtil(search_disease, umls=umls)
	align = Alignment()

	#check if the disease FASTA file already exist
	if not os.path.isfile('FASTA/%s.fasta' % diseaseU.getName()):
		uniprot.generateFasta()

	#break if the user only wants to download disease FASTA file
	if disease_only:
		print 'Disease file downloaded, location is the FASTA/ directory'
		return

	likelyhood = diseaseU.getScore()

	clean,dirty = getFastaFiles(diseaseU.getName())

	#case where program is unable to locate a file in the YOU/ directory to compare
	if clean == None or dirty == None:
		print "Unable to locate file in YOU/ directory ending..."
		return

	align_score = align.calculateMutationPercentage(clean,dirty)

	print 'Your likelyhood for devloping {0} is: \033[31m{1:.2f}\033[0m%'.format(diseaseU.getName(), round(likelyhood*align_score,2))

	writer = HTMLWriter()
	writer.writeTableOutput(diseaseU.getName(), str(round(likelyhood*align_score,2)) + '%')
	webbrowser.open('HTML/index.html', new=2)

#gets the two sequences from the FASTA folder (seq1) and the YOU folder (seq2)
def getFastaFiles(diseaseName):
	seq1 = open('FASTA/%s.fasta' % diseaseName)
	header = seq1.readline()
	seq1 = seq1.read().replace('\n','')

	if os.path.isfile('YOU/%s.fasta' % diseaseName):
		seq2 = open('YOU/%s.fasta' % diseaseName)
		seq2.readline()
		seq2 = seq2.read().replace('\n','')

	else:
		file = findFastaFile(header.split('|'))
		if file == None:
			return [None,None]
		file.readline()
		seq2 = file.read().replace('\n','')

	return [seq1, seq2]

#Checks to see if any of the identifiers in the first line of a file are the name of a file in the YOU/ directory
def findFastaFile(header):
	for file in glob.glob("YOU/*.fasta"):
		for section in header:
			if section in file:
				return open(file)
	return None

if __name__ == '__main__':main(sys.argv[1:])