"""
Gloss preprocessing for arborator-parser integration.

When the gloss parser model is selected, CoNLL-U files need FORM<->Gloss swapping:
- Before parsing: move FORM -> OrigForm in MISC, move Gloss -> FORM
- After parsing:  restore OrigForm -> FORM, move FORM -> Gloss in MISC
"""

import re


def swap_gloss_to_form(conllu_str: str) -> str:
    """Pre-processing: Replace FORM with Gloss value from MISC.

    For each token line:
    - If MISC contains Gloss=X: store original FORM as OrigForm=FORM in MISC,
      set FORM=X, remove Gloss= from MISC
    - If no Gloss= in MISC: keep FORM unchanged

    Skips comment lines and multiword/empty tokens.
    """
    lines = conllu_str.split('\n')
    out = []
    for line in lines:
        if not line or line.startswith('#'):
            out.append(line)
            continue
        fields = line.split('\t')
        if len(fields) != 10:
            out.append(line)
            continue
        tok_id = fields[0]
        if '-' in tok_id or '.' in tok_id:
            out.append(line)
            continue

        form = fields[1]
        misc = fields[9]

        # Extract Gloss= from MISC
        gloss = None
        m = re.search(r'(?:^|\|)Gloss=([^|]+)', misc)
        if m:
            gloss = m.group(1)

        if gloss and gloss != '_':
            # Normalize: strip leading =, take first comma-separated value
            gloss = gloss.lstrip('=')
            if ',' in gloss:
                gloss = gloss.split(',')[0]
            gloss = gloss.replace(' ', '_').strip()

            if gloss:
                # Store original form
                if misc == '_' or not misc:
                    new_misc = f'OrigForm={form}'
                else:
                    new_misc = f'{misc}|OrigForm={form}'
                # Remove Gloss= from MISC
                parts = [p for p in new_misc.split('|') if not p.startswith('Gloss=')]
                new_misc = '|'.join(parts) if parts else '_'

                fields[1] = gloss
                fields[9] = new_misc

        out.append('\t'.join(fields))
    return '\n'.join(out)


def swap_form_to_gloss(conllu_str: str) -> str:
    """Post-processing: Restore original FORM and put predicted parse back.

    For each token line:
    - If MISC contains OrigForm=X: restore FORM=X, store current FORM as Gloss= in MISC,
      remove OrigForm= from MISC
    - If no OrigForm= in MISC: keep as-is (token had no gloss)

    The HEAD, DEPREL, UPOS, etc. predicted by the parser are left intact.
    """
    lines = conllu_str.split('\n')
    out = []
    for line in lines:
        if not line or line.startswith('#'):
            out.append(line)
            continue
        fields = line.split('\t')
        if len(fields) != 10:
            out.append(line)
            continue
        tok_id = fields[0]
        if '-' in tok_id or '.' in tok_id:
            out.append(line)
            continue

        current_form = fields[1]  # This is still the gloss (parser doesn't change FORM)
        misc = fields[9]

        # Extract OrigForm= from MISC
        m = re.search(r'(?:^|\|)OrigForm=([^|]+)', misc)
        if m:
            orig_form = m.group(1)
            # Restore original form
            fields[1] = orig_form
            # Put gloss back in MISC
            parts = [p for p in misc.split('|') if not p.startswith('OrigForm=')]
            parts.append(f'Gloss={current_form}')
            fields[9] = '|'.join(parts) if parts else '_'

        out.append('\t'.join(fields))
    return '\n'.join(out)


def is_gloss_model(project_name: str) -> bool:
    """Check if a model is a gloss parser model by its project name."""
    return project_name.lower().startswith('gloss_')
