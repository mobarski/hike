__author__ = 'Maciej Obarski'
__version__ = '0.1'
__license__ = 'MIT'

import re
import time
import sys
import os

USAGE = f"""USAGE: {sys.argv[0]} [task1:[:steps]] [task2[:steps]] ...

steps - comma separated list of step identifiers; leave empty to select
        all the steps; use dash to specify ranges; example: 10,20,30-40,99

"""

# =============================================================================

def get_file_parts(path, n=10, header=True):
	parts = []
	with open(path) as f:
		head = f.readline() if header else None
		pos_after_head = f.tell()
		f.seek(0,2) # EOF
		pos_of_eof = f.tell()
		size = pos_of_eof - pos_after_head
		#
		f.seek(pos_after_head, 0)
		for i in range(n):
			a = f.tell()
			f.seek(pos_after_head + (i+1)*size//n, 0)
			f.readline()
			b = f.tell()
			parts += [(i, a, b, b-a)] # TODO: dict?
	return {'parts':parts, 'header':head}

# =============================================================================

def _get_jobs(depth=1): # -> dict[str, list[function]]
	out = {}
	sf = sys._getframe(depth)
	env = sf.f_globals
	for x in env:
		match = re.findall('(.+?)_step(\d+)(.?)',x)
		if match:
			job = match[0][0]
			if job not in out: out[job] = []
			out[job] += [env[x]]
	return out


def _filter_steps(fun_list, args):
	# TODO: m[0][2] handling (step version)
	# TODO: refactor
	if args is None: return fun_list
	out = []
	for a in args:
		if type(a) is int:
			for f in fun_list:
				m = re.findall('(.+?)_step(\d+)(.?)', f.__name__)
				if m:
					if m[0][1]==str(a):
						out += [f]
		if type(a) is tuple:
			lo = a[0]
			hi = a[1]
			for f in fun_list:
				m = re.findall('(.+?)_step(\d+)(.?)', f.__name__)
				if m:
					if lo <= int(m[0][1]) <=hi:
						out += [f]
	return out


def _parse_steps(text):
	if not text: return None
	out = []
	for x in text.split(','):
		if '-' in x:
			a,_,b = x.partition('-')
			out += [(int(a),int(b))]
		else:
			out += [int(x)]
	return out

def _list_steps():
	jobs = _get_jobs(depth=3)
	jobs_str = ', '.join(jobs)
	print(f'Available tasks: {jobs_str}\n')
	for j in jobs:
		print(f"{j}:")
		for fun in jobs[j]:
			_,_,s = fun.__name__.partition('_step')
			label = (fun.__doc__ or '').split('\n')[0]
			label = f' -- {label}' if label else ''
			print(f'• step {s:4}{label}')
		print()

# -----------------------------------------------------------------------------

def run_steps(job, args=None, ctx=None, depth=3):
	ctx = {} if ctx==None else ctx
	jobs = _get_jobs(depth=depth)
	all_steps = jobs[job]
	steps = _filter_steps(all_steps, args)
	for i,fun in enumerate(steps):
		t0 = time.time()
		label = (fun.__doc__ or '').split('\n')[0]
		label = f' -- {label}' if label else ''
		print(f'running {fun.__name__}{label} ', end='', file=sys.stderr, flush=True)
		fun(ctx)
		dt = time.time()-t0
		print(f'... done in {dt:0.1f}s', file=sys.stderr, flush=True)
	return ctx


def run_cli():
	# TODO: run all jobs/tasks in the script
	# TODO: include/exclude steps with tags (ie step20a step20b)
	# TODO: cfg from env
	# TODO: show job/task description in _list_steps()
	# TODO: import steps from other files -> no, use xxx_step10 = other.zzz_step10
	args = sys.argv[1:]
	if not args:
		print(USAGE)
		_list_steps()
		exit(1)
	for a in args:
		job,_,raw_steps = a.partition(':')
		steps = _parse_steps(raw_steps)
		run_steps(job, steps)
