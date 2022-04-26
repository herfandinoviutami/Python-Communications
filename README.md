# Readme file
These codes shows how to generate a signal and upload them to the Arbitrary Wave Generator.

## Files
The files included in this repository are:
- **interference.ipynb** (Notebook): It shows how to generate a sinusoid signal and a square signal with different phases and frequencies for two awg channels.
- **manchester_encoding.ipynb** (Notebook): It shows how to generate a manchester encoded signal.
- **T3AWG3252.py** (Python code): contains the class T3AWG3252 for controlling the Teledyne arbitrary wave generator
- **requirements.txt**: contains the required python modules.
## Installation steps (Windows)
-------------------------------------------------------------------------------------------
The steps for the installation in Windows are:

1) Download your preferred Python version and install it for all the users.
2) Open a console terminal and check the python installed version by typing in the terminal

```python --version```

3) Install the virtual environment manager using this python.

```python -m pip install virtualenv```

4) Go to your project folder and create a virtual environment.

```python -m virtualenv .env```

This command will create a virtual enviroment in the folder .env

5) Activate the virtual enviroment.

```.\.env\Scripts\activate```

6) You can later deactivate your enviroment by using.

```deactivate```

7) Install required python modules

```python -m pip install -r requirements.txt```

8) You can install more modules using the following command.

```python -m pip install <module_name>```

9) Install jupyter lab

```python -m pip install jupyterlab```

10) Launch jupyter lab server

```python -m jupyter lab --port <port>```

11) To save new installed modules you can use the following command.

```python -m pip freeze > requirements.txt```

12) Launch the browser (if it was not launched) and start having fun coding!