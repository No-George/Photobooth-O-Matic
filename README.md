# Photobooth-O-Matic  

sony nex 6 photobooth 

Generates liveview from camera then takes 4 pictures and renders them within a frame upon a bitton press  

I created my photobooth for my wedding in Mar15, this is my first python project so the code is pretty cowboy but it works at the moment  
Results can be viewed   
https://drive.google.com/open?id=0B__O93einHn9Z2xIXy1ZWWUxZXM   
  
To Use:  
1 update the save_directory in the script to one which exists (check your camera url too if not using nex6)  
2 edit the 'frame.png' so that it suits you 
3 turn on camera and run Smart Remote Control App  
4 connect computer to camera wifi host  
5 configure app to take pictures in 16:9 aspect ratio  
6 run script  
Press SPACE (I used an arduino keyboard with a big red button)  

Tested environments:  
Windows 7 Pro running Portable Python 2.7.6.1  


 
  
To Do:  
Add user prompts for things which can be configured     
Simplify the number of libraries required  
Ensure cross platform compatibility  
Run on a PI   
Introduce user prompts to   
......choose save location (once only with configuration file)  
......choose required functions eg. omit saving  
Take steps to make compatible with all nex devices   
......eg. Check api list and only call start rec mode where necessary, automatically find url/port  
Automatically set camera aspect, resolution, flash mode etc.  
Generate frame templates or automatically generate one from provided image and text  
Remove aliasing between frame and images  
Improve lag and frame rate of liveview if possible  
Add exception errors/recovery with suitable prompts  


thanks to ericklo for UCSD-E4E/qx100-interfacing which demonstrated many of the commands necessary to get this project going  
