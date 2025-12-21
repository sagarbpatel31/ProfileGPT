from http.server import BaseHTTPRequestHandler
import json
import io
import tempfile
import os
from urllib.parse import parse_qs
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

class handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            content_type = self.headers.get("Content-Type", "")

            if not content_type.startswith("multipart/form-data"):
                self.send_json_response({"error": "Multipart form data required"}, 400)
                return

            post_data = self.rfile.read(content_length)

            # Simple multipart parsing for demo
            boundary = content_type.split("boundary=")[1].encode()
            parts = post_data.split(b"--" + boundary)

            file_content = None
            filename = None

            for part in parts:
                if b"Content-Disposition" in part and b"filename=" in part:
                    # Extract filename
                    lines = part.split(b"\r\n")
                    for line in lines:
                        if b"filename=" in line:
                            filename = line.decode().split('filename="')[1].split('"')[0]
                            break

                    # Extract file content (after double CRLF)
                    if b"\r\n\r\n" in part:
                        file_content = part.split(b"\r\n\r\n", 1)[1].rstrip(b"\r\n")

            if not file_content or not filename:
                self.send_json_response({"error": "No file uploaded"}, 400)
                return

            # Process the file content
            text_content = ""
            if filename.lower().endswith('.txt'):
                text_content = file_content.decode('utf-8', errors='ignore')
            elif filename.lower().endswith('.pdf'):
                text_content = f"PDF file '{filename}' received. Content extraction would require additional libraries in production."
            elif filename.lower().endswith('.docx'):
                text_content = f"DOCX file '{filename}' received. Content extraction would require additional libraries in production."
            else:
                text_content = f"File '{filename}' received. Type: {filename.split('.')[-1] if '.' in filename else 'unknown'}"

            # Generate a summary using OpenAI if available
            summary = "File uploaded successfully."
            if openai.api_key and len(text_content) > 50:
                try:
                    response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "Create a brief summary of this document content for a professional portfolio system."
                            },
                            {
                                "role": "user",
                                "content": text_content[:2000]  # Limit content for API
                            }
                        ],
                        max_tokens=100
                    )
                    summary = response.choices[0].message.content
                except:
                    summary = "File processed successfully."

            self.send_json_response({
                "message": "Document uploaded and processed successfully",
                "document": {
                    "id": f"doc-{hash(filename) % 10000}",
                    "title": filename,
                    "source_type": "uploaded",
                    "status": "processed",
                    "summary": summary,
                    "size": len(file_content)
                }
            })

        except Exception as e:
            self.send_json_response({"error": f"Upload error: {str(e)}"}, 500)

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())