# Copyright (c) Opendatalab. All rights reserved.
import json
import os
from pathlib import Path

import asyncio
from dotenv import load_dotenv
from loguru import logger

from mineru.cli.common import (
    convert_pdf_bytes_to_bytes_by_pypdfium2,
    prepare_env,
    read_fn,
)
from mineru.data.data_reader_writer import FileBasedDataWriter
from mineru.utils.draw_bbox import draw_layout_bbox, draw_span_bbox
from mineru.utils.enum_class import MakeMode
from mineru.backend.vlm.vlm_analyze import doc_analyze as vlm_doc_analyze
from mineru.backend.vlm.vlm_middle_json_mkcontent import union_make as vlm_union_make

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "mineru",
#     "python-dotenv",
# ]
# ///


async def do_parse(
    output_dir,  # Output directory for storing parsing results
    pdf_file_name: str,  # Single PDF file name to be parsed
    pdf_bytes: bytes,  # Single PDF bytes to be parsed
    backend="vlm-sglang-client",  # The backend for parsing PDF, default is 'pipeline'
    server_url=None,  # Server URL for vlm-sglang-client backend
    f_draw_layout_bbox=True,  # Whether to draw layout bounding boxes
    f_draw_span_bbox=True,  # Whether to draw span bounding boxes
    f_dump_md=True,  # Whether to dump markdown files
    f_dump_middle_json=True,  # Whether to dump middle JSON files
    f_dump_model_output=True,  # Whether to dump model output files
    f_dump_orig_pdf=True,  # Whether to dump original PDF files
    f_dump_content_list=True,  # Whether to dump content list files
    f_make_md_mode=MakeMode.MM_MD,  # The mode for making markdown content, default is MM_MD
    start_page_id=0,  # Start page ID for parsing, default is 0
    end_page_id=None,  # End page ID for parsing, default is None (parse all pages until the end of the document)
):

    if backend.startswith("vlm-"):
        backend = backend[4:]

    f_draw_span_bbox = False
    parse_method = "vlm"

    pdf_bytes = await asyncio.to_thread(
        convert_pdf_bytes_to_bytes_by_pypdfium2, pdf_bytes, start_page_id, end_page_id
    )
    local_image_dir, local_md_dir = await asyncio.to_thread(
        prepare_env, output_dir, pdf_file_name, parse_method
    )
    image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(
        local_md_dir
    )
    middle_json, infer_result = await asyncio.to_thread(
        lambda: vlm_doc_analyze(
            pdf_bytes,
            image_writer=image_writer,
            backend=backend,
            server_url=server_url,
        )
    )

    pdf_info = middle_json["pdf_info"]

    if f_draw_layout_bbox:
        await asyncio.to_thread(
            draw_layout_bbox,
            pdf_info,
            pdf_bytes,
            local_md_dir,
            f"{pdf_file_name}_layout.pdf",
        )

    if f_draw_span_bbox:
        await asyncio.to_thread(
            draw_span_bbox,
            pdf_info,
            pdf_bytes,
            local_md_dir,
            f"{pdf_file_name}_span.pdf",
        )

    if f_dump_orig_pdf:
        await asyncio.to_thread(
            md_writer.write,
            f"{pdf_file_name}_origin.pdf",
            pdf_bytes,
        )

    if f_dump_md:
        image_dir = str(os.path.basename(local_image_dir))
        md_content_str = await asyncio.to_thread(
            vlm_union_make, pdf_info, f_make_md_mode, image_dir
        )
        await asyncio.to_thread(
            md_writer.write_string,
            f"{pdf_file_name}.md",
            md_content_str,
        )

    if f_dump_content_list:
        image_dir = str(os.path.basename(local_image_dir))
        content_list = await asyncio.to_thread(
            vlm_union_make, pdf_info, MakeMode.CONTENT_LIST, image_dir
        )
        await asyncio.to_thread(
            md_writer.write_string,
            f"{pdf_file_name}_content_list.json",
            json.dumps(content_list, ensure_ascii=False, indent=4),
        )

    if f_dump_middle_json:
        await asyncio.to_thread(
            md_writer.write_string,
            f"{pdf_file_name}_middle.json",
            json.dumps(middle_json, ensure_ascii=False, indent=4),
        )

    if f_dump_model_output:
        model_output = ("\n" + "-" * 50 + "\n").join(infer_result)
        await asyncio.to_thread(
            md_writer.write_string,
            f"{pdf_file_name}_model_output.txt",
            model_output,
        )

    logger.info(f"local output dir is {local_md_dir}")


async def parse_doc(
    path_list: list[Path],
    output_dir,
    backend="vlm-sglang-client",
    server_url=None,
    start_page_id=0,
    end_page_id=None,
):
    """
    Parameter description:
    path_list: List of document paths to be parsed, can be PDF or image files.
    output_dir: Output directory for storing parsing results.
    lang: Language option, default is 'ch', optional values include['ch', 'ch_server', 'ch_lite', 'en', 'korean', 'japan', 'chinese_cht', 'ta', 'te', 'ka']。
        Input the languages in the pdf (if known) to improve OCR accuracy.  Optional.
        Adapted only for the case where the backend is set to "pipeline"
    backend: the backend for parsing pdf:
        pipeline: More general.
        vlm-transformers: More general.
        vlm-sglang-engine: Faster(engine).
        vlm-sglang-client: Faster(client).
        without method specified, pipeline will be used by default.
    method: the method for parsing pdf:
        auto: Automatically determine the method based on the file type.
        txt: Use text extraction method.
        ocr: Use OCR method for image-based PDFs.
        Without method specified, 'auto' will be used by default.
        Adapted only for the case where the backend is set to "pipeline".
    server_url: When the backend is `sglang-client`, you need to specify the server_url, for example:`http://127.0.0.1:30000`
    start_page_id: Start page ID for parsing, default is 0
    end_page_id: End page ID for parsing, default is None (parse all pages until the end of the document)
    """
    try:
        for path in path_list:
            file_name = str(Path(path).stem)
            pdf_bytes = await asyncio.to_thread(read_fn, path)
            await do_parse(
                output_dir=output_dir,
                pdf_file_name=file_name,
                pdf_bytes=pdf_bytes,
                backend=backend,
                server_url=server_url,
                start_page_id=start_page_id,
                end_page_id=end_page_id,
            )
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # args
    __dir__ = os.path.dirname(os.path.abspath(__file__))
    pdf_files_dir = os.path.join(__dir__, "pdfs")
    output_dir = os.path.join(__dir__, "output")
    pdf_suffixes = [".pdf"]
    image_suffixes = [".png", ".jpeg", ".jpg"]

    # Get server URL from environment variable
    server_url = os.getenv("SGLANG_SERVER", "http://127.0.0.1:30000")
    logger.info(f"server_url: {server_url}")

    doc_path_list = []
    for doc_path in Path(pdf_files_dir).glob("*"):
        if doc_path.suffix in pdf_suffixes + image_suffixes:
            doc_path_list.append(doc_path)
    asyncio.run(
        parse_doc(
            doc_path_list,
            output_dir,
            backend="vlm-sglang-client",
            server_url=server_url,
        )
    )

    """To enable VLM mode, change the backend to 'vlm-xxx'"""
    # parse_doc(doc_path_list, output_dir, backend="vlm-transformers")  # more general.
    # parse_doc(doc_path_list, output_dir, backend="vlm-sglang-engine")  # faster(engine).
    # parse_doc(doc_path_list, output_dir, backend="vlm-sglang-client", server_url="http://127.0.0.1:30000")  # faster(client).
