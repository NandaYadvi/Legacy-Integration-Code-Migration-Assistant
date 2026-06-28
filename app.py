"""
Gradio UI for Actian → MuleSoft RAG Converter

Run:
    python app.py
"""

import os
import socket
import time
from pathlib import Path

import gradio as gr

from rag_pipeline import generate_mule_flow


# --------------------------------------------------------
# Output Directory
# --------------------------------------------------------

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# --------------------------------------------------------
# Conversion Function
# --------------------------------------------------------

def convert_actian_to_mule(actian_xml: str):
    """Convert Actian XML into MuleSoft XML using the RAG pipeline."""

    if not actian_xml.strip():
        yield "", None, "⚠️ Please paste your Actian XML before clicking Convert."
        return

    yield "", None, "📘 Reading XML..."
    time.sleep(0.15)

    yield "", None, "🔎 Searching MongoDB..."
    time.sleep(0.15)

    yield "", None, "🧠 Retrieving similar examples..."
    time.sleep(0.15)

    yield "", None, "⚙️ Generating MuleSoft XML..."

    try:
        mule_output = generate_mule_flow(actian_xml)
        output_file = OUTPUT_DIR / "mule_output.xml"

        with open(output_file, "w", encoding="utf-8") as file_handle:
            file_handle.write(mule_output)

        yield mule_output, str(output_file), "✅ Done."

    except Exception as exception:
        yield "", None, f"❌ Error:\n\n{exception}"


# --------------------------------------------------------
# Port Helper
# --------------------------------------------------------

def get_available_port(start_port: int = 7860, max_attempts: int = 20) -> int:
    """Return the first free local port starting from start_port."""

    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue

    return start_port


# --------------------------------------------------------
# Gradio Interface
# --------------------------------------------------------

with gr.Blocks(title="🚀 AI-Powered Actian → MuleSoft Converter") as demo:

    gr.Markdown(
        """
# 🚀 AI-Powered Actian → MuleSoft Converter

Convert legacy **Actian DataConnect XML** into **production-ready MuleSoft 4 XML** using Retrieval-Augmented Generation (RAG).
"""
    )

    gr.HTML(
        """
<div style="background: #F5F7FA; border: 1px solid #D1D5DB; border-radius: 18px; padding: 24px 28px; margin: 0.5rem 0 1rem; box-shadow: 0 2px 8px rgba(17, 24, 39, 0.05);">
  <div style="font-size: 26px; font-weight: 700; color: #1F2937; margin-bottom: 14px;">🖥️ System Overview</div>
  <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 18px; font-size: 15px; color: #111827;">
    <div><div style="font-size: 16px; font-weight: 600; color: #1F2937;">📁 Training Projects</div><div style="color: #4B5563; margin-top: 2px;">10</div></div>
    <div><div style="font-size: 16px; font-weight: 600; color: #1F2937;">🧩 Training Chunks</div><div style="color: #4B5563; margin-top: 2px;">569</div></div>
    <div><div style="font-size: 16px; font-weight: 600; color: #1F2937;">🤗 Embedding Model</div><div style="color: #4B5563; margin-top: 2px;">all-MiniLM-L6-v2</div></div>
    <div><div style="font-size: 16px; font-weight: 600; color: #1F2937;">🗄 Vector Database</div><div style="color: #4B5563; margin-top: 2px;">MongoDB Atlas</div></div>
    <div><div style="font-size: 16px; font-weight: 600; color: #1F2937;">🧠 LLM</div><div style="color: #4B5563; margin-top: 2px;">Gemini 2.5 Flash</div></div>
    <div><div style="font-size: 16px; font-weight: 600; color: #1F2937;">🔗 Framework</div><div style="color: #4B5563; margin-top: 2px;">LangChain + RAG</div></div>
  </div>
  <div style="height: 1px; background: #E5E7EB; margin: 14px 0 12px;"></div>
  <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 16px; font-size: 14px; color: #4B5563;">
    <div>
      <div style="font-size: 15px; font-weight: 600; color: #1F2937; margin-bottom: 6px;">📂 Supported Connectors</div>
      <div style="color: #4B5563; margin-top: 2px;">• Database</div>
      <div style="color: #4B5563; margin-top: 2px;">• File</div>
      <div style="color: #4B5563; margin-top: 2px;">• FTP</div>
      <div style="color: #4B5563; margin-top: 2px;">• SMTP</div>
      <div style="color: #4B5563; margin-top: 2px;">• REST APIs</div>
    </div>
    <div>
      <div style="font-size: 15px; font-weight: 600; color: #1F2937; margin-bottom: 6px;">🎯 Features</div>
      <div style="color: #4B5563; margin-top: 2px;">• XML Parsing</div>
      <div style="color: #4B5563; margin-top: 2px;">• Retrieval-Augmented Generation</div>
      <div style="color: #4B5563; margin-top: 2px;">• Semantic Search</div>
      <div style="color: #4B5563; margin-top: 2px;">• Context-aware Conversion</div>
      <div style="color: #4B5563; margin-top: 2px;">• Production-ready Mule XML</div>
      <div style="color: #4B5563; margin-top: 2px;">• Download XML</div>
    </div>
  </div>
</div>
"""
    )

    gr.HTML("<div style='height: 0.4rem;'></div>")

    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            actian_input = gr.Textbox(
                label="Actian XML",
                lines=24,
                placeholder="Paste your Actian DataConnect XML here...",
            )

        with gr.Column(scale=1):
            mule_output = gr.Code(
                language="html",
                label="Generated MuleSoft XML",
                lines=24,
            )
            download_file = gr.File(label="Download XML")

    gr.HTML("<div style='height: 0.8rem;'></div>")

    with gr.Row():
        convert_btn = gr.Button(
            "⚡ Convert to MuleSoft",
            variant="primary",
            size="lg",
        )

    gr.HTML("<div style='height: 0.6rem;'></div>")

    status_text = gr.Textbox(label="Status", interactive=False, lines=1)

    gr.HTML("<div style='height: 0.5rem;'></div>")

    gr.Markdown("### Example Inputs")
    examples = gr.Examples(
        examples=[
            [
                "<Request>\n  <Type>ClientDataExtract</Type>\n  <ClientId>12345</ClientId>\n</Request>"
            ],
            [
                "<Request>\n  <Type>PayrollExport</Type>\n  <Period>2024-08</Period>\n  <Department>Finance</Department>\n</Request>"
            ],
            [
                "<Request>\n  <Type>CustomerSync</Type>\n  <Customer>Acme Corp</Customer>\n</Request>"
            ],
            [
                "<Request>\n  <Type>FileProcessing</Type>\n  <FileName>data_extract.xml</FileName>\n</Request>"
            ],
        ],
        inputs=[actian_input],
        examples_per_page=4,
        label="Example Inputs",
    )

    gr.HTML("<div style='height: 0.8rem;'></div>")

    convert_btn.click(
        fn=convert_actian_to_mule,
        inputs=actian_input,
        outputs=[mule_output, download_file, status_text],
        show_progress=True,
    )

    gr.Markdown(
        """
<div align="center" style="font-size: 0.9rem; color: #64748b; padding-top: 0.6rem;">
Built with ❤️ using<br>
🤗 HuggingFace • 🗄 MongoDB Atlas • 🧠 Gemini • 🔗 LangChain • ⚡ Gradio
</div>
"""
    )


# --------------------------------------------------------
# Launch
# --------------------------------------------------------

if __name__ == "__main__":
    requested_port = os.environ.get("GRADIO_SERVER_PORT")
    server_port = int(requested_port) if requested_port else get_available_port()

    demo.launch(
        server_name="127.0.0.1",
        server_port=server_port,
        share=False,
        theme=gr.themes.Soft(),
    )
