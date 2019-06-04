# GF2-Software
## CUED IIA project - Logic simulator

### Getting Started

To install, run the following sequence of commands in your terminal
```
git clone https://github.com/rsewell97/GF2-Software/
cd GF2-Software/
```
If using computers in the DPO, you must run the command
```
export PATH=/usr/local/apps/anaconda3-5.0.1/bin:$PATH
```
to initialise the desktop environment. Else, to install dependencies manually, run

```
pip3 install -r requirements.txt
```
To run on Linux and MacOSX:
```
./main.py
```
Or for Windows:
```
python3 main_project.py
```
And you will see the graphical user interface of the logic simulator

Currently, both English and French languages are supported. The current language can either automatically detected or specified when the program is run, for example:
```
LANG=fr_FR.utf-8 ./main.py
```
or
```
LANG=fr_FR.utf-8 python3 main.py
```
### Other Help

Help operating the GUI can be found by clicking the 'Help' button in the top right-hand corner of the screen at any point.


### Running unit tests

Run the following commands in your terminal
```
python -m pytest pytests
```


