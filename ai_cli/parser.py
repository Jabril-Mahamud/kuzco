"""Advanced response parser for handling various model output formats"""
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ResponseType(Enum):
    """Types of response segments"""
    THOUGHT = "thought"
    CODE = "code"
    TEXT = "text"
    COMMAND = "command"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ResponseSegment:
    """A segment of parsed response"""
    type: ResponseType
    content: str
    metadata: Dict[str, str] = None


class ModelResponseParser:
    """Parse and clean responses from various AI models"""

    # Common thinking/reasoning patterns across models
    THINKING_PATTERNS = {
        'llama': [
            r'<thinking>(.*?)</thinking>',
            r'\*thinking\*(.*?)\*/thinking\*',
            r'Let me think.*?(?=\n\n)',
        ],
        'codellama': [
            r'<reasoning>(.*?)</reasoning>',
            r'```reasoning(.*?)```',
        ],
        'mistral': [
            r'<thoughts>(.*?)</thoughts>',
            r'<!--.*?-->',  # HTML comments
        ],
        'deepseek': [
            r'<analyze>(.*?)</analyze>',
            r'Analysis:(.*?)(?=Solution:|Answer:|$)',
        ],
        'default': [
            r'<.*?thinking.*?>(.*?)</.*?>',
            r'<.*?thoughts.*?>(.*?)</.*?>',
            r'<.*?reasoning.*?>(.*?)</.*?>',
            r'\[thinking\](.*?)\[/thinking\]',
        ]
    }

    def __init__(self, model_name: str = None):
        """Initialize parser for specific model"""
        self.model_name = model_name or 'default'
        self.model_family = self._detect_model_family(model_name)

    def _detect_model_family(self, model_name: str) -> str:
        """Detect model family from name"""
        if not model_name:
            return 'default'

        model_lower = model_name.lower()

        if 'llama' in model_lower and 'code' not in model_lower:
            return 'llama'
        elif 'codellama' in model_lower or 'code' in model_lower:
            return 'codellama'
        elif 'mistral' in model_lower:
            return 'mistral'
        elif 'deepseek' in model_lower:
            return 'deepseek'
        else:
            return 'default'

    def parse_response(self, response: str) -> List[ResponseSegment]:
        """Parse response into segments"""
        segments = []
        remaining = response

        # Extract thinking/reasoning first
        thoughts = self._extract_thoughts(remaining)
        if thoughts:
            segments.append(ResponseSegment(ResponseType.THOUGHT, thoughts))
            remaining = self._remove_thoughts(remaining)

        # Extract code blocks
        code_blocks = self._extract_code_blocks(remaining)
        for code, language in code_blocks:
            segments.append(ResponseSegment(
                ResponseType.CODE,
                code,
                {'language': language}
            ))
            remaining = remaining.replace(f"```{language}\n{code}```", "")
            remaining = remaining.replace(f"```\n{code}```", "")

        # Extract commands
        commands = self._extract_commands(remaining)
        for command in commands:
            segments.append(ResponseSegment(ResponseType.COMMAND, command))
            remaining = remaining.replace(f"EXECUTE_COMMAND: {command}", "")

        # Remaining text
        if remaining.strip():
            segments.append(ResponseSegment(ResponseType.TEXT, remaining.strip()))

        return segments

    def _extract_thoughts(self, text: str) -> Optional[str]:
        """Extract thinking/reasoning sections"""
        patterns = self.THINKING_PATTERNS.get(
            self.model_family,
            self.THINKING_PATTERNS['default']
        )

        thoughts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            thoughts.extend(matches)

        return '\n'.join(thoughts) if thoughts else None

    def _remove_thoughts(self, text: str) -> str:
        """Remove thinking sections from text"""
        patterns = self.THINKING_PATTERNS.get(
            self.model_family,
            self.THINKING_PATTERNS['default']
        )

        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)

        return text

    def _extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extract code blocks with language detection"""
        code_blocks = []

        # Match code blocks with language specifier
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        for language, code in matches:
            language = language or 'text'
            code_blocks.append((code.strip(), language))

        return code_blocks

    def _extract_commands(self, text: str) -> List[str]:
        """Extract executable commands"""
        commands = []

        # Look for EXECUTE_COMMAND markers
        for line in text.split('\n'):
            if line.strip().startswith('EXECUTE_COMMAND:'):
                command = line.replace('EXECUTE_COMMAND:', '').strip()
                commands.append(command)

        # Also look for shell command patterns
        shell_pattern = r'^\$\s+(.+)$'
        for line in text.split('\n'):
            match = re.match(shell_pattern, line)
            if match:
                commands.append(match.group(1))

        return commands

    def clean_for_display(self, response: str, show_thoughts: bool = False) -> str:
        """Clean response for display to user"""
        segments = self.parse_response(response)

        display_parts = []
        for segment in segments:
            if segment.type == ResponseType.THOUGHT and not show_thoughts:
                continue  # Skip thoughts unless requested
            elif segment.type == ResponseType.CODE:
                # Format code blocks nicely
                lang = segment.metadata.get('language', 'text')
                display_parts.append(f"```{lang}\n{segment.content}\n```")
            elif segment.type == ResponseType.COMMAND:
                # Don't show raw command markers
                continue
            else:
                display_parts.append(segment.content)

        return '\n\n'.join(display_parts)

    def clean_for_file_edit(self, response: str) -> str:
        """Clean response specifically for file editing"""
        segments = self.parse_response(response)

        # For file edits, we want only code or text content
        for segment in segments:
            if segment.type == ResponseType.CODE:
                return segment.content
            elif segment.type == ResponseType.TEXT:
                # Check if this looks like file content
                if self._looks_like_file_content(segment.content):
                    return segment.content

        # Fallback: return cleaned text without thoughts
        return self.clean_for_display(response, show_thoughts=False)

    def _looks_like_file_content(self, text: str) -> bool:
        """Heuristic to determine if text is file content"""
        # Check for code indicators
        code_indicators = [
            'import ', 'function ', 'class ', 'def ', 'const ', 'var ', 'let ',
            '#include', 'package ', 'public ', 'private ', '#!/'
        ]

        for indicator in code_indicators:
            if indicator in text:
                return True

        # Check if it has multiple lines and looks structured
        lines = text.split('\n')
        if len(lines) > 3:
            # Likely file content if multi-line
            return True

        return False

    def extract_structured_data(self, response: str) -> Dict[str, any]:
        """Extract structured data from response (JSON, tables, etc.)"""
        data = {}

        # Try to find JSON blocks
        json_pattern = r'```json\n(.*?)```'
        json_matches = re.findall(json_pattern, response, re.DOTALL)
        if json_matches:
            import json
            for match in json_matches:
                try:
                    parsed = json.loads(match)
                    data['json'] = parsed
                except:
                    pass

        # Try to find table data
        table_pattern = r'\|.*\|.*\|'
        if re.search(table_pattern, response):
            lines = response.split('\n')
            tables = []
            current_table = []

            for line in lines:
                if '|' in line:
                    current_table.append(line)
                elif current_table:
                    tables.append(current_table)
                    current_table = []

            if current_table:
                tables.append(current_table)

            if tables:
                data['tables'] = tables

        return data


class StreamingResponseParser:
    """Parser specifically for streaming responses"""

    def __init__(self, model_name: str = None):
        self.parser = ModelResponseParser(model_name)
        self.buffer = ""
        self.in_thought = False
        self.thought_depth = 0

    def process_token(self, token: str) -> Tuple[str, ResponseType]:
        """Process a streaming token and return display text with type"""
        self.buffer += token

        # Check if we're entering a thought section
        if not self.in_thought:
            for pattern in ['<thinking', '<thought', '<reasoning']:
                if pattern in self.buffer[-20:]:  # Check recent buffer
                    self.in_thought = True
                    self.thought_depth = 1
                    return (token, ResponseType.THOUGHT)

        # Check if we're exiting a thought section
        if self.in_thought:
            if '</' in token:
                self.thought_depth -= 1
                if self.thought_depth <= 0:
                    self.in_thought = False
                    return (token, ResponseType.THOUGHT)
            return (token, ResponseType.THOUGHT)

        # Regular text
        return (token, ResponseType.TEXT)

    def finalize(self) -> str:
        """Finalize and clean the complete response"""
        return self.parser.clean_for_display(self.buffer)