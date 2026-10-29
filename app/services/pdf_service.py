
from pypdf import PdfReader
from io import BytesIO


def extract_text_from_pdf(pdf_file):
    """
    Extract text from an uploaded PDF file.

    Args:
        pdf_file: Uploaded PDF file or a file-like object.

    Returns:
        Extracted text as a string.
    """
    try:
        pdf_bytes = pdf_file.read()

        reader = PdfReader(BytesIO(pdf_bytes))

        if reader.is_encrypted:
            raise ValueError(
                "This PDF is password-protected. "
                "Please upload an unlocked PDF."
            )

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""

            if page_text.strip():
                extracted_pages.append(
                    f"--- Page {page_number} ---\n{page_text}"
                )

        full_text = "\n\n".join(extracted_pages)

        if not full_text.strip():
            raise ValueError(
                "No readable text found. "
                "This may be a scanned PDF."
            )

        return full_text

    except ValueError:
        raise

    except Exception as error:
        raise ValueError(
            f"Unable to read the PDF: {error}"
        ) from error
