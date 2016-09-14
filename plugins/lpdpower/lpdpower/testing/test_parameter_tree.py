""" Test ParameterTree class from lpdpower.

Tim Nicholls, STFC Application Engingeering
"""

from copy import deepcopy
from nose.tools import *
from lpdpower.parameter_tree import ParameterTree, ParameterTreeError

class TestParameterTree():

    """Test the ParameterTree class.
    """

    @classmethod
    def setup_class(cls):

        cls.int_value = 1234
        cls.float_value = 3.1415
        cls.bool_value = True
        cls.str_value = 'theString'
        cls.list_values = range(4)

        cls.simple_dict = {
            'intParam': cls.int_value,
            'floatParam': cls.float_value,
            'boolParam': cls.bool_value,
            'strParam':  cls.str_value,
        }

        cls.simple_tree = ParameterTree(cls.simple_dict)

        # Set up nested dict of parameters for a more complex tree
        cls.nested_dict = cls.simple_dict.copy()
        cls.nested_dict['branch'] = {
            'branchIntParam': 4567,
            'branchStrParam': 'theBranch',
        }
        cls.nested_tree = ParameterTree(cls.nested_dict)

        cls.callback_tree = deepcopy(cls.nested_tree)
        cls.callback_tree.addCallback('branch/', cls.branch_callback)

        cls.branch_callback_count = 0

        cls.complex_tree_branch = ParameterTree(deepcopy(cls.nested_dict))
        cls.complex_tree_branch.addCallback('', cls.branch_callback)

        cls.complex_tree = ParameterTree({
            'intParam': cls.int_value,
            'callableRoParam': (lambda: cls.int_value, None),
            'listParam': cls.list_values,
            'branch': cls.complex_tree_branch,
        })

    @classmethod
    def branch_callback(cls, path, value):
        cls.branch_callback_count += 1
        # print("branch_callback call #{}: on path {} with value {}".format(
        #     cls.branch_callback_count, path, value))

    def setup(self):
        TestParameterTree.branch_callback_count = 0
        pass

    def test_simple_tree_returns_dict(self):

        dt_vals = self.simple_tree.getData('')
        assert_equal(dt_vals, self.simple_dict)

    def test_simple_tree_single_values(self):

        dt_int_val = self.simple_tree.getData('intParam')
        assert_equal(dt_int_val['intParam'], self.int_value)

        dt_float_val = self.simple_tree.getData('floatParam')
        assert_equal(dt_float_val['floatParam'], self.float_value)

        dt_bool_val = self.simple_tree.getData('boolParam')
        assert_equal(dt_bool_val['boolParam'], self.bool_value)

        dt_str_val = self.simple_tree.getData('strParam')
        assert_equal(dt_str_val['strParam'], self.str_value)

    def test_simple_tree_missing_value(self):

        with assert_raises_regexp(ParameterTreeError, 'The path missing is invalid'):
            self.simple_tree.getData('missing')

    def test_nested_tree_returns_nested_dict(self):

        nested_dt_vals = self.nested_tree.getData('')
        assert_equal(nested_dt_vals, self.nested_dict)

    def test_nested_tree_branch_returns_dict(self):

        branch_vals = self.nested_tree.getData('branch')
        assert_equals(branch_vals['branch'], self.nested_dict['branch'])

    def test_callback_modifies_branch_value(self):

        branch_data = deepcopy(self.nested_dict['branch'])
        branch_data['branchIntParam'] = 90210

        self.callback_tree.setData('branch', branch_data)

        modified_branch_vals = self.callback_tree.getData('branch')
        assert_equals(modified_branch_vals['branch'], branch_data)
        assert_equals(self.branch_callback_count, len(branch_data))

    def test_callback_modifies_single_branch_value(self):

        int_param = 22603
        self.callback_tree.setData('branch/branchIntParam', int_param)

    def test_callback_with_extra_branch_paths(self):

        branch_data = deepcopy(self.nested_dict['branch'])
        branch_data['extraParam'] = 'oops'

        with assert_raises_regexp(ParameterTreeError, 'Invalid path'):
            self.callback_tree.setData('branch', branch_data)

    def test_complex_tree_calls_leaf_nodes(self):

        complex_vals = self.complex_tree.getData('')
        assert_equals(complex_vals['intParam'], self.int_value)
        assert_equals(complex_vals['callableRoParam'], self.int_value)

    def test_complex_tree_callable_readonly(self):

        with assert_raises_regexp(ParameterTreeError, 'Parameter callableRoParam is read-only'):
            self.complex_tree.setData('callableRoParam', 1234)

    def test_complex_tree_set_invalid_path(self):

        invalid_path = 'invalidPath/toNothing'
        with assert_raises_regexp(ParameterTreeError, 'Invalid path: {}'.format(invalid_path)):
            self.complex_tree.setData(invalid_path, 0)

    def test_complex_tree_set_top_level(self):

        complex_vals = self.complex_tree.getData('')
        complex_vals_copy = deepcopy(complex_vals)
        del complex_vals_copy['callableRoParam']

        self.complex_tree.setData('', complex_vals_copy)
        complex_vals2 = self.complex_tree.getData('')
        assert_equals(complex_vals, complex_vals2)

    def test_complex_tree_inject_spurious_dict(self):

        param_data = {'intParam': 9876}

        with assert_raises_regexp(ParameterTreeError, 'Type mismatch updating intParam'):
            self.complex_tree.setData('intParam', param_data)

class TestRwParameterTree():

    @classmethod
    def setup_class(cls):

        cls.int_rw_param = 4576
        cls.int_ro_param = 255374
        cls.int_rw_value = 9876
        cls.int_wo_param = 0

        cls.nested_rw_param = 53.752
        cls.nested_ro_value = 9.8765

        nested_tree = ParameterTree({
            'nestedRwParam': (cls.nestedRwParamGet, cls.nestedRwParamSet),
            'nestedRoParam': cls.nested_ro_value
        })

        cls.rw_callable_tree = ParameterTree({
            'intCallableRwParam': (cls.intCallableRwParamGet, cls.intCallableRwParamSet),
            'intCallableRoParam': (cls.intCallableRoParamGet, None),
            'intCallableWoParam': (None, cls.intCallableWoParamSet),
            'intCallableRwValue': (cls.int_rw_value, cls.intCallableRoParamSet),
            'branch': nested_tree
        })

    @classmethod
    def intCallableRwParamSet(cls, value):
        cls.int_rw_param = value

    @classmethod
    def intCallableRwParamGet(cls):
        return cls.int_rw_param

    @classmethod
    def intCallableRoParamGet(cls):
        return cls.int_ro_param

    @classmethod
    def intCallableWoParamSet(cls, value):
        cls.int_wo_param = value

    @classmethod
    def intCallableRoParamSet(cls, value):
        pass

    @classmethod
    def nestedRwParamSet(cls, value):
        cls.nested_rw_param = value

    @classmethod
    def nestedRwParamGet(cls):
        return cls.nested_rw_param

    def test_rw_tree_simple_get_values(self):

        dt_rw_int_param = self.rw_callable_tree.getData('intCallableRwParam')
        assert_equal(dt_rw_int_param['intCallableRwParam'], self.int_rw_param)

        dt_ro_int_param = self.rw_callable_tree.getData('intCallableRoParam')
        assert_equal(dt_ro_int_param['intCallableRoParam'], self.int_ro_param)

        dt_rw_int_value = self.rw_callable_tree.getData('intCallableRwValue')
        assert_equal(dt_rw_int_value['intCallableRwValue'], self.int_rw_value)

    def test_rw_tree_simple_set_value(self):

        new_int_value = 91210
        self.rw_callable_tree.setData('intCallableRwParam', new_int_value)

        dt_rw_int_param = self.rw_callable_tree.getData('intCallableRwParam')
        assert_equal(dt_rw_int_param['intCallableRwParam'], new_int_value)

    def test_rw_tree_set_ro_param(self):

        with assert_raises_regexp(ParameterTreeError, 'Parameter intCallableRoParam is read-only'):
            self.rw_callable_tree.setData('intCallableRoParam', 0)

    def test_rw_callable_tree_set_wo_param(self):

        new_value = 1234
        self.rw_callable_tree.setData('intCallableWoParam', new_value)
        assert_equal(self.int_wo_param, new_value)

    def test_rw_callable_nested_param_get(self):

        dt_nested_param = self.rw_callable_tree.getData('branch/nestedRwParam')
        assert_equal(dt_nested_param['nestedRwParam'], self.nested_rw_param)

    def test_rw_callable_nested_param_set(self):

        new_float_value = self.nested_rw_param + 2.3456
        self.rw_callable_tree.setData('branch/nestedRwParam', new_float_value)
        assert_equal(self.nested_rw_param, new_float_value)
