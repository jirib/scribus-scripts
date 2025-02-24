#!/usr/bin/env python3

"""
This Scribus script loads metadata.yaml from the same directory as the Scribus
document and updates the newly create Scribus document based on a template;
that is, it updates specific text frames (named as keys in the YAML file) with
the values of the YAML keys.

That is, if the YAML file has 'title' key, it would find 'title' frame in
Scribus, and update its text with 'title' key value, plus it would "reset" the
frame style to key name prefixed with 'lang' (if applicable), key name and
finally applying back the its current style (note that this text replace
removes the current formatting, thus the styles are used).

An example for such a YAML file:

---%>---
lang: cs
title: "Hello world!"
subtitle: "A stupid introduction\u2028to using Scribus with Python"
date: Březen 2025
number: 1
series: HOWTOs for dummies
---%<---

"""

import scribus
import os
import yaml

metadata_file = "metadata.yaml"

# these keys MUST be present in the metadata.yaml file
mandatory_keys = {'title', 'date', 'series'}

# these metadata keys are not paragraphs, so apply only character style
character_style_keys = {'date', 'series'}


def update_document(sla_dir, metadata_file):
    # Open the YAML file "metadata"
    metadata_path = os.path.join(sla_dir, metadata_file)

    try:
        with open(metadata_path, 'r') as stream:
            metadata = yaml.safe_load(stream)
    except IOError:
        scribus.messageBox("Error", f'File "{metadata_path}" not found',
                           scribus.ICON_WARNING)
        return 1

    # validate provided metadata
    if not mandatory_keys <= metadata.keys():
        scribus.messageBox(
            "Error",
            f'File "{metadata_path}" does not have all mandatory keys: '
            f'{mandatory_keys}. Update the file.',
            scribus.ICON_WARNING
        )
        return 1

    lang = metadata['lang'] if 'lang' in metadata else None

    all_objects = scribus.getAllObjects()

    for frame_name, value in metadata.items():
        text = str(value)
        if frame_name in all_objects:
            style_type = 'Character' if frame_name in character_style_keys \
                else 'Paragraph'

            if 'Character' in style_type:
                current_style = scribus.getCharacterStyle(frame_name) \
                    or 'Default Character Style'
            else:
                current_style = scribus.getParagraphStyle(frame_name) \
                    or 'Default Paragraph Style'

            scribus.setText(text, frame_name)
            scribus.statusMessage(
                f'Text frame "{frame_name}" updated successfully.'
            )

            available_styles = getattr(
                scribus,
                'getCharStyles' if 'Character' in style_type
                else f'get{style_type}Styles'
            )()

            try_styles = []
            if lang:
                try_styles.append(f'{lang}--{frame_name}')
            try_styles.append(frame_name)

            valid_styles = [s for s in try_styles if s in available_styles]
            valid_styles.append(current_style)  # fallback

            for style in valid_styles:
                print(
                    f'Frame name "{frame_name}"',
                    f'style_type: "{style_type}", style: "{style}"'
                )
                try:
                    getattr(
                        scribus,
                        f'set{style_type}Style'
                    )(style, frame_name)
                except scribus.NotFoundError:
                    pass
                else:
                    break

        else:
            scribus.statusMessage(f'Text frame "{frame_name}" does not exist.')

        scribus.statusMessage('Finished updating text frame.')


if __name__ == '__main__':
    scribus.statusMessage('Script started.')

    if scribus.haveDoc():
        sla_path = scribus.getDocName()
        if sla_path:
            sla_dir = os.path.dirname(sla_path)
            update_document(sla_dir, metadata_file)
        else:
            scribus.messageBox(
                "Error",
                "The document hasn't been saved yet. Save it first.",
                scribus.ICON_WARNING
            )
    else:
        scribus.messageBox(
            "Error",
            "No document is open",
            scribus.ICON_WARNING
        )
