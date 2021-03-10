from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import QObject# GUI functions
import sys                                                                                    # For interacting with computer OS
from os import walk                                                                           # To get filepaths automatically
import numpy as np                                                                            # Maths
import matplotlib.pyplot as plt                                                               # Plotting
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas              # 'Canvas' widget for inserting pyplot into pyqt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar      # Toolbar widget to accompany pyplot figure
import gui_counting_functions as cf                                                               # Custom functions for shape this program
import types # for scroll
import csv # for saving
import time # for notifying
from datetime import datetime

# Set fake Windows App ID to trick taskbar into displaying icon
import ctypes
myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# set image background colour to match grey of GUI
plt.rcParams.update({"figure.facecolor": '#f0f0f0'})

# def zoom_factory(self,ax,base_scale = .8):
#     """ Allow zooming with the scroll wheel on pyplot figures 
#         Pass figure axes and a scrolling scale. 
        
#         Based on https://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel """
#     def zoom_fun(event):
#         # get the current x and y limits
#         cur_xlim = ax.get_xlim()
#         cur_ylim = ax.get_ylim()
#         cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
#         cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
#         xdata = event.xdata # get event x location
#         ydata = event.ydata # get event y location
        
#         if event.button == 'up':
#             # deal with zoom in
#             scale_factor = 1/base_scale
#         elif event.button == 'down':
#             # deal with zoom out
#             scale_factor = base_scale
            
#         # set new limits
#         # zoom such that the cursor stays in the same position
#         ax.figure.canvas.toolbar.push_current() # Ensure toolbar home stays the same
#         ax.set_xlim([xdata - (xdata-cur_xlim[0]) / scale_factor, xdata + (cur_xlim[1]-xdata) / scale_factor]) 
#         ax.set_ylim([ydata - (ydata-cur_ylim[0]) / scale_factor, ydata + (cur_ylim[1]-ydata) / scale_factor])

#         self.canvas.draw()  # force re-draw

#     fig = ax.get_figure() # get the figure of interest
#     # attach the call back
#     self.canvas.mpl_connect('scroll_event',zoom_fun) #QWheelEvent

#     #return the function
#     return zoom_fun

def zoom_factory(self,ax,base_scale=60):
    """ Allow zooming with the scroll wheel on pyplot figures 
         Pass figure axes and a scrolling scale. 
         Based on https://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel """
    
    def mousewheel_move( event):
        ax=event.inaxes
        ax._pan_start = types.SimpleNamespace(
                lim=ax.viewLim.frozen(),
                trans=ax.transData.frozen(),
                trans_inverse=ax.transData.inverted().frozen(),
                bbox=ax.bbox.frozen(),
                x=event.x,
                y=event.y)
        ax.figure.canvas.toolbar.push_current() # Ensure toolbar home stays the same
        
        # Note using ax.drag_pan is much faster than resetting axis limits
        if event.button == 'up':
            ax.drag_pan(3, event.key, event.x+base_scale, event.y+base_scale)
        else: #event.button == 'down':
            ax.drag_pan(3, event.key, event.x-base_scale, event.y-base_scale)
        fig=ax.get_figure()
        fig.canvas.draw_idle()
    
    fig = ax.get_figure()
    fig.canvas.mpl_connect('scroll_event',mousewheel_move)
    
    return mousewheel_move
        
class Ui(QtWidgets.QMainWindow):
    """ User interface class """
    def __init__(self):
        """ Initialise attributes of the GUI """
        # Load GUI layout for QT designer .ui file
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('gui_draft_2.ui', self) # Load the .ui file from QT Designer
        
        # Set logo
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        
        # Create figure widget
        self.figure = plt.figure(figsize=(20,20)) 
        self.canvas = FigureCanvas(self.figure) # pass figure into canvas widget
        self.toolbar = NavigationToolbar(self.canvas, self) # add toolbar to canvas widget
   
        # Add figure widget into the GUI
        layout = self.verticalLayout_plotwindow # connect to the plot layout
        layout.addWidget(self.toolbar) # add toolbar to the layout 
        layout.addWidget(self.canvas) # add canvas to the layout 
        
        # Plot initial figure
        im = plt.imread('initial_pic.png')
        self.ax = self.figure.add_subplot(111)
        self.ax.imshow(im)
        self.plot()
            
        # Connect buttons to functions
        self.pushButton_fileinput.clicked.connect(self.file_input)
        self.pushButton_nextimage.clicked.connect(self.plot) 
        self.pushButton_updatescalenm.clicked.connect(self.update_calibration)
        self.pushButton_autoidentify.clicked.connect(self.auto_identify)
        self.pushButton_updateshapes.clicked.connect(self.remove_shape_row)
        self.pushButton_manualidentify.clicked.connect(self.manualidentify)
        self.checkBox_shapetoggle.toggled.connect(self.toggle_shapes)
        self.pushButton_outputfile.clicked.connect(self.file_output)
        self.pushButton_addtofile.clicked.connect(self.add_to_file)
        self.pushButton_nextimage.clicked.connect(self.next_im)
        self.pushButton_previousimage.clicked.connect(self.previous_im)
        self.pushButton_previousimage.clicked.connect(self.previous_im)
        self.checkBox_selectall.toggled.connect(self.select_all)
        
        # Initialise shapes
        self.shapes = []
        
    def file_input(self,fpath=False):
        """ Connects to file input button
        Opens file explorer for user to select image then plots it """
        
        try:
            self.label_statusbar.setText(r'Status: Opening image')
            if fpath == False:
                # Get filepath from file explorer
                self.fpath, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', '*.tif')

            else:
                self.fpath = fpath
            self.label_inputname.setText(self.fpath)

            # Clear current figure and plot selected image
            self.figure.clear() # clear old figure
            self.ax = self.figure.add_subplot(111) # create an axis
            self.im,self.raw_im,self.px,self.w,self.h = cf.read_tif(self.fpath) # load image
            self.ax.imshow(self.raw_im,cmap='Greys_r') # add image to axis
            self.plot() # plot axis

            # prompt user input if metadata is not present
            if np.isnan(self.px):
                self.lineEdit_scalenm.setEnabled(True)
                self.pushButton_updatescalenm.setEnabled(True)
                self.label_pxwidth.setText('Pixel width: Metadata not found')
                self.label_imdim.setText('Image dimensions: Metadata not found')
                self.label_statusbar.setText(r'Status: Metadata not found. Please enter the scalebar size in nm.')

            else:
                # Update labels
                self.lineEdit_scalenm.setEnabled(False)
                self.lineEdit_scalenm.setText(' ')
                self.pushButton_updatescalenm.setEnabled(False)
                self.label_pxwidth.setText('Pixel width: %.3f px per nm' % (self.px*1e9))
                self.label_imdim.setText('Image dimensions: %i nm x %i nm' % (self.w*1e9,self.h*1e9))
                self.label_statusbar.setText(r'Status: Idle')
        except:
            self.label_statusbar.setText(r'Status: Error')
    
    def plot(self):
        """ Plots the image that is currently assigned to self.ax 
        Image will be added to interactive canvas with scrollwheel zoom enabled """
        # image settings
        self.ax.axis('off')
        plt.tight_layout()
        
        # Plot with zoom functionality
        f = zoom_factory(self,self.ax)
        
        # refresh canvas 
        self.canvas.draw()
        
    def update_calibration(self):
        """ Runs automatic calibration based on scalebar size input by user """
        try:
            # Get user value
            scale_bar_val = int(self.lineEdit_scalenm.text())

            # Run calibration
            self.im,self.raw_im,self.px,self.w,self.h = cf.alternate_calibration(self.fpath,scale_bar_val = scale_bar_val)

            # Update labels
            self.label_pxwidth.setText('Pixel width: %.3f px per nm' % (self.px*1e9))
            self.label_imdim.setText('Image dimensions: %i nm x %i nm' % (self.w*1e9,self.h*1e9))
            self.label_statusbar.setText(r'Status: Idle')
        except:
            self.label_statusbar.setText(r'Status: Error')
        
    def auto_identify(self):
        """ Check auto identification settings and run searching algorithms """
        try:
            self.label_statusbar.setText(r'Status: Analysing image')
            self.label_statusbar.repaint() # force status to update

            # Check settings
            filters = []
            if self.checkBox_f1.isChecked():
                filters.append('blur_fill')
            if self.checkBox_f2.isChecked():
                filters.append('sobel')
            minsize = self.spinBox_minsize.value()
            maxsize = self.spinBox_maxsize.value()

            # Prepare for new image

            # Extract shapes and plot new images
            ds,errs,shapes = cf.full_count_process(self.im,self.raw_im,self.px,self.w,self.h, self.ax, filters=filters, min_avg_length = minsize, max_avg_length = maxsize)


            # Add shapes to current shapes bar
            # ONLY IF NOT THE SAME AS EXISTING
            self.shapes = np.concatenate((self.shapes,shapes))
            self.shapes = cf.remove_identical_shapes(self.shapes,threshold=.3)
            self.figure.clear() # clear old figure
            self.ax = self.figure.add_subplot(111) # create an axis
            # Fit circles to shapes and plot
            cents,rads = cf.fit_circles(self.shapes)
            ds = np.array(cf.calibrate_radii(rads,self.px))
            cf.plot_circles(self.im,self.ax,self.raw_im,self.shapes,cents,rads,ds)
            self.plot()

            # Remove all rows
            layout = self.gridLayout_13
            cs = self.scrollAreaWidgetContents.children()
            for i,w in enumerate(cs):
                if i > 4:
                    layout.removeWidget(w)
                    w.deleteLater()
                    w = None

            # Add rows for shapes still there
            for i,s in enumerate(self.shapes):
                self.add_shape_row(i)

            # Toggle shape view on
            self.checkBox_shapetoggle.setChecked(True)

            self.label_statusbar.setText(r'Status: Idle')
        
        except:
            self.label_statusbar.setText(r'Status: Error')
        
    def add_shapes(self,shapes):
        """ Adds all shapes to current shapes bar"""
        current_shapes = len(self.shapes)
        for i,s in enumerate(shapes):
            self.add_shape_row(current_shapes+i)
            
    def add_shape_row(self,i):
        """ Adds a new shape at label i"""
        layout = self.gridLayout_13
            
        nlabel = QtWidgets.QLabel('%i' % i)
        bg = QtWidgets.QButtonGroup(self)
        hexbox = QtWidgets.QRadioButton('')
        hexbox.setChecked(True)
        rodbox = QtWidgets.QRadioButton('')
        bg.addButton(hexbox)
        bg.addButton(rodbox)
        #self.b1.toggled.connect(lambda:self.btnstate(self.b1))
        #self.b2.toggled.connect(lambda:self.btnstate(self.b2))
        
        self.includebox = QtWidgets.QCheckBox('')
        self.includebox.setChecked(True)
            
        layout.addWidget(nlabel)
        layout.addWidget(hexbox)
        layout.addWidget(rodbox)
        layout.addWidget(self.includebox)
        
        
    def remove_shape_row(self):
        """ Removes any shapes with 'Keep?' unchecked """
        
        try:
            layout = self.gridLayout_13
            cs = self.scrollAreaWidgetContents.children()
            # 8 is position of first keep checkbox
            # they repeat every 4 items
            keeps = cs[8::4] 
            to_delete = []
            for i,box in enumerate(keeps):
                if box.checkState() == 0: # if box is unchecked
                    # Remove from shapes list
                    to_delete.append(i)

            if len(self.shapes) > 0:
                self.shapes = np.delete(self.shapes,to_delete,axis=0)

            # Remove all rows
            cs = self.scrollAreaWidgetContents.children()
            for i,w in enumerate(cs):
                if i > 4:
                    layout.removeWidget(w)
                    w.deleteLater()
                    w = None

            # Add rows for shapes still there
            for i,s in enumerate(self.shapes):
                self.add_shape_row(i)

            self.checkBox_shapetoggle.setChecked(True)

            # plot with shapes
            self.figure.clear() # clear old figure
            self.ax = self.figure.add_subplot(111) # create an axis
            # Fit circles to shapes and plot

    #         self.shapes = self.shapes.tolist()
    #         self.shapes = np.array(self.shapes)
            cents,rads = cf.fit_circles(self.shapes)
            ds = np.array(cf.calibrate_radii(rads,self.px))
            cf.plot_circles(self.im,self.ax,self.raw_im,self.shapes,cents,rads,ds)
            self.plot() # plot axis

            self.checkBox_selectall.setChecked(True)
        
        except:
            self.label_statusbar.setText(r'Status: Error')
        
    def toggle_shapes(self):
        """ Switch between showing/not showing shape outlines over image """
        try:
            if self.checkBox_shapetoggle.isChecked():
                # plot with shapes
                self.figure.clear() # clear old figure
                self.ax = self.figure.add_subplot(111) # create an axis
                # Fit circles to shapes and plot
                cents,rads = cf.fit_circles(self.shapes)
                ds = np.array(cf.calibrate_radii(rads,self.px))
                cf.plot_circles(self.im,self.ax,self.raw_im,self.shapes,cents,rads,ds)
                self.plot() # plot axis


            if self.checkBox_shapetoggle.isChecked() == False:
                # plot without shapes
                self.figure.clear() # clear old figure
                self.ax = self.figure.add_subplot(111) # create an axis
                self.ax.imshow(self.raw_im,cmap='Greys_r') # add image to axis
                self.plot() # plot axis
        except:
            self.label_statusbar.setText(r'Status: Error')
            
    def manualidentify(self):
        try:
            self.label_statusbar.setText(r'Status: Add points manually')
            self.figure.clear() # clear old figure
            self.ax = self.figure.add_subplot(111) # create an axis
            self.ax.imshow(self.raw_im,cmap='Greys_r') # add image to axis
            cf.plot_shapes(self.shapes,self.raw_im,self.ax,cols=['dodgerblue'])
            self.plot()

            # Get new shapes from user input
            new_s = cf.manual_detection(self.raw_im)

            # add to existing shapes
            self.shapes = np.concatenate((self.shapes,new_s))

            #remove identical shapes
            self.shapes = cf.remove_identical_shapes(self.shapes,threshold=.3)

            #plot
            self.figure.clear() # clear old figure
            self.ax = self.figure.add_subplot(111) # create an axis
            # Fit circles to shapes and plot
            cents,rads = cf.fit_circles(self.shapes)
            ds = np.array(cf.calibrate_radii(rads,self.px))
            cf.plot_circles(self.im,self.ax,self.raw_im,self.shapes,cents,rads,ds)
            self.plot()

            # Adjust rows
            layout = self.gridLayout_13
            cs = self.scrollAreaWidgetContents.children()
            for i,w in enumerate(cs):
                if i > 4:
                    layout.removeWidget(w)
                    w.deleteLater()
                    w = None
            # Add rows for shapes still there
            for i,s in enumerate(self.shapes):
                self.add_shape_row(i)

            # Toggle shape view on
            self.checkBox_shapetoggle.setChecked(True)

            self.label_statusbar.setText(r'Status: Idle')  
        except:
            
            self.label_statusbar.setText(r'Status: Error')
        
    def file_output(self):
        """ Connects to file input button
        Opens file explorer for user to select image then plots it """
        try:
            self.label_statusbar.setText(r'Status: Choosing output file')

            # Get filepath from file explorer
            files_types = "CSV (*.csv)"
            default_name = datetime.today().strftime('%Y-%m-%d') + '.csv'
            self.fpath_out, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Choose output filepath', default_name, filter = files_types, options=QtWidgets.QFileDialog.DontConfirmOverwrite)


            # Get selected folder
            fpath = self.fpath_out
            split = fpath.split(sep='/')
            folder = ''
            for i in split[:-1]:
                folder += i + '/'

            _, _, fnames = next(walk(folder))


            if split[-1] in fnames:
                # file already exists
                name = split[-1].split(sep='.')[0]
                try:
                    name.split(sep='_HEX')[1]
                    name = name.split(sep='_HEX')[0]
                except:
                    name.split(sep='_ROD')[1]
                    name = name.split(sep='_ROD')[0]
                self.fpath_hex = folder+name+'_HEX.csv'
                self.fpath_rod = folder+name+'_ROD.csv'

            else:
                # create file
                name = split[-1].split(sep='.')[0] # name without suffix
                self.fpath_hex = folder+name+'_HEX.csv'
                self.fpath_rod = folder+name+'_ROD.csv'
                with open(self.fpath_hex, 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',',
                                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow(['Size (hex) / nm'] + ['fpath'])

                with open(self.fpath_rod, 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',',
                                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow(['Size (rod) / nm'] + ['Filepath'])

            self.label_output_path.setText(folder+name+'_XXX.csv')
            self.label_statusbar.setText(r'Status: Idle')
        
        except:
            self.label_statusbar.setText(r'Status: Choosing output file')

            # Get filepath from file explorer
            files_types = "CSV (*.csv)"
            default_name = datetime.today().strftime('%Y-%m-%d') + '.csv'
            self.fpath_out, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Choose output filepath', default_name, filter = files_types, options=QtWidgets.QFileDialog.DontConfirmOverwrite)


            # Get selected folder
            fpath = self.fpath_out
            split = fpath.split(sep='/')
            folder = ''
            for i in split[:-1]:
                folder += i + '/'

            _, _, fnames = next(walk(folder))


            if split[-1] in fnames:
                # file already exists
                name = split[-1].split(sep='.')[0]
                try:
                    name.split(sep='_HEX')[1]
                    name = name.split(sep='_HEX')[0]
                except:
                    name.split(sep='_ROD')[1]
                    name = name.split(sep='_ROD')[0]
                self.fpath_hex = folder+name+'_HEX.csv'
                self.fpath_rod = folder+name+'_ROD.csv'

            else:
                # create file
                name = split[-1].split(sep='.')[0] # name without suffix
                self.fpath_hex = folder+name+'_HEX.csv'
                self.fpath_rod = folder+name+'_ROD.csv'
                with open(self.fpath_hex, 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',',
                                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow(['Size (hex) / nm'] + ['fpath'])

                with open(self.fpath_rod, 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',',
                                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow(['Size (rod) / nm'] + ['Filepath'])

            self.label_output_path.setText(folder+name+'_XXX.csv')
            self.label_statusbar.setText(r'Status: Idle')
            self.label_statusbar.setText(r'Status: Error')
        
    def add_to_file(self):
        # Need to define ds globally and have it update like shapes does.
        # then need to check whether hexagon or rod - swap to radio
        # then write to file
        # then add some hover text
        # then add some try/except statements to prevent crashing
        # then load into app!
        try:
            self.label_statusbar.setText(r'Status: Saving')
            self.label_statusbar.repaint() # force status to update
            cents,rads = cf.fit_circles(self.shapes)
            ds = np.array(cf.calibrate_radii(rads,self.px))

            cs = self.scrollAreaWidgetContents.children()
            hex_boxs = cs[6::4]
            hexs = []
            for i,w in enumerate(hex_boxs):
                if w.isChecked() == True:
                    hexs.append(1)
                else:
                    hexs.append(0)

            with open(self.fpath_hex, 'a', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='"', quoting=csv.QUOTE_MINIMAL)


                for i,d in enumerate(ds):
                    if hexs[i] == 1:
                        spamwriter.writerow(['%.2f' % d] + [self.fpath])

            with open(self.fpath_rod, 'a', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='"', quoting=csv.QUOTE_MINIMAL)

                for i,d in enumerate(ds):
                    if hexs[i] != 1:
                        spamwriter.writerow(['%.2f' % d] + [self.fpath])

            time.sleep(3) # Wait so that user sees saving status
            self.label_statusbar.setText(r'Status: Idle')
            
        except:
            self.label_statusbar.setText(r'Status: Error')
        
        
    def next_im(self):
        """ open next tif in folder """
        # get current folder and filename
        try:
            fpath = self.fpath
            split = fpath.split(sep='/')
            folder = ''
            for i in split[:-1]:
                folder += i + '/'
            current_name = split[-1]

            # get files in folder
            _, _, fnames = next(walk(folder))
            all_tifs = []
            tif = ['tif','TIF','tiff','TIFF']

            # find tifs in folder and position of current file
            i=0
            for f in fnames:
                ext = f.split(sep='.')[-1]
                if ext  in tif:
                    all_tifs.append(f)
                    if f == current_name:
                        current_i = i
                    i += 1

            # select next folder
            ind = current_i+1
            if ind == len(all_tifs):
                ind = 0 # loop back to start
            fpath = folder + all_tifs[ind]

            self.file_input(fpath=fpath)
        except:
                self.label_statusbar.setText(r'Status: Error')

    def previous_im(self):
        """ open previous tif in folder """
        try:
            fpath = self.fpath
            split = fpath.split(sep='/')
            folder = ''
            for i in split[:-1]:
                folder += i + '/'
            current_name = split[-1]
            _, _, fnames = next(walk(folder))
            all_tifs = []
            tif = ['tif','TIF','tiff','TIFF']
            i=0
            for f in fnames:
                ext = f.split(sep='.')[-1]
                if ext  in tif:
                    all_tifs.append(f)
                    if f == current_name:
                        current_i = i
                    i += 1


            ind = current_i-1
            fpath = folder + all_tifs[ind]

            self.file_input(fpath=fpath)
        except:
            self.label_statusbar.setText(r'Status: Error')
        
    def select_all(self):
        try:
            if self.checkBox_selectall.isChecked():
                cs = self.scrollAreaWidgetContents.children()
                keep_boxs = cs[8::4]
                for i,w in enumerate(keep_boxs):
                    w.setChecked(True)

            if self.checkBox_selectall.isChecked() == False:
                cs = self.scrollAreaWidgetContents.children()
                keep_boxs = cs[8::4]
                for i,w in enumerate(keep_boxs):
                    w.setChecked(False)
        except:
            self.label_statusbar.setText(r'Status: Error')

# Launch GUI

app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = Ui() # Create an instance of our class

# Show in fullscreen
window.resize(800,800) # workaround for FS
window.showMaximized()

app.exec_() # Start the application