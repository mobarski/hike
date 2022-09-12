from setuptools import setup

import hike

setup(
	name='hike',
	version=hike.__version__,    
	description='Hike is a library for automatically generating command line interfaces (CLIs) from Python scripts allowing selection and reordering of steps to run.',
	url='https://github.com/mobarski/hike',
	author='Maciej Obarski',
	author_email='mobarski@gmail.com',
	license='MIT',
	py_modules=['hike'],
	platforms='any',
)
