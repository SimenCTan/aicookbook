# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "extractous",
#     "python-dotenv",
#     "loguru",
# ]
# ///

import os
import json
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

try:
    from extractous import Extractor
except Exception as e:  # pragma: no cover
    Extractor = None
    _import_error = e


def ensure_output_dirs(base_output_dir: str, pdf_stem: str) -> tuple[str, str]:
    extractous_dir = os.path.join(base_output_dir, pdf_stem, "extractous")
    os.makedirs(extractous_dir, exist_ok=True)
    return extractous_dir, extractous_dir


def extract_pdf_with_extractous(
    pdf_path: Path, output_dir: str, max_len: int | None = None
) -> None:
    if Extractor is None:
        raise RuntimeError(f"extractous is not available: {_import_error}")

    extractor = Extractor()
    if max_len is not None:
        try:
            extractor.set_extract_string_max_length(max_len)
        except Exception:
            pass

    text, metadata = extractor.extract_file_to_string(str(pdf_path))

    extractous_dir, _ = ensure_output_dirs(output_dir, pdf_path.stem)

    text_path = os.path.join(extractous_dir, f"{pdf_path.stem}.txt")
    meta_path = os.path.join(extractous_dir, f"{pdf_path.stem}_metadata.json")

    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text or "")

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata or {}, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved text to {text_path}")
    logger.info(f"Saved metadata to {meta_path}")


if __name__ == "__main__":
    load_dotenv()

    __dir__ = os.path.dirname(os.path.abspath(__file__))
    pdf_files_dir = os.path.join(__dir__, "pdfs")
    output_dir = os.path.join(__dir__, "output")

    pdf_suffixes = [".pdf"]

    if Extractor is None:
        raise SystemExit(
            f"Please install extractous first: pip install extractous\nReason: {_import_error}"
        )

    doc_path_list: list[Path] = []
    for doc_path in Path(pdf_files_dir).glob("*"):
        if doc_path.suffix.lower() in pdf_suffixes:
            doc_path_list.append(doc_path)

    if not doc_path_list:
        logger.warning(f"No PDF files found in {pdf_files_dir}")

    for pdf_path in doc_path_list:
        logger.info(f"Extracting with Extractous: {pdf_path}")
        extract_pdf_with_extractous(pdf_path, output_dir, max_len=None)
