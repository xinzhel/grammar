from typing import (
    Dict,
    Tuple,
    List
)
import logging
from spacy.language import Language as SpacyModelType
import spacy
from spacy.cli.download import download as spacy_download
logger = logging.getLogger(__name__)

LOADED_SPACY_MODELS: Dict[Tuple[str, bool, bool, bool], SpacyModelType] = {}
def get_spacy_model(
    spacy_model_name: str="en_core_web_sm", pos_tags: bool = True, parse: bool = False, ner: bool = False
) -> SpacyModelType:
    """
    In order to avoid loading spacy models a whole bunch of times, we'll save references to them,
    keyed by the options we used to create the spacy model, so any particular configuration only
    gets loaded once.
    """

    options = (spacy_model_name, pos_tags, parse, ner)
    if options not in LOADED_SPACY_MODELS:
        disable = ["vectors", "textcat"]
        if not pos_tags:
            disable.append("tagger")
        if not parse:
            disable.append("parser")
        if not ner:
            disable.append("ner")
        try:
            spacy_model = spacy.load(spacy_model_name, disable=disable)
        except OSError:
            logger.warning(
                f"Spacy models '{spacy_model_name}' not found.  Downloading and installing."
            )
            spacy_download(spacy_model_name)

            # Import the downloaded model module directly and load from there
            spacy_model_module = __import__(spacy_model_name)
            spacy_model = spacy_model_module.load(disable=disable)  # type: ignore

        LOADED_SPACY_MODELS[options] = spacy_model
    return LOADED_SPACY_MODELS[options]

def _remove_spaces(tokens: List[spacy.tokens.Token]) -> List[spacy.tokens.Token]:
    return [token for token in tokens if not token.is_space]

class SpacyTokenizer:
    def __init__(self, spacy_model_name: str="en_core_web_sm", pos_tags: bool = True, parse: bool = False, ner: bool = False):
        self.spacy = get_spacy_model(spacy_model_name, pos_tags, parse, ner)

    def tokenize(self, text: str) -> List[str]:
        return [token.text for token in _remove_spaces(self.spacy(text))]