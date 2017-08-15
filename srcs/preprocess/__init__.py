"""Preprocess init, load utils dependencies."""
import os
import sys


# Load utils source folder into path
nb_dir = os.path.join(os.path.split(os.getcwd())[0], 'utils')
if nb_dir not in sys.path:
    sys.path.append(nb_dir)
