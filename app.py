import streamlit as st
import base64
import pdfplumber
import io
import qrcode
from pygments import highlight
from pygments.lexers import XmlLexer
from pygments.formatters import HtmlFormatter

# Function to decode Base64 to a file
def decode_base64_to_file(b64_content, is_text=False):
    decoded_data = base64.b64decode(b64_content)
    if is_text:
        return decoded_data.decode('utf-8')
    else:
        return io.BytesIO(decoded_data)

def highlight_xml(xml_content):
    formatter = HtmlFormatter(style="friendly", full=True, cssclass="codehilite")
    highlighted_xml = highlight(xml_content, XmlLexer(), formatter)
    style = "<style>" + formatter.get_style_defs() + "</style>"
    return style + highlighted_xml

st.title('Base64 Decoder App')

b64_string = st.text_area("Enter your base64 encoded string here:")
option = st.selectbox("Choose the output format:", ['XML', 'PDF', 'QR Code'])
decode_button = st.button("Decode")
download_data = ""

if decode_button and b64_string:
    if option == 'XML':
        try:
            xml_content = decode_base64_to_file(b64_string, is_text=True)
            highlighted_xml = highlight_xml(xml_content)
            st.markdown(highlighted_xml, unsafe_allow_html=True)
            download_data = xml_content.encode('utf-8')
        except Exception as e:
            st.error(f"An error occurred: {e}")
    
    elif option == 'PDF':
        try:
            pdf_file = decode_base64_to_file(b64_string)
            base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            download_data = pdf_file.getvalue()
        except Exception as e:
            st.error(f"An error occurred: {e}")

    elif option == 'QR Code':
        try:
            qr_code_img = qrcode.make(b64_string)
            img_buffer = io.BytesIO()
            qr_code_img.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            b64_img = base64.b64encode(img_buffer.getvalue()).decode()
            qr_code_display = f'<img src="data:image/png;base64,{b64_img}" />'
            st.markdown(qr_code_display, unsafe_allow_html=True)
            download_data = img_buffer.getvalue()
        except Exception as e:
            st.error(f"An error occurred while generating the QR Code: {e}")

    # Offer a download button
    st.download_button(label="Download File",
                       data=download_data,
                       file_name=f"decoded.{option.lower()}")


# Custom CSS for XML syntax highlighting
st.markdown("""
    <style>
    .codehilite {
        overflow: auto;
        max-height: 400px;
        margin: 0.5em 0;
        border-radius: 0.5em;
        background-color: #f6f8fa;
    }
    </style>
    """, unsafe_allow_html=True)
