#@String datapath
#@String resultpath
from __future__ import with_statement
import os
from ij import IJ
from ij import WindowManager as wm

def fiji_avg(source_path, result_path):
	img = IJ.open(source_path)
	IJ.run(img, "Z Project...", "projection=[Average Intensity]")
	IJ.saveAs('tiff', result_path)

def extract_filepaths(path):
	"""
	walk through a directory and put names of all tiff files into an ordered list
	para: path - string
	return: filenames - list of string (remove the extension name)
	"""

	paths = []
	for root, dirs, files in os.walk(path):
		for f in files:
			if f.endswith('.tif'):
				filepath = os.path.join(root, f)
				paths.append(filepath)
	return paths

if __name__ == '__main__':

	paths = extract_filepaths(datapath)
	for path in paths:
		result_path = resultpath +'/'+ os.path.basename(path)
		fiji_avg(path, result_path)

	IJ.run("Quit")
