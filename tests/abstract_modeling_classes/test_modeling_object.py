from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject

import unittest
from unittest.mock import patch, MagicMock

MODELING_OBJ_CLASS_PATH = "efootprint.abstract_modeling_classes.modeling_object"


class ModelingObjectForTesting(ModelingObject):
    def __init__(self, name, custom_input=None):
        super().__init__(name)
        if custom_input is not None:
            self.custom_input = custom_input

    def compute_calculated_attributes(self):
        pass

    def modeling_objects_whose_attributes_depend_directly_on_me(self):
        return []


class TestModelingObject(unittest.TestCase):

    def setUp(self):
        self.modeling_object = ModelingObjectForTesting("test_object")

    def test_setattr_sets_modeling_obj_container(self):
        value = MagicMock(modeling_obj_container=None)

        with patch(f"{MODELING_OBJ_CLASS_PATH}.type", lambda x: ExplainableObject):
            self.modeling_object.attribute = value

        value.set_modeling_obj_container.assert_called_once_with(self.modeling_object, "attribute")

    def test_handle_model_input_update_triggers(self):
        value = MagicMock(
            modeling_obj_container=None, left_parent=None, right_parent=None, mock_type=ExplainableObject)
        old_value = MagicMock(mock_type=ExplainableObject)
        self.modeling_object.attribute = old_value
        self.modeling_object.handle_model_input_update = MagicMock()

        with patch(f"{MODELING_OBJ_CLASS_PATH}.type", lambda x: x.mock_type):
            self.modeling_object.attribute = value

            self.modeling_object.handle_model_input_update.assert_called_once_with(old_value)

    def test_handle_model_input_update_single_level_descendants(self):
        mod_obj_container = "mod_obj"
        parent = MagicMock()
        parent.id = 'parent_id'

        child1 = MagicMock()
        child1.id = 'child1_id'
        child1.direct_children_with_id = []
        child1.direct_ancestors_with_id = [parent]

        child2 = MagicMock()
        child2.id = 'child2_id'
        child2.direct_children_with_id = []
        child2.direct_ancestors_with_id = [parent]

        for index, child in enumerate([child1, child2]):
            child.modeling_obj_container = mod_obj_container
            child.attr_name_in_mod_obj_container = f"attr_{index}"

        parent.get_all_descendants_with_id.return_value = [child1, child2]
        parent.direct_children_with_id = [child1, child2]

        with patch(f'{MODELING_OBJ_CLASS_PATH}.ModelingObject.retrieve_update_function_from_attribute_name') \
                as mock_retrieve_update_func:
            mock_retrieve_update_func.return_value = MagicMock()

            self.modeling_object.handle_model_input_update(parent)

            mock_retrieve_update_func.assert_any_call(mod_obj_container, "attr_0")
            mock_retrieve_update_func.assert_any_call(mod_obj_container, "attr_1")

            self.assertEqual(mock_retrieve_update_func.call_count, 2)

    def test_handle_model_input_update_multiple_levels_of_descendants(self):
        mod_obj_container = "mod_obj_container"
        parent = MagicMock()
        parent.id = 'parent_id'

        child1 = MagicMock()
        child1.id = 'child1_id'
        child1.direct_ancestors_with_id = [parent]

        grandchild1 = MagicMock()
        grandchild1.id = 'grandchild1_id'
        grandchild1.direct_children_with_id = []
        grandchild1.direct_ancestors_with_id = [child1]

        grandchild2 = MagicMock()
        grandchild2.id = 'grandchild2_id'
        grandchild2.direct_children_with_id = []
        grandchild2.direct_ancestors_with_id = [child1]

        child1.direct_children_with_id = [grandchild1, grandchild2]
        parent.get_all_descendants_with_id.return_value = [child1, grandchild1, grandchild2]
        parent.direct_children_with_id = [child1]

        for index, child in enumerate([child1, grandchild1, grandchild2]):
            child.modeling_obj_container = mod_obj_container
            child.attr_name_in_mod_obj_container = f"attr_{index}"

        with patch(f'{MODELING_OBJ_CLASS_PATH}.ModelingObject.retrieve_update_function_from_attribute_name') \
                as mock_retrieve_update_func:
            mock_retrieve_update_func.return_value = MagicMock()

            self.modeling_object.handle_model_input_update(parent)

            mock_retrieve_update_func.assert_any_call(mod_obj_container, "attr_0")
            mock_retrieve_update_func.assert_any_call(mod_obj_container, "attr_1")
            mock_retrieve_update_func.assert_any_call(mod_obj_container, "attr_2")

            self.assertEqual(mock_retrieve_update_func.call_count, 3)

    def test_launch_attributes_computation_chain(self):
        dep1 = MagicMock()
        dep2 = MagicMock()
        dep1_sub1 = MagicMock()
        dep1_sub2 = MagicMock()
        dep2_sub1 = MagicMock()
        dep2_sub2 = MagicMock()

        self.modeling_object.modeling_objects_whose_attributes_depend_directly_on_me = [dep1, dep2]
        dep1.modeling_objects_whose_attributes_depend_directly_on_me = [dep1_sub1, dep1_sub2]
        dep2.modeling_objects_whose_attributes_depend_directly_on_me = [dep2_sub1, dep2_sub2]

        for obj in [dep1_sub1, dep1_sub2, dep2_sub1, dep2_sub2]:
            obj.modeling_objects_whose_attributes_depend_directly_on_me = []

        self.modeling_object.launch_attributes_computation_chain()

        for dep in [dep1, dep2, dep1_sub1, dep1_sub2, dep2_sub1, dep2_sub2]:
            dep.compute_calculated_attributes.assert_called_once()

    def test_list_attribute_update_works_with_classical_syntax(self):
        val1 = MagicMock()
        val2 = MagicMock()
        val3 = MagicMock()

        mod_obj = ModelingObjectForTesting("test mod obj", custom_input=[val1, val2])

        with patch(f'{MODELING_OBJ_CLASS_PATH}.ModelingObject.handle_object_list_link_update') \
                as mock_list_obj_update_func:
            mod_obj.custom_input = [val1, val2, val3]
            mock_list_obj_update_func.assert_called_once_with([val1, val2, val3], [val1, val2])

    def test_list_attribute_update_works_with_list_condensed_addition_syntax(self):
        val1 = MagicMock()
        val2 = MagicMock()
        val3 = MagicMock()

        mod_obj = ModelingObjectForTesting("test mod obj", custom_input=[val1, val2])

        with patch(f'{MODELING_OBJ_CLASS_PATH}.ModelingObject.handle_object_list_link_update') \
                as mock_list_obj_update_func:
            assert mod_obj.custom_input__previous_list_value_set == [val1, val2]
            mod_obj.custom_input += [val3]
            assert mod_obj.custom_input__previous_list_value_set == [val1, val2, val3]
            mock_list_obj_update_func.assert_called_once_with([val1, val2, val3], [val1, val2])


if __name__ == "__main__":
    unittest.main()
