import re

class MarkdownStripper:
    def __init__(self):
        self.patterns = [
            (r'\*\*(.*?)\*\*', r'\1'),  # Bold
            (r'\*(.*?)\*', r'\1'),  # Italics
            (r'\_(.*?)\_', r'\1'),  # Italics with underscores
            (r'\~\~(.*?)\~\~', r'\1'),  # Strikethrough
            (r'\[(.*?)\]\((.*?)\)', r'\1 \2'),  # Convert links to text followed by URL
            (r'\!\[(.*?)\]\((.*?)\)', r'\1'),  # Convert image alt text, remove URL
            (r'`{1,3}(.*?)`{1,3}', r'\1'),  # Inline code to regular text
            (r'^>+\s', ''),  # Remove blockquotes
            (r'^#+\s', ''),  # Remove headers
            (r'^-\s', ''),  # Remove list items
            (r'^\*\s', ''),  # Remove list items
            (r'^\+\s', ''),  # Remove list items
            (r'\n-{3,}', ''),  # Remove horizontal rules
            (r'\n+', ' '),  # Replace multiple new lines with a single space
        ]

    def strip(self, text):
        for pattern, replace in self.patterns:
            text = re.sub(pattern, replace, text, flags=re.MULTILINE)
        return text.strip()
