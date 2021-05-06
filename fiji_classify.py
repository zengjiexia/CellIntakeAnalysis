#@String datapath
#@String resultpath

from __future__ import with_statement
import os
from ij import IJ
from ij import WindowManager as wm
import ij.io.FileSaver as FileSaver
from trainableSegmentation import WekaSegmentation, Weka_Segmentation
import trainableSegmentation.utils.Utils as Utils


if __name__ == "__main__":

    def file_organizer(path):
        paths =[]
        for r,d,f in os.walk(path):
            for file in f:
                filepath = os.path.join(r, file)
                if '_WL' in filepath:
                    paths.append(filepath)
                else:
                    pass
        return paths
    

    paths = file_organizer(datapath)
    weka = WekaSegmentation()
    weka.loadClassifier(os.path.dirname(os.path.abspath(__file__)) + '/classifier_20201204.model')
        
    for path in paths:
        fov_name = os.path.basename(path)[:10]
        img = IJ.openImage(path.replace('\\', '/'))
        result = weka.applyClassifier(img, 0, True)
        result.setLut(Utils.getGoldenAngleLUT())
        FileSaver(result).saveAsTiff(resultpath +'/'+ fov_name + '.tif')
        
    IJ.run("Quit")
    


