# sem-np-counter
GUI for measuring the size of nanoparticles from SEM images.

Program can be downloaded from <a href="https://www.dropbox.com/s/9801947k5b12l8h/gui_code.zip?dl=0">here</a>.

Overview:
1.	Load an SEM .tif file of some nanoparticles
2.	Calibration is carried out automatically if metadata is present, if there is no metadata then you just need to input the scalebar value and the program will finish the calibration automatically.
3.	Measurements can then be made automatically. You can finetune by changing filters, size limits, and removing bad particle suggestions.
4.	Particles can also be manually recorded by clicking their outline (note that you can zoom into an image using the scroll wheel)
5.	After identifying all shapes in an image, categorise them as hexagons or rods and then save these measurements to two separate .csv files.
6.	You can then move onto the next image in the folder to continue your measurements.

See video for more details.

[![Watch the video](https://github.com/grlewis333/sem-np-counter/blob/main/initial_pic.png?raw=true)](https://user-images.githubusercontent.com/30181254/110630828-c59a3b80-819d-11eb-8f7b-233b8a692fcf.mp4)

