import os
from inspect import signature

from jinja2 import Template
import ruamel.yaml

from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyUsage
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from docs_sources.doc_utils.docs_case import (
    system, usage_pattern, user_journey, network, streaming_step, service, server, storage)

ROOT = os.path.dirname(os.path.abspath(__file__))


def return_class_str(input_obj):
    return str(input_obj.__class__).replace("<class '", "").replace("'>", "").split(".")[-1]


def obj_to_md(input_obj, attr_name):
    if attr_name == "name":
        return f"""### name\nA human readable description of the object."""
    elif issubclass(type(input_obj), ModelingObject):
        obj_class = return_class_str(input_obj)
        return f"### {attr_name}\nAn instance of [{obj_class}]({obj_class}.md)."
    elif issubclass(type(input_obj), ExplainableQuantity):
        return f"### {attr_name}\n{input_obj.label.lower()} in {input_obj.value.units}."
    elif type(input_obj) == list:
        if issubclass(type(input_obj[0]), ModelingObject):
            obj_class = return_class_str(input_obj[0])
            return f"### {attr_name}\nA list of [{obj_class}s]({obj_class}.md)."
        else:
            return "this shouldn’t happen"

    return f"### {attr_name}\ndescription to be done"


def calc_attr_to_md(input_obj: ExplainableObject, attr_name):
    return_str = f"### {attr_name}"
    if issubclass(type(input_obj), ExplainableQuantity):
        return_str += f"  \nExplainableQuantity in {input_obj.value.units}, representing the {input_obj.label.lower()}."
    elif issubclass(type(input_obj), ExplainableHourlyUsage):
        return_str += f"""  \nRepresentation of the evolution throughout a typical day of the {input_obj.label.lower()} by 24 values in {input_obj.value[0].units}."""

    formula_expl = "=".join(input_obj.explain().split("\n=\n")[:2])
    ancestor_md_link_list = [f'[{elt.label}]({return_class_str(elt.modeling_obj_container)}.md#{elt.attr_name_in_mod_obj_container})' for elt in input_obj.direct_ancestors_with_id]
    ancestor_md_links_list_formatted = "  \n- " + "\n- ".join(ancestor_md_link_list)
    return_str += f"  \n  \nDepends directly on:  \n{ancestor_md_links_list_formatted}  \n\nthrough the following calculations:  \n"

    if issubclass(type(input_obj), ExplainableObject):
        containing_obj_str = input_obj.modeling_obj_container.name.replace(" ", "_")
        calculus_graph_path = os.path.join(
            ROOT, "..", "mkdocs_sourcefiles", "calculus_graphs", f"{containing_obj_str}_{attr_name}.html")
        input_obj.calculus_graph_to_file(calculus_graph_path)
        calculus_graph_path_depth1 = os.path.join(
            ROOT, "..", "mkdocs_sourcefiles", "calculus_graphs_depth1", f"{containing_obj_str}_{attr_name}_depth1.html")
        input_obj.calculus_graph_to_file(calculus_graph_path_depth1, width="760px", height="300px", max_depth=1)

        md_calculus_graph_link_depth1 = calculus_graph_path_depth1.replace(
            os.path.join(ROOT, "..", "mkdocs_sourcefiles"), "docs_sources/mkdocs_sourcefiles")
        return_str += f'\n--8<-- "{md_calculus_graph_link_depth1}"\n'

        # The relative path starts with .. instead of . because it seems like mkdocs considers md files as html within a folder
        md_calculus_graph_link = calculus_graph_path.replace(os.path.join(ROOT, "..", "mkdocs_sourcefiles"), "..")
        return_str += f"  \nYou can also visit the <a href='{md_calculus_graph_link}' target='_blank'>link to {input_obj.label}’s full calculation graph</a>."

    return return_str


def generate_object_reference(automatically_update_yaml=False):
    country = usage_pattern.country
    device = usage_pattern.devices[0]

    nav_items = []
    for mod_obj in (
            system, usage_pattern, user_journey, country, device, network, streaming_step,
            streaming_step.jobs[0], service, server, storage):
        mod_obj_dict = {"class": return_class_str(mod_obj), "modeling_obj_containers": list(
            set([return_class_str(mod_obj) for mod_obj in mod_obj.modeling_obj_containers]))}

        init_sig_params = signature(mod_obj.__init__).parameters
        mod_obj_dict["params"] = []
        mod_obj_dict["calculated_attrs"] = []

        for key, elt in init_sig_params.items():
            if key != "self":
                # "type": str(elt).replace(f"{key}: ", "")
                mod_obj_dict["params"].append(obj_to_md(getattr(mod_obj, key), key))

        for attr in mod_obj.calculated_attributes:
            calc_attr = getattr(mod_obj, attr)
            mod_obj_dict["calculated_attrs"].append(calc_attr_to_md(calc_attr, attr))

        with open(os.path.join(ROOT, 'obj_template.md'), 'r') as file:
            template = Template(file.read(), trim_blocks=False)
        rendered_file = template.render(obj_dict=mod_obj_dict)

        filename = f"{mod_obj_dict['class']}.md"
        with open(os.path.join(ROOT, "..", "mkdocs_sourcefiles", f"{mod_obj_dict['class']}.md"), "w") as file:
            file.write(rendered_file)
        nav_items.append(filename)

    if automatically_update_yaml:
        yaml = ruamel.yaml.YAML()
        # yaml.preserve_quotes = True
        mkdocs_yml_filepath = os.path.join(ROOT, "..", "..", "mkdocs.yml")
        with open(mkdocs_yml_filepath, "r") as fp:
            data = yaml.load(fp)
        for filename in nav_items:
            write_filename = True
            for elt in data["nav"][2]["e-footprint objects reference"]:
                if filename.replace(".md", "") in elt.keys():
                    write_filename = False
            if write_filename:
                data["nav"][2]["e-footprint objects reference"].append({filename.replace(".md", ""): filename})
        with open(mkdocs_yml_filepath, "w") as fp:
            yaml.dump(data, fp)
