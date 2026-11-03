import base64
import email
import json
import re
import time
import urllib.request

from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from prompts import (
    SECTION_EXTRACTION_PROMPT,
    SECTION_ANALYSIS_PROMPT,
    FINAL_SELECTION_PROMPT
)


# ============================================================
# OLLAMA
# ============================================================
# ============================================================
# OLLAMA
# ============================================================

def ask_ollama(prompt, output_schema):

    data = {
        "model": "qwen3:4b",
        "prompt": prompt,
        "stream": False,
        "format": output_schema,
        "options": {
            "temperature": 0.1,
            "num_predict": 4000
        }
    }

    request = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=180
    ) as response:

        result = json.loads(
            response.read().decode("utf-8")
        )

    return result.get("response", "").strip()

# ============================================================
# JSON SCHEMAS
# ============================================================

SECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "section_name": {
                        "type": "string"
                    },
                    "content": {
                        "type": "string"
                    }
                },
                "required": [
                    "section_name",
                    "content"
                ]
            }
        }
    },
    "required": [
        "sections"
    ]
}


SECTION_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "section_name": {
            "type": "string"
        },
        "topics": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string"
                    },
                    "importance": {
                        "type": "string",
                        "enum": [
                            "High",
                            "Medium",
                            "Low"
                        ]
                    },
                    "engagement_potential": {
                        "type": "string",
                        "enum": [
                            "High",
                            "Medium",
                            "Low"
                        ]
                    },
                    "what_happened": {
                        "type": "string"
                    },
                    "important_details": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "summary_hinglish": {
                        "type": "string"
                    },
                    "why_it_matters": {
                        "type": "string"
                    },
                    "why_engaging": {
                        "type": "string"
                    }
                },
                "required": [
                    "topic",
                    "importance",
                    "engagement_potential",
                    "what_happened",
                    "important_details",
                    "summary_hinglish",
                    "why_it_matters",
                    "why_engaging"
                ]
            }
        }
    },
    "required": [
        "section_name",
        "topics"
    ]
}


FINAL_SCHEMA = {
    "type": "object",
    "properties": {
        "topics": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string"
                    },
                    "importance": {
                        "type": "string",
                        "enum": [
                            "High",
                            "Medium",
                            "Low"
                        ]
                    },
                    "engagement_potential": {
                        "type": "string",
                        "enum": [
                            "High",
                            "Medium",
                            "Low"
                        ]
                    },
                    "what_happened": {
                        "type": "string"
                    },
                    "important_details": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "summary_hinglish": {
                        "type": "string"
                    },
                    "why_it_matters": {
                        "type": "string"
                    },
                    "why_engaging": {
                        "type": "string"
                    }
                },
                "required": [
                    "topic",
                    "importance",
                    "engagement_potential",
                    "what_happened",
                    "important_details",
                    "summary_hinglish",
                    "why_it_matters",
                    "why_engaging"
                ]
            }
        },

        "content_opportunities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string"
                    },
                    "reason": {
                        "type": "string"
                    },
                    "best_content_angle": {
                        "type": "string"
                    },
                    "hooks": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "discussion_question": {
                        "type": "string"
                    }
                },
                "required": [
                    "topic",
                    "reason",
                    "best_content_angle",
                    "hooks",
                    "discussion_question"
                ]
            }
        }
    },
    "required": [
        "topics",
        "content_opportunities"
    ]
}
   
# ============================================================
# JSON CLEANER
# ============================================================

def extract_json(text):

    if not text:
        return None

    text = text.strip()

    # Remove markdown code fences
    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*$",
        "",
        text
    )

    text = text.strip()

    # Direct JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        possible_json = text[start:end + 1]

        try:
            return json.loads(possible_json)
        except json.JSONDecodeError:
            pass

    return None


# ============================================================
# AI EMAIL ANALYSIS
# ============================================================

# ============================================================
# AI EMAIL ANALYSIS
# ============================================================

def summarize_email(email_content, sender):

    print("\n" + "=" * 80)
    print("STEP 1: DETECTING NEWSLETTER SECTIONS")
    print("=" * 80)

    # --------------------------------------------------------
    # STEP 1: EXTRACT SECTIONS
    # --------------------------------------------------------

    section_prompt = SECTION_EXTRACTION_PROMPT.replace(
        "{email_content}",
        email_content
    )

    raw_sections = ask_ollama(
        section_prompt,
        SECTION_SCHEMA
    )

    sections = extract_json(raw_sections)

    if not sections or "sections" not in sections:

        return {
            "error": "Could not detect newsletter sections.",
            "raw_response": raw_sections
        }

    print(
        f"Sections detected: {len(sections['sections'])}"
    )

    for index, section in enumerate(
        sections["sections"],
        start=1
    ):

        print(
            f"{index}. {section['section_name']}"
        )


    # --------------------------------------------------------
    # STEP 2: ANALYZE EACH SECTION
    # --------------------------------------------------------

    section_results = []

    for index, section in enumerate(
        sections["sections"],
        start=1
    ):

        section_name = section.get(
            "section_name",
            f"Section {index}"
        )

        section_content = section.get(
            "content",
            ""
        )

        if not section_content.strip():
            continue

        print("\n" + "-" * 80)

        print(
            f"STEP 2: ANALYZING SECTION {index}/"
            f"{len(sections['sections'])}"
        )

        print(
            f"SECTION: {section_name}"
        )

        print("-" * 80)

        prompt = SECTION_ANALYSIS_PROMPT.replace(
            "{section_content}",
            section_content
        )

        raw_analysis = ask_ollama(
            prompt,
            SECTION_ANALYSIS_SCHEMA
        )

        parsed_analysis = extract_json(
            raw_analysis
        )

        if parsed_analysis is None:

            print(
                f"Could not parse section: {section_name}"
            )

            continue

        section_results.append(
            parsed_analysis
        )

        topic_count = len(
            parsed_analysis.get(
                "topics",
                []
            )
        )

        print(
            f"Topics found in this section: {topic_count}"
        )


    # --------------------------------------------------------
    # STEP 3: FINAL SELECTION
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("STEP 3: FINAL CROSS-SECTION SELECTION")
    print("=" * 80)

    if not section_results:

        return {
            "error": "No section analyses were produced."
        }

    section_analyses = json.dumps(
        section_results,
        ensure_ascii=False,
        indent=2
    )

    final_prompt = FINAL_SELECTION_PROMPT.replace(
        "{section_analyses}",
        section_analyses
    )

    raw_final = ask_ollama(
        final_prompt,
        FINAL_SCHEMA
    )

    final_result = extract_json(
        raw_final
    )

    if final_result is None:

        return {
            "error": "Final AI selection returned invalid JSON.",
            "raw_response": raw_final
        }

    return final_result

# ============================================================
# BASE64 DECODER
# ============================================================

def decode_email_data(data):

    if not data:
        return ""

    try:

        padding = "=" * (-len(data) % 4)

        data += padding

        decoded = base64.urlsafe_b64decode(data)

        return decoded.decode(
            "utf-8",
            errors="replace"
        )

    except Exception:

        return ""


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    lines = [
        line.strip()
        for line in text.split("\n")
    ]

    lines = [
        line
        for line in lines
        if line
    ]

    cleaned_lines = []

    for line in lines:

        if not cleaned_lines:
            cleaned_lines.append(line)

        elif line != cleaned_lines[-1]:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


# ============================================================
# CLEAN HTML
# ============================================================

def clean_html(html):

    if not html:
        return ""

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    for tag in soup.find_all([
        "style",
        "script",
        "noscript",
        "head",
        "meta",
        "title",
        "img",
        "svg",
        "picture"
    ]):

        tag.decompose()

    text = soup.get_text(
        "\n",
        strip=True
    )

    return clean_text(text)


# ============================================================
# REMOVE NEWSLETTER ADS / FOOTERS
# ============================================================

def remove_ad_sections(text):

    if not text:
        return ""

    lines = text.splitlines()

    cleaned = []

    skip = False

    for line in lines:

        lower = line.lower().strip()

        # Common newsletter ad markers
        if lower.startswith("#ad"):
            skip = True
            continue

        if lower in [
            "advertisement",
            "sponsored",
            "sponsor",
            "sponsored by"
        ]:
            skip = True
            continue

        # Stop skipping when a new major section starts
        if skip and (
            lower.startswith("##")
            or lower.startswith("topic")
            or lower.startswith("research")
            or lower.startswith("tools")
            or lower.startswith("quick hits")
            or lower.startswith("the setup")
        ):
            skip = False

        if not skip:
            cleaned.append(line)

    return clean_text(
        "\n".join(cleaned)
    )


# ============================================================
# FIND EMAIL PARTS
# ============================================================

def collect_email_parts(payload):

    plain_text_parts = []
    html_parts = []

    mime_type = payload.get(
        "mimeType",
        ""
    )

    body = payload.get(
        "body",
        {}
    )

    if body.get("data"):

        content = decode_email_data(
            body["data"]
        )

        if mime_type == "text/plain":

            if content.strip():
                plain_text_parts.append(content)

        elif mime_type == "text/html":

            if content.strip():
                html_parts.append(content)

    for part in payload.get(
        "parts",
        []
    ):

        nested_plain, nested_html = collect_email_parts(
            part
        )

        plain_text_parts.extend(
            nested_plain
        )

        html_parts.extend(
            nested_html
        )

    return (
        plain_text_parts,
        html_parts
    )


# ============================================================
# REMOVE DUPLICATE CONTENT
# ============================================================

def remove_duplicate_blocks(parts):

    unique_parts = []
    seen = set()

    for part in parts:

        cleaned = clean_text(part)

        if not cleaned:
            continue

        key = cleaned.lower()

        if key not in seen:

            seen.add(key)

            unique_parts.append(
                cleaned
            )

    return unique_parts


# ============================================================
# GET EMAIL BODY
# ============================================================

def get_email_body(payload):

    plain_parts, html_parts = collect_email_parts(
        payload
    )

    plain_parts = remove_duplicate_blocks(
        plain_parts
    )

    if plain_parts:

        body = "\n\n".join(
            plain_parts
        ).strip()

    else:

        cleaned_html_parts = []

        for html in html_parts:

            cleaned = clean_html(
                html
            )

            if cleaned:
                cleaned_html_parts.append(
                    cleaned
                )

        cleaned_html_parts = remove_duplicate_blocks(
            cleaned_html_parts
        )

        if cleaned_html_parts:

            body = "\n\n".join(
                cleaned_html_parts
            ).strip()

        else:

            body = ""

    # Remove obvious ad sections
    body = remove_ad_sections(body)

    return body


# ============================================================
# GET EMAIL HEADERS
# ============================================================

def get_email_headers(email_data):

    payload = email_data.get(
        "payload",
        {}
    )

    headers = payload.get(
        "headers",
        []
    )

    sender = ""
    subject = ""
    date = ""

    for header in headers:

        name = header.get(
            "name",
            ""
        ).lower()

        value = header.get(
            "value",
            ""
        )

        if name == "from":
            sender = value

        elif name == "subject":
            subject = value

        elif name == "date":
            date = value

    return (
        sender,
        subject,
        date
    )
# ============================================================
# CONFIGURATION
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

SENDERS = [
    "hi@mail.theresanaiforthat.com",
    "stayingahead@mail.beehiiv.com"
]

# ============================================================
# CREATE GMAIL SERVICE
# ============================================================

def create_gmail_service():

    print("Loading Gmail credentials...")

    credentials = Credentials.from_authorized_user_file(
        "token.json",
        SCOPES
    )

    gmail = build(
        "gmail",
        "v1",
        credentials=credentials
    )

    print("Gmail service ready.")

    return gmail


# ============================================================
# GET EMAILS FROM ONE SENDER
# ============================================================

def get_emails_from_sender(gmail, sender):

    print(
        f"\nSearching latest email from: {sender}"
    )

    for attempt in range(3):

        try:

            results = gmail.users().messages().list(
                userId="me",
                q=f"from:{sender}",
                maxResults=1
            ).execute()

            return results.get(
                "messages",
                []
            )

        except (
            ConnectionResetError,
            TimeoutError
        ) as error:

            print(
                f"Gmail connection error. Retry {attempt + 1}/3..."
            )

            if attempt == 2:
                print(
                    f"Could not fetch emails from {sender}"
                )
                return []

            time.sleep(
                2 ** attempt
            )

        except HttpError as error:

            print(
                f"Gmail API error: {error}"
            )

            return []

        except Exception as error:

            print(
                f"Unexpected Gmail error: {error}"
            )

            return []

    return []


# ============================================================
# PROCESS ONE EMAIL
# ============================================================

def process_email(
    gmail,
    message_id
):

    email_data = gmail.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    sender, subject, date = get_email_headers(
        email_data
    )

    body = get_email_body(
        email_data.get(
            "payload",
            {}
        )
    )

    print(
        f"Email length: {len(body)} characters"
    )

    print(
    "Sending email to Qwen..."

    )

    analysis = summarize_email(
        body,
        sender
    )

    return {
        "id": message_id,
        "sender": sender,
        "subject": subject,
        "date": date,
        "body": body,
        "analysis": analysis
    }


# ============================================================
# PRINT EMAIL
# ============================================================

def print_email(email_data):

    print("\n")
    print("=" * 80)

    print(
        "FROM:",
        email_data["sender"]
    )

    print(
        "SUBJECT:",
        email_data["subject"]
    )

    print(
        "DATE:",
        email_data["date"]
    )

    print("\nEMAIL CONTENT")
    print("-" * 80)

    print(
        email_data["body"]
    )

    print("\n🤖 QWEN ANALYSIS")
    print("-" * 80)

    print(
        json.dumps(
            email_data["analysis"],
            indent=2,
            ensure_ascii=False
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("EMAIL AI AUTOMATION - GMAIL READER")
    print("=" * 80)

    gmail = create_gmail_service()

    total_emails = 0

    for sender in SENDERS:

        print("\n")
        print("#" * 80)

        print(
            "SOURCE:",
            sender
        )

        print("#" * 80)

        messages = get_emails_from_sender(
            gmail,
            sender
        )

        print(
            "Emails found:",
            len(messages)
        )

        for message in messages:

            try:

                email_data = process_email(
                    gmail,
                    message["id"]
                )

                print_email(
                    email_data
                )

                total_emails += 1

            except Exception as error:

                print(
                    "\nError processing email:",
                    message.get("id")
                )

                print(
                    "Error:",
                    error
                )

    print("\n")
    print("=" * 80)

    print(
        "TOTAL EMAILS PROCESSED:",
        total_emails
    )

    print("=" * 80)


if __name__ == "__main__":
    main()