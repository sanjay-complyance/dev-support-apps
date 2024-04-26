from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
import base64
import io
import qrcode
from pygments import highlight
from pygments.lexers import XmlLexer
from pygments.formatters import HtmlFormatter
import pdfplumber

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

class DecodeForm(FlaskForm):
    b64_string = TextAreaField('Enter your base64 encoded string:', validators=[DataRequired()])
    output_format = SelectField('Choose the output format:', choices=[('XML', 'XML'), ('PDF', 'PDF'), ('QR Code', 'QR Code')])
    submit = SubmitField('Decode')

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

@app.route('/', methods=['GET', 'POST'])
def index():
    form = DecodeForm()
    output = None
    if form.validate_on_submit():
        b64_string = form.b64_string.data
        option = form.output_format.data

        if option == 'XML':
            xml_content = decode_base64_to_file(b64_string, is_text=True)
            output = highlight_xml(xml_content)

        elif option == 'PDF':
            pdf_file = decode_base64_to_file(b64_string)
            pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
            output = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="600"></iframe>'

        elif option == 'QR Code':
            qr_code_img = qrcode.make(b64_string)
            img_buffer = io.BytesIO()
            qr_code_img.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            output = f'<img src="data:image/png;base64,{img_base64}" alt="QR Code" />'

    return render_template('index.html', form=form, output=output)

if __name__ == '__main__':
    app.run(debug=True)
