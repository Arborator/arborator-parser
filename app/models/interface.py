from typing import Literal, TypedDict


class ParsingSettings_t(TypedDict):
    keep_upos: Literal["NONE", "EXISTING", "ALL"]
    keep_feats: Literal["NONE", "EXISTING", "ALL"]
    keep_xpos: Literal["NONE", "EXISTING", "ALL"]
    keep_heads: Literal["NONE", "EXISTING", "ALL"]
    keep_deprels: Literal["NONE", "EXISTING", "ALL"]
    keep_lemmas: Literal["NONE", "EXISTING", "ALL"]
