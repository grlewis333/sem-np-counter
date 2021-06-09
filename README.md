# sem-np-counter
GUI for measuring the size of nanoparticles from SEM images.

Program can be downloaded from <a href="https://www.dropbox.com/s/ld9us31h61hyct1/gui_code-0_1_2.zip?dl=0">here</a>. (Extract zipped contents and then run the gui_code.exe file).

Overview:
1.	Load an SEM .tif file of some nanoparticles
2.	Calibration is carried out automatically if metadata is present, if there is no metadata then you just need to input the scalebar value and the program will finish the calibration automatically.
3.	Measurements can then be made automatically. You can finetune by changing filters, size limits, and removing bad particle suggestions.
4.	Particles can also be manually recorded by clicking their outline (note that you can zoom into an image using the scroll wheel)
5.	After identifying all shapes in an image, categorise them as hexagons or rods and then save these measurements to two separate .csv files.
6.	You can then move onto the next image in the folder to continue your measurements.

See <a href='https://user-images.githubusercontent.com/30181254/110630828-c59a3b80-819d-11eb-8f7b-233b8a692fcf.mp4'>video</a> for more details.

<img src='https://github.com/grlewis333/sem-np-counter/blob/main/initial_pic.png' width=400>

If you want to work directly from the terminal:
1. Create a fresh conda environment 'conda create -n counting_env'
2. Activate the environment 'conda activate counting_env'
3. Install necessary modules 'conda install -c defaults -c conda-forge -c anaconda opencv matplotlib numpy tifffile pyqt'
4. (If you would like to be able to use the jupyter notebook for demonstration, you should follow this up with 'conda install -c conda-forge jupyterlab')
5. Navigate to the directory where you downloaded the code 'cd path-to-download\sem-np-counter-main'
6. Run the program from here 'python gui_code.py'

If you want to build your own .exe from the code here directly:
1. Install pyinstaller 'conda install -c conda-forge pyinstaller'
2. Navigate to the repo directory from the command prompt
3. Run: 'pyinstaller --onedir --add-data="gui_draft_2.ui;." --add-data="logo.png;." --add-data="initial_pic.png;." gui_code.py'
