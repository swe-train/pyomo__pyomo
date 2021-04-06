#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright 2017 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and 
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain 
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

import pyomo.common.unittest as unittest
import glob
import os
import os.path
import subprocess
import sys
from itertools import zip_longest
from pyomo.opt import check_available_solvers
from pyomo.common.dependencies import attempt_import
from filecmp import cmp
parameterized, param_available = attempt_import('parameterized')
if not param_available:
    raise unittest.SkipTest('Parameterized is not available.')

# Find all *.txt files, and use them to define baseline tests
currdir = os.path.dirname(os.path.abspath(__file__))
datadir = currdir
testdirs = [currdir, ]

solver_dependencies =   {
    # abstract_ch
    'test_abstract_ch_wl_abstract_script': ['glpk'],
    'test_abstract_ch_pyomo_wl_abstract': ['glpk'],
    'test_abstract_ch_pyomo_solve1': ['glpk'],
    'test_abstract_ch_pyomo_solve2': ['glpk'],
    'test_abstract_ch_pyomo_solve3': ['glpk'],
    'test_abstract_ch_pyomo_solve4': ['glpk'],
    'test_abstract_ch_pyomo_solve5': ['glpk'],
    'test_abstract_ch_pyomo_diet1': ['glpk'],
    'test_abstract_ch_pyomo_buildactions_works': ['glpk'],
    'test_abstract_ch_pyomo_abstract5_ns1': ['glpk'],
    'test_abstract_ch_pyomo_abstract5_ns2': ['glpk'],
    'test_abstract_ch_pyomo_abstract5_ns3': ['glpk'],
    'test_abstract_ch_pyomo_abstract6': ['glpk'],
    'test_abstract_ch_pyomo_abstract7': ['glpk'],
    'test_abstract_ch_pyomo_AbstractH': ['ipopt'],
    'test_abstract_ch_AbstHLinScript': ['glpk'],
    'test_abstract_ch_pyomo_AbstractHLinear': ['glpk'],
    
    # blocks_ch
    'test_blocks_ch_lotsizing': ['glpk'],
    'test_blocks_ch_blocks_lotsizing': ['glpk'],
    
    # dae_ch
    'test_dae_ch_run_path_constraint_tester': ['ipopt'],
    
    # gdp_ch
    'test_gdp_ch_pyomo_scont': ['glpk'],
    'test_gdp_ch_pyomo_scont2': ['glpk'],
    'test_gdp_ch_scont_script': ['glpk'],
    
    # intro_ch'
    'test_intro_ch_pyomo_concrete1_generic': ['glpk'],
    'test_intro_ch_pyomo_concrete1': ['glpk'],
    'test_intro_ch_pyomo_coloring_concrete': ['glpk'],
    'test_intro_ch_pyomo_abstract5': ['glpk'],
    
    # mpec_ch
    'test_mpec_ch_path1': ['path'],
    'test_mpec_ch_nlp_ex1b': ['ipopt'],
    'test_mpec_ch_nlp_ex1c': ['ipopt'],
    'test_mpec_ch_nlp_ex1d': ['ipopt'],
    'test_mpec_ch_nlp_ex1e': ['ipopt'],
    'test_mpec_ch_nlp_ex2': ['ipopt'],
    'test_mpec_ch_nlp1': ['ipopt'],
    'test_mpec_ch_nlp2': ['ipopt'],
    'test_mpec_ch_nlp3': ['ipopt'],
    'test_mpec_ch_mip1': ['glpk'],
    
    # nonlinear_ch
    'test_rosen_rosenbrock': ['ipopt'],
    'test_react_design_ReactorDesign': ['ipopt'],
    'test_react_design_ReactorDesignTable': ['ipopt'],
    'test_multimodal_multimodal_init1': ['ipopt'],
    'test_multimodal_multimodal_init2': ['ipopt'],
    'test_disease_est_disease_estimation': ['ipopt'],
    'test_deer_DeerProblem': ['ipopt'],
    
    # scripts_ch
    'test_sudoku_sudoku_run': ['glpk'],
    'test_scripts_ch_warehouse_script': ['glpk'],
    'test_scripts_ch_warehouse_print': ['glpk'],
    'test_scripts_ch_warehouse_cuts': ['glpk'],
    'test_scripts_ch_prob_mod_ex': ['glpk'],
    'test_scripts_ch_attributes': ['glpk'],
    
    # optimization_ch
    'test_optimization_ch_ConcHLinScript': ['glpk'],
    
    # overview_ch
    'test_overview_ch_wl_mutable_excel': ['glpk'],
    'test_overview_ch_wl_excel': ['glpk'],
    'test_overview_ch_wl_concrete_script': ['glpk'],
    'test_overview_ch_wl_abstract_script': ['glpk'],
    'test_overview_ch_pyomo_wl_abstract': ['glpk'],
    
    # performance_ch
    'test_performance_ch_wl': ['gurobi', 'gurobi_persistent'],
    'test_performance_ch_persistent': ['gurobi', 'gurobi_persistent'],
}
package_dependencies =  {
    # abstract_ch'
    'test_abstract_ch_pyomo_solve4': ['yaml'],
    'test_abstract_ch_pyomo_solve5': ['yaml'],

    # gdp_ch
    'test_gdp_ch_pyomo_scont': ['yaml'],
    'test_gdp_ch_pyomo_scont2': ['yaml'],

    # overview_ch'
    'test_overview_ch_wl_excel': ['pandas', 'xlrd'],
    'test_overview_ch_wl_mutable_excel': ['pandas', 'xlrd'],
    
    # scripts_ch'
    'test_scripts_ch_warehouse_cuts': ['matplotlib'],
    
    # performance_ch'
    'test_performance_ch_wl': ['numpy','matplotlib'],
}


#
# Initialize the availability data
#
solvers_used = set(sum(list(solver_dependencies.values()), []))
available_solvers = check_available_solvers(*solvers_used)
solver_available = {solver_:solver_ in available_solvers for solver_ in solvers_used}

package_available = {}        
packages_used = set(sum(list(package_dependencies.values()), []))
for package_ in packages_used:
    pack, pack_avail = attempt_import(package_)
    package_available[package_] = pack_avail


def check_skip(name):
    """
    Return a boolean if the test should be skipped
    """

    if name in solver_dependencies:
        solvers_ = solver_dependencies[name]
        if not all([solver_available[i] for i in solvers_]):
            # Skip the test because a solver is not available
            _missing = []
            for i in solvers_:
                if not solver_available[i]:
                    _missing.append(i)
            return "Solver%s %s %s not available" % (
                's' if len(_missing) > 1 else '',
                ", ".join(_missing),
                'are' if len(_missing) > 1 else 'is',)

    if name in package_dependencies:
        packages_ = package_dependencies[name]
        if not all([package_available[i] for i in packages_]):
            # Skip the test because a package is not available
            _missing = []
            for i in packages_:
                if not package_available[i]:
                    _missing.append(i)
            return "Package%s %s %s not available" % (
                's' if len(_missing) > 1 else '',
                ", ".join(_missing),
                'are' if len(_missing) > 1 else 'is',)
    return False

def filter(line):
    """
    Ignore certain text when comparing output with baseline
    """
    for field in ( '[',
                   'password:',
                   'http:',
                   'Job ',
                   'Importing module',
                   'Function',
                   'File', 
                   '^',):
        if line.startswith(field):
            return True
    for field in ( 'Total CPU',
                   'Ipopt',
                   'Status: optimal',
                   'Status: feasible',
                   'time:',
                   'Time:',
                   'with format cpxlp',
                   'usermodel = <module',
                   'execution time=',
                   'Solver results file:' ):
        if field in line:
            return True
    return False


def filter_items(items):
    filtered = []
    for i in items:
        if not i:
            continue
        if not (i.startswith('/') or i.startswith(":\\", 1)):
            try:
                filtered.append(float(i))
            except:
                filtered.append(i)
    return filtered


py_test_tuples=[]
sh_test_tuples=[]

for tdir in testdirs:

  for testdir in glob.glob(os.path.join(tdir,'*')):
    if not os.path.isdir(testdir):
        continue
    # Only test files in directories ending in -ch. These directories
    # contain the updated python and scripting files corresponding to
    # each chapter in the book.
    if '-ch' not in testdir:
        continue
   
    # Find all .py files in the test directory
    for file in list(glob.glob(os.path.join(testdir,'*.py'))) \
        + list(glob.glob(os.path.join(testdir,'*','*.py'))):
    
        test_file = os.path.abspath(file)
        bname = os.path.basename(test_file)
        dir_ = os.path.dirname(test_file)
        name=os.path.splitext(bname)[0]
        tname = os.path.basename(dir_)+'_'+name
    
        suffix = None
        # Look for txt and yml file names matching py file names. Add
        # a test for any found
        for suffix_ in ['.txt', '.yml']:
            if os.path.exists(os.path.join(dir_,name+suffix_)):
                suffix = suffix_
                break
        if not suffix is None:
            # cwd = os.getcwd()
            tname = tname.replace('-','_')
            tname = tname.replace('.','_')
        
            # Create list of tuples with (test_name, test_file, baseline_file)
            py_test_tuples.append((tname, test_file, os.path.join(dir_,name+suffix)))

    # Find all .sh files in the test directory
    for file in list(glob.glob(os.path.join(testdir,'*.sh'))) \
            + list(glob.glob(os.path.join(testdir,'*','*.sh'))):
        test_file = os.path.abspath(file)
        bname = os.path.basename(file)
        dir_ = os.path.dirname(os.path.abspath(file))+os.sep
        name='.'.join(bname.split('.')[:-1])
        tname = os.path.basename(os.path.dirname(dir_))+'_'+name
        suffix = None
        # Look for txt and yml file names matching sh file names. Add
        # a test for any found
        for suffix_ in ['.txt', '.yml']:
            if os.path.exists(dir_+name+suffix_):
                suffix = suffix_
                break
        if not suffix is None:
            tname = tname.replace('-','_')
            tname = tname.replace('.','_')

            # Create list of tuples with (test_name, test_file, baseline_file)
            sh_test_tuples.append((tname, test_file, os.path.join(dir_,name+suffix)))


def custom_name_func(test_func, test_num, test_params):
    func_name = test_func.__name__
    return "test_%s_%s" %(test_params.args[0], func_name[-2:])

class TestBookExamples(unittest.TestCase):

    def compare_files(self, out_file, base_file):
        try:
            self.assertTrue(cmp(out_file, base_file),
                            msg="Files %s and %s differ" % (out_file, base_file))
        except:
            with open(out_file, 'r') as f1, open(base_file, 'r') as f2:
                out_file_contents = f1.read()
                base_file_contents = f2.read()
                f1_contents = out_file_contents.strip().split('\n')
                f2_contents = base_file_contents.strip().split('\n')
                f1_filtered = []
                f2_filtered = []
                for item1, item2 in zip_longest(f1_contents, f2_contents):
                    if not item1 and not item2:
                        # Both empty lines
                        continue
                    elif not item1 or not item2:
                        # Empty line in one file but not the other
                        f1_filtered.append(item1)
                        f2_filtered.append(item2)
                        break
                    if not filter(item1):
                        items1 = item1.strip().split()
                        items2 = item2.strip().split()
                        f1_filtered.append(filter_items(items1))
                        f2_filtered.append(filter_items(items2))
                try:
                    self.assertStructuredAlmostEqual(f2_filtered, f1_filtered,
                                                 abstol=1e-6,
                                                 allow_second_superset=False)
                except AssertionError as m:
                    print('---------------------------------')
                    print('BASELINE FILE')
                    print('---------------------------------')
                    print(base_file_contents)
                    print('=================================')
                    print('---------------------------------')
                    print('TEST OUTPUT FILE')
                    print('---------------------------------')
                    print(out_file_contents)
                    raise(m)

    @parameterized.parameterized.expand(py_test_tuples, name_func=custom_name_func)
    def test_book_py(self, tname, test_file, base_file):
        bname = os.path.basename(test_file)
        dir_ = os.path.dirname(test_file)      

        skip_msg = check_skip('test_'+tname)
        if skip_msg:
            raise unittest.SkipTest(skip_msg)

        cwd = os.getcwd()
        os.chdir(dir_)
        out_file = os.path.splitext(test_file)[0]+'.out'
        with open(out_file, 'w') as f:
            subprocess.run([sys.executable, bname], stdout=f, stderr=f, cwd=dir_)
        os.chdir(cwd)

        self.compare_files(out_file, base_file)
        os.remove(out_file)

    @parameterized.parameterized.expand(sh_test_tuples, name_func=custom_name_func)
    def test_book_sh(self, tname, test_file, base_file):
        bname = os.path.basename(test_file)
        dir_ = os.path.dirname(test_file)

        skip_msg = check_skip('test_'+tname)
        if skip_msg:
            raise unittest.SkipTest(skip_msg)

        # Skip all shell tests on Windows.
        if os.name == 'nt':
           raise unittest.SkipTest("Shell tests are not runnable on Windows")
    
        cwd = os.getcwd()
        os.chdir(dir_)
        out_file = os.path.splitext(test_file)[0]+'.out'
        with open(out_file, 'w') as f:
            subprocess.run(['bash', bname], stdout=f, stderr=f, cwd=dir_)
        os.chdir(cwd)

        self.compare_files(out_file, base_file)
        os.remove(out_file)


if __name__ == "__main__":
    unittest.main()
