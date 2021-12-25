import os
import jinja2
import yaml
from yaml import Loader


with open(os.path.join("jinja/templates.yml"), "r", encoding="utf-8") as f:
    template_list = yaml.load(f, Loader=Loader)
for template_info in template_list:
    with open(
        os.path.join("jinja", template_info["template"]), "r", encoding="utf-8"
    ) as f:
        template = jinja2.Template(f.read())
    with open(os.path.join("jinja", template_info["vars"]), "r", encoding="utf-8") as f:
        template_vars = yaml.load(f, Loader=Loader)
    for instance_vars in template_vars:
        instance = template.render(**instance_vars)
        output_path = instance_vars["output_path"]
        parent = os.path.dirname(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(instance_vars["output_path"], "w", encoding="utf-8") as f:
            f.write(instance)
