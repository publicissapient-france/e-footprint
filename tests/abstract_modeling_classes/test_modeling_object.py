from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject

import unittest
from unittest.mock import patch, MagicMock

MODELING_OBJ_CLASS_PATH = "efootprint.abstract_modeling_classes.modeling_object"


class TestModelingObject(unittest.TestCase):

    def setUp(self):
        class TestModelingSubObject(ModelingObject):
            def compute_calculated_attributes(self):
                pass

            @property
            def modeling_objects_whose_attributes_depend_directly_on_me(self):
                return []

        self.modeling_object = TestModelingSubObject("test_object")

    def test_setattr_sets_modeling_obj_container(self):
        value = MagicMock(modeling_obj_container=None)

        with patch(f"{MODELING_OBJ_CLASS_PATH}.type", lambda x: ExplainableObject):
            self.modeling_object.attribute = value

        value.set_modeling_obj_container.assert_called_once_with(self.modeling_object, "attribute")

    def test_handle_model_input_update_triggers(self):
        value = MagicMock(
            modeling_obj_container=None, left_child=None, right_child=None, mock_type=ExplainableObject)
        old_value = MagicMock(mock_type=ExplainableObject)
        self.modeling_object.attribute = old_value
        self.modeling_object.handle_model_input_update = MagicMock()

        with patch(f"{MODELING_OBJ_CLASS_PATH}.type", lambda x: x.mock_type):
            self.modeling_object.attribute = value

            self.modeling_object.handle_model_input_update.assert_called_once_with(old_value)

    def test_handle_model_input_update(self):
        # TODO implement
        pass


if __name__ == "__main__":
    unittest.main()
