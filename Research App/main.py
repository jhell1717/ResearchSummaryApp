from openai import OpenAI

client = OpenAI(api_key="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")
from fasthtml.common import *
from pypdf import PdfReader


app, rt = fast_app(live=True, hdrs=(Style("""
    body {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        height: 100vh;
        background-color: #fff6ea;
        margin: 0;
    }
    button {
        background-color: #499fa4;  /* Matching your theme color */
        color: #fff6ea;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
    }
    button:hover {
        background-color: #3a8186;  /* Slightly darker shade for hover effect */
    }
    .logo {
        margin-bottom: 20px;
    }
    .center-content {
        text-align: center;
        margin-bottom: 20px;
    }
    .upload-box {
        width: 400px;
        padding: 20px;
        border: 2px dashed #499fa4;
        border-radius: 10px;
        background-color: #ffffff;
        text-align: center;
        cursor: pointer;
    }
    input[type="file"], input[type="text"] {
        margin-bottom: 10px;
        padding: 10px;
        border: 1px solid #499fa4;
        border-radius: 5px;
        font-size: 16px;
        width: 95%;
    }
    .custom-upload-label {
        display: block;
        color: #499fa4;
        font-size: 16px;
    }
    .upload-button {
        background-color: #499fa4; /* Custom background color */
        color: #ffffff;            /* Text color */
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
    }
    table {
        border-collapse: collapse;
        margin: 20px auto;
        width: 80%;
        text-align: left;
    }
    table, th, td {
        border: 1px solid #499fa4;
    }
    th, td {
        padding: 10px;
    }
    th {
        background-color: #499fa4;
        color: white;
    }
    .upload-button:hover {
        background-color: #3b828b; /* Darker shade on hover */
"""), Script("""
    document.addEventListener('dragover', function(event) {
        event.preventDefault();
    });
    document.addEventListener('drop', function(event) {
        event.preventDefault();
    });
""")))

upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)

import pdfplumber

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                try:
                    text += page.extract_text() or ""
                except Exception as e:
                    print(f"Error reading page: {e}")
                    continue
            if not text.strip():
                return "No readable text found in the PDF. The file might be scanned or image-based."
            return text.strip()
    except Exception as e:
        return f"Error extracting text from PDF: {e}"

def analyze_text_with_openai(text, topics):
    results = {}
    for topic in topics:
        if topic.strip():
            prompt = f"Analyze the following research paper and extract key points related to the theme '{topic}':\n\n{text[:2000]}. Output format should be concise bullet points focusing only on the specified areas of interest. If the paper does not mention the key topic, notify the user of this and do not provide opinions or information on the topic."
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that analyses research papers for information relating to specific topics."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.7
                )
                # Updated way to access the message content
                message = response.choices[0].message.content
                results[topic] = message.strip()
            except Exception as e:
                results[topic] = f"Error: {e}"
        else:
            results[topic] = "No theme provided."
    return results


@rt("/")
def get():
    return Div(
        Div(
            Img(src="Research App/static/logo.png", alt="Logo", cls="logo", style="width: 350px; display: block; margin: 0 auto;"),
            cls='center-content'
        ),
        Form(method="post", enctype="multipart/form-data", action="/analyze")(
            Div(
                Label("Drag and drop your PDF here or click to upload", cls="custom-upload-label", **{"for": "pdf_upload"}),
                Input(type="file", name="pdf_file", id="pdf_upload", accept=".pdf"),
                cls="upload-box"
            ),
            Div(
                Input(type="text", name="theme1", placeholder="Enter Theme 1"),
                Input(type="text", name="theme2", placeholder="Enter Theme 2"),
                Input(type="text", name="theme3", placeholder="Enter Theme 3")
            ),
            Button("Analyze", type="submit", cls="upload-button")
        )
    )

# Route for analysis
@rt("/analyze", methods=["POST"])
async def analyze(pdf_file: UploadFile, theme1: str = "", theme2: str = "", theme3: str = ""):
    file_path = upload_dir / pdf_file.filename
    content = await pdf_file.read()
    file_path.write_bytes(content)

    text = extract_text_from_pdf(file_path)
    topics = [theme1.strip(), theme2.strip(), theme3.strip()]

    if text:
        analysis_results = analyze_text_with_openai(text, topics)
        table_rows = [
            Tr(Td(topic), Td(result)) for topic, result in analysis_results.items()
        ]
        return Div(
            Titled("Analysis Results",
                   Table(
                       Tr(Th("Theme"), Th("Key Points")),
                       *table_rows
                   )
            )
        )
    else:
        return Titled("Error", P("Failed to extract text from the PDF. Please try another file."))




serve()

