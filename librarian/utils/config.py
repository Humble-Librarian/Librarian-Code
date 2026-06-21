from dotenv import load_dotenv
import os
import warnings

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
warnings.filterwarnings("ignore", module="huggingface_hub")
warnings.filterwarnings("ignore", module="sentence_transformers")

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", ".librarian/memory")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")


def _load_toml_defaults():
    try:
        from librarian.utils.toml_config import get_config_value
        return get_config_value("model", EMBED_MODEL)
    except Exception:
        return EMBED_MODEL


EMBED_MODEL = _load_toml_defaults()
