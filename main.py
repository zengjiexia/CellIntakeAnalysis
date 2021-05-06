import subprocess
import os
import tifffile as tiff
from skimage import filters
import pandas as pd
import numpy as np



def ij_classify(fiji_path, data_path, result_path):
	code_path = os.path.dirname(os.path.abspath(__file__))

	try:
		subprocess.call([fiji_path, "--ij2", "--console", "--run", code_path + "\\fiji_classify.py", 'datapath=\''+data_path+'\','+'resultpath=\''+result_path+'\''])
		print('Calculation completed without error.')
	except FileNotFoundError:
		print('Fiji path is incorrect.')

def thresholder(img, threshold_control=800):
	threshold = filters.threshold_otsu(img)
	if threshold >= threshold_control:
		return threshold
	else:
		return threshold_control

def calc_intensity(sample_path, threshold_control=800):
	paths_635 = []
	paths_488 = []
	paths_mask = []
	sample_result = pd.DataFrame()
	for root, dirs, files in os.walk(sample_path):
		for f in files:
			if f.endswith('_635.tif'):
				paths_635.append(os.path.join(root, f))
			elif f.endswith('_488.tif'):
				paths_488.append(os.path.join(root, f))
			else:
				pass
	for root, dirs, files in os.walk(sample_path.replace(data_path, mask_path)):
		for f in files:
			if f.endswith('.tif'):
				paths_mask.append(os.path.join(root, f))
	paths_635 = sorted(paths_635)
	paths_488 = sorted(paths_488)
	paths_mask = sorted(paths_mask)

	for i in range(0, len(paths_mask)):
		mask = tiff.imread(paths_mask[i]).mean(axis=0)
		img_488 = tiff.imread(paths_488[i]).mean(axis=0)
		img_635 = tiff.imread(paths_635[i]).mean(axis=0)

		mask_rev = mask[1] < 0.67
		mask = mask[1] >= 0.67

		thred_488 = img_488 >= thresholder(img_488,threshold_control=threshold_control)
		thred_635 = img_635 >= thresholder(img_635,threshold_control=threshold_control)

		masked_488 = thred_488 * mask
		masked_635 = thred_635 * mask

		masked_488_rev = thred_488 * mask_rev
		masked_635_rev = thred_635 * mask_rev

		df = pd.DataFrame.from_dict({
			'sample': [os.path.basename(sample_path)],
			'FoV': [os.path.basename(paths_mask[i])[:10]],
			'cell area': [np.sum(mask)],
			'488 read': [masked_488.sum()],
			'488 per cell area': [masked_488.sum()/np.sum(mask)],
			'635 read': [masked_635.sum()],
			'635 per cell area': [masked_635.sum()/np.sum(mask)],
			'488 read(non-cell area)': [masked_488_rev.sum()],
			'488 per non-cell area': [masked_488_rev.sum()/np.sum(mask_rev)],
			'635 read(non-cell area)': [masked_635_rev.sum()],
			'635 per non-cell area': [masked_635_rev.sum()/np.sum(mask_rev)]
			})
		sample_result = pd.concat([sample_result, df])

	sample_result = sample_result.fillna(0)
	return sample_result


if __name__ == "__main__":
	data_path = r"" # parameter

	fiji_path = r"D:\Fiji.app\ImageJ-win64.exe" # parameter
	result_path = data_path +'_result'

	if os.path.isdir(result_path) != True:
		os.mkdir(result_path)

	# generate masks
	mask_path = result_path +'/' + os.path.basename(data_path) + "_mask"
	if os.path.isdir(mask_path) != True:
		os.mkdir(mask_path)
		well_paths = [f.path for f in os.scandir(data_path) if f.is_dir()]
		for well_path in well_paths:
			well_result = well_path.replace(data_path, mask_path)
			if os.path.isdir(well_result) != True:
				os.mkdir(well_result)
			print('Masking ' + os.path.basename(well_result))
			ij_classify(fiji_path, well_path, well_result)
	else:
		print('Masks already generated. Skipping this process.')
		pass

	# get intensities
	results = pd.DataFrame()
	sample_paths = [f.path for f in os.scandir(data_path) if f.is_dir()]
	for sample_path in sample_paths:
		print('Calculating '+ sample_path)
		dff = sample_result = calc_intensity(sample_path)
		results = pd.concat([results, dff])
	results.to_csv(result_path + '/summary.csv')
