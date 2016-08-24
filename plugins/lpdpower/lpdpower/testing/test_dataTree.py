""" Test DataTree class from lpdpower.

Tim Nicholls, STFC Application Engingeering
"""

from copy import deepcopy
from nose.tools import *
from lpdpower.DataTree import DataTree, InvalidRequest
import pprint

class TestDataTree():

    """Test the DataTree class.
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

        cls.simple_tree = DataTree(cls.simple_dict)

        # Set up nested dict of parameters for a more complex tree
        cls.nested_dict = cls.simple_dict.copy()
        cls.nested_dict['branch'] = {
            'branchIntParam': 4567,
            'branchStrParam': 'theBranch',
        }
        cls.nested_tree = DataTree(cls.nested_dict)

        cls.callback_tree = deepcopy(cls.nested_tree)
        cls.callback_tree.addCallback('branch/', cls.branch_callback)

        cls.branch_callback_count = 0

        cls.complex_tree_branch = DataTree(deepcopy(cls.nested_dict))
        cls.complex_tree_branch.addCallback('', cls.branch_callback)

        cls.complex_tree = DataTree({
            'intParam': cls.int_value,
            'callableIntParam': lambda: cls.int_value,
            'listParam': cls.list_values,
            'branch': cls.complex_tree_branch,
        })

    @classmethod
    def branch_callback(cls, path, value):
        cls.branch_callback_count += 1
        # print("branch_callback call #{}: on path {} with value {}".format(
        #     cls.branch_callback_count, path, value))

    def setup(self):
        TestDataTree.branch_callback_count = 0
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

        with assert_raises_regexp(InvalidRequest, 'The path missing is invalid'):
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

        with assert_raises_regexp(InvalidRequest, 'Invalid path'):
            self.callback_tree.setData('branch', branch_data)

    def test_complex_tree_calls_leaf_nodes(self):

        complex_vals = self.complex_tree.getData('')
        assert_equals(complex_vals['intParam'], self.int_value)
        assert_equals(complex_vals['callableIntParam'], self.int_value)

    def test_complex_tree_callable_readonly(self):

        with assert_raises_regexp(InvalidRequest, "Cannot set value of read only path"):
            self.complex_tree.setData('callableIntParam', 1234)

    def test_complex_tree_set_invalid_path(self):

        invalid_path = 'invalidPath/toNothing'
        with assert_raises_regexp(InvalidRequest, 'Invalid path: {}'.format(invalid_path)):
            self.complex_tree.setData(invalid_path, 0)

    def test_complex_tree_set_top_level(self):

        complex_vals = self.complex_tree.getData('')
        complex_vals_copy = deepcopy(complex_vals)
        del complex_vals_copy['callableIntParam']

        self.complex_tree.setData('', complex_vals_copy)
        complex_vals2 = self.complex_tree.getData('')
        assert_equals(complex_vals, complex_vals2)

    def test_complex_tree_inject_spurious_dict(self):

        param_data = {'intParam': 9876}

        with assert_raises_regexp(InvalidRequest, 'Type mismatch updating intParam'):
            self.complex_tree.setData('intParam', param_data)
