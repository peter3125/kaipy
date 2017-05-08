import logging
import kai.res
import os
import xml.etree.ElementTree

aim_set = dict()


# add a new aiml pattern
def add_pattern(pattern_list, template_list, aiml_name: str):
    if len(pattern_list) > 0 and len(template_list) > 0 and len(aiml_name) > 0:
        pass

# process all AIML files
for aiml_file in kai.res.directory_content('aiml'):
    aiml_name = str(os.path.basename(aiml_file).split('.')[0])
    try:
        e = xml.etree.ElementTree.parse(aiml_file).getroot()
        for category in e.findall('category'):
            pattern_list = []
            for pattern in category.findall('pattern'):
                pattern_list.append(pattern.text)
            template_list = []
            for template in category.findall('template'):
                template_list.append(template.text)
            add_pattern(pattern_list, template_list, aiml_name)
    except:
        pass
