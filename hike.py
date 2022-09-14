__author__ = 'Maciej Obarski'
__version__ = '0.2.4'
__license__ = 'MIT'

# CHANGELOG:
# 0.2.5 - run_steps run time
# 0.2.4 - cosmetic changes in run_steps
# 0.2.3 - cosmetic changes in step listing
# 0.2.2 - cosmetic changes in step listing
# 0.2.1 - omit underscores in steps listing
# 0.2 - variants

import re
import time
import sys
import os

USAGE = f"""USAGE: {sys.argv[0]} [task1:[:steps]] [task2[:steps]] [--use variants]

steps - comma separated list of step identifiers; leave empty to select
        all the steps; use dash to specify ranges; example: '10,20,30-40,99'

variants - coma separated list of step variants to use; example: 'cpu,windows'

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
		match = re.findall('(.+?)_step(\d+)(.*)',x)
		if match:
			job = match[0][0]
			if job not in out: out[job] = []
			out[job] += [env[x]]
	return out


def _filter_steps(fun_list, args, use):
	# TODO: refactor
	if args is None:
		args = [(None, None)]
	out = []
	for a in args:
		if type(a) is int:
			for f in fun_list:
				m = re.findall('(.+?)_step(\d+)(.*)', f.__name__)
				if m:
					job, step, variant = m[0]
					if step==str(a):
						if variant:
							if set(variant.strip('_').split('_')) & set(use):
								out += [f]
						else:
							out += [f]
		if type(a) is tuple:
			lo = a[0] or float('-inf')
			hi = a[1] or float('+inf')
			for f in fun_list:
				m = re.findall('(.+?)_step(\d+)(.*)', f.__name__)
				if m:
					job, step, variant = m[0]
					if lo <= int(step) <= hi:
						if variant:
							if set(variant.strip('_').split('_')) & set(use):
								out += [f]
						else:
							out += [f]
	return out


def _parse_steps(text):
	"converts steps list from string to actual list, ie '10,20-50,99' -> [10,(20,50),99]"
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
		width = max([len(f.__name__.partition('_step')[2]) for f in jobs[j]])
		print(f" {j}:")
		for i,fun in enumerate(jobs[j]):
			_,_,s = fun.__name__.partition('_step')
			s = s.replace('_', ' ')
			label = (fun.__doc__ or '').split('\n')[0]
			label = f' -- {label}' if label else ''
			prefix = "└─" if i==len(jobs[j])-1 else "├─"
			print(f'  {prefix} {s:{width}}{label}')
		print()

# -----------------------------------------------------------------------------

def run_steps(job, args=None, ctx=None, depth=2, use=[]):
	t0 = time.time()
	ctx = {} if ctx==None else ctx
	jobs = _get_jobs(depth=depth)
	all_steps = jobs[job]
	steps = _filter_steps(all_steps, args, use)
	width = max([len(fun.__name__) for fun in steps])
	for i,fun in enumerate(steps):
		#t1 = time.time()
		label = (fun.__doc__ or '').split('\n')[0]
		label = f' -- {label}' if label else ''
		print(f'running {fun.__name__:{width}}{label} ', end='\n', file=sys.stderr, flush=True)
		fun(ctx)
		#dt = time.time()-t1
		#print(f'... done in {dt:0.1f}s', file=sys.stderr, flush=True)
	dt = time.time() - t0
	print(f'done in {dt:0.1f}s', file=sys.stderr, flush=True)
	return ctx


def run_cli():
	# TODO: run all jobs/tasks in the script
	# TODO: cfg from env
	# TODO: show job/task description in _list_steps()
	# TODO: import steps from other files -> no, use xxx_step10 = other.zzz_step10
	args = sys.argv[1:]
	use_idx = [i for i,_ in enumerate(args) if args[i]=='--use']
	use_idx.sort(reverse=True)
	use = set()
	for i in use_idx:
		use.update(args[i+1].split(','))
		del args[i+1]
		del args[i]
	#
	if not args:
		print(USAGE)
		_list_steps()
		exit(1)
	ctx = {'use':use}
	for a in args:
		job,_,raw_steps = a.partition(':')
		steps = _parse_steps(raw_steps)
		run_steps(job, steps, ctx=ctx, use=use, depth=3)

