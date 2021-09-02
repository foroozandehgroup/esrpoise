from esrpoise import Xepr_link
import os
import shutil
import filecmp


def test_modif_def():
    var_name = ['p1', 'aa1']
    var_value = ['92', '88']
    def_file = os.path.join(os.getcwd(), 'tests', 'def_file_test.def')
    Xepr_link.modif_def(None, def_file, var_name, var_value)

    # create copy for comparison
    def_file_copy = def_file[0:-4]+'_copy.def'
    shutil.copy(def_file, def_file_copy)

    # modify value
    var_value = ['17.4', '777']
    Xepr_link.modif_def(None, def_file, var_name, var_value)

    # come back to original value
    var_value = ['92', '88']
    Xepr_link.modif_def(None, def_file, var_name, var_value)

    assert filecmp.cmp(def_file, def_file_copy, shallow=False)

    os.remove(def_file_copy)
