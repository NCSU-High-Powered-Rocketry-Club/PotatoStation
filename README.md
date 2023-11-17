# Potato-Station Ground Control System

This is the repository for the PotatoStation ground control software, which is a multi-purpose
ground control GUI slash control system for a variety of payloads for the NASA Student Launch Challenge.

## Setting Up Your Python Venv

> Note: These commands are for Linux, on Windows simply ensure you have python installed and in your system path. 
> Skip any apt install commands and run python and pip commands without the 3.

The first thing you should do prior to running your code is set up your virtual environment. To do this, open you your terminal and make sure you are in the `Potato-Station` directory. Inside of that directory call the commands

(Install pip3)
```bash
sudo apt install python3-pip
```

(Install venv)
```bash
sudo apt install python3-venv
```

(Make venv)
```bash
python3 -m venv env
```

to set up your virtual environment in a folder called env. Next you need to set this folder as your interpreter (your IDE might prompt you to do this automatically. If it did not prompt you, to do this in VS Code, press `ctrl+shift+p` to open your command prompt and type in `Python: Select Interpreter`. Press enter and select the one that ends in something like `('env':venv)`).

## Installing Required Packages

In order to install the required packages, open a new terminal in VS Code by pressing ```ctrl+shift+` ```. This terminal will already be in your virtual environment, and simply run the command

```bash
pip3 install -r requirements.txt
```

## Running the Program

Now that you have all the required packages installed, you can run the program by running the command

```bash
python3 main.py
```

or with arguments

```bash
python3 main.py <arguments>
```

The arguments will vary depending on what payload and functionality is needed.