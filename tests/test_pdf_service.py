
from io import BytesIO

from pypdf import PdfWriter
from app.services.pdf_service import extract_text_from_pdf


def create_test_pdf():
    pdf_buffer = BytesIO()

    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)

    # Add a content stream containing a small text example.
    from pypdf.generic import DecodedStreamObject, NameObject

    stream = DecodedStreamObject()
    stream.set_data(
        b"BT /F1 12 Tf 40 200 Td (Hello StudyMate) Tj ET"
    )

    # A manually created stream without font resources may not
    # be extractable across PDF readers. Use the app with a real
    # PDF for the initial verification instead.
    writer.write(pdf_buffer)
    pdf_buffer.seek(0)

    return pdf_buffer


if __name__ == "__main__":
    print("PDF service imported successfully.")
    print("Next, test using a real text-based PDF in the app.")
