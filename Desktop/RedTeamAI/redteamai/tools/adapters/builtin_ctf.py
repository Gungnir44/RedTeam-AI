"""Built-in CTF tools: pure Python, no external binary required."""
from __future__ import annotations
import base64
import binascii
import hashlib
import string
import urllib.parse
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.ai.tool_manifest import build_tool_schema, string_param, integer_param


class BuiltinCTFTool(BaseTool):
    @property
    def name(self) -> str:
        return "ctf_decode"

    @property
    def display_name(self) -> str:
        return "CTF Decoder"

    @property
    def description(self) -> str:
        return "Encode/decode text: base64, hex, rot13, caesar, xor, morse, binary, url, atbash"

    @property
    def is_builtin(self) -> bool:
        return True

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "operation": string_param(
                    "Operation to perform",
                    enum=["base64_decode", "base64_encode", "hex_decode", "hex_encode",
                          "rot13", "caesar", "xor", "morse_decode", "morse_encode",
                          "binary_decode", "binary_encode", "url_decode", "url_encode",
                          "atbash", "hash_identify", "hash_md5", "hash_sha256",
                          "from_decimal", "to_decimal"],
                ),
                "text": string_param("Input text to process"),
                "key": string_param("Key for operations that require one (caesar shift, XOR key)"),
            },
            required=["operation", "text"],
        )

    def execute(self, operation: str, text: str, key: str = "") -> ToolResult:
        try:
            result = self._dispatch(operation, text, key)
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

    def _dispatch(self, op: str, text: str, key: str) -> str:
        ops = {
            "base64_decode": self._b64_decode,
            "base64_encode": self._b64_encode,
            "hex_decode": self._hex_decode,
            "hex_encode": self._hex_encode,
            "rot13": self._rot13,
            "caesar": self._caesar,
            "xor": self._xor,
            "morse_decode": self._morse_decode,
            "morse_encode": self._morse_encode,
            "binary_decode": self._binary_decode,
            "binary_encode": self._binary_encode,
            "url_decode": lambda t, k: urllib.parse.unquote(t),
            "url_encode": lambda t, k: urllib.parse.quote(t),
            "atbash": self._atbash,
            "hash_identify": self._hash_identify,
            "hash_md5": lambda t, k: hashlib.md5(t.encode()).hexdigest(),
            "hash_sha256": lambda t, k: hashlib.sha256(t.encode()).hexdigest(),
            "from_decimal": lambda t, k: "".join(chr(int(x)) for x in t.split()),
            "to_decimal": lambda t, k: " ".join(str(ord(c)) for c in t),
        }
        fn = ops.get(op)
        if not fn:
            raise ValueError(f"Unknown operation: {op}")
        return fn(text, key)

    def _b64_decode(self, text: str, _: str) -> str:
        # Try standard, then URL-safe
        text = text.strip()
        for fn in (base64.b64decode, base64.urlsafe_b64decode):
            try:
                padded = text + "=" * (-len(text) % 4)
                decoded = fn(padded)
                try:
                    return decoded.decode("utf-8")
                except UnicodeDecodeError:
                    return decoded.hex()
            except Exception:
                continue
        raise ValueError("Invalid base64")

    def _b64_encode(self, text: str, _: str) -> str:
        return base64.b64encode(text.encode()).decode()

    def _hex_decode(self, text: str, _: str) -> str:
        text = text.strip().replace(" ", "").replace("0x", "").replace("\\x", "")
        raw = bytes.fromhex(text)
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1")

    def _hex_encode(self, text: str, _: str) -> str:
        return text.encode().hex()

    def _rot13(self, text: str, _: str) -> str:
        return text.translate(str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm",
        ))

    def _caesar(self, text: str, key: str) -> str:
        shift = int(key) if key.lstrip("-").isdigit() else 13
        result = []
        for ch in text:
            if ch.isupper():
                result.append(chr((ord(ch) - 65 + shift) % 26 + 65))
            elif ch.islower():
                result.append(chr((ord(ch) - 97 + shift) % 26 + 97))
            else:
                result.append(ch)
        return "".join(result)

    def _xor(self, text: str, key: str) -> str:
        if not key:
            raise ValueError("XOR requires a key")
        # Try hex input
        try:
            data = bytes.fromhex(text.replace(" ", ""))
        except ValueError:
            data = text.encode()
        key_bytes = key.encode()
        xored = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))
        try:
            return xored.decode("utf-8")
        except UnicodeDecodeError:
            return xored.hex()

    _MORSE = {
        ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
        "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
        "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
        ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
        "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
        "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
        "...--": "3", "....-": "4", ".....": "5", "-....": "6",
        "--...": "7", "---..": "8", "----.": "9",
    }
    _MORSE_REV = {v: k for k, v in _MORSE.items()}

    def _morse_decode(self, text: str, _: str) -> str:
        words = text.strip().split("   ")
        return " ".join("".join(self._MORSE.get(c, "?") for c in w.split()) for w in words)

    def _morse_encode(self, text: str, _: str) -> str:
        return "   ".join(
            " ".join(self._MORSE_REV.get(c.upper(), "?") for c in w)
            for w in text.upper().split()
        )

    def _binary_decode(self, text: str, _: str) -> str:
        text = text.strip().replace(" ", "")
        chars = [text[i:i+8] for i in range(0, len(text), 8)]
        return "".join(chr(int(c, 2)) for c in chars if c)

    def _binary_encode(self, text: str, _: str) -> str:
        return " ".join(format(ord(c), "08b") for c in text)

    def _atbash(self, text: str, _: str) -> str:
        result = []
        for ch in text:
            if ch.isupper():
                result.append(chr(90 - (ord(ch) - 65)))
            elif ch.islower():
                result.append(chr(122 - (ord(ch) - 97)))
            else:
                result.append(ch)
        return "".join(result)

    def _hash_identify(self, text: str, _: str) -> str:
        h = text.strip()
        patterns = [
            (32, "hex", "MD5"),
            (40, "hex", "SHA-1"),
            (56, "hex", "SHA-224"),
            (64, "hex", "SHA-256"),
            (96, "hex", "SHA-384"),
            (128, "hex", "SHA-512"),
            (32, "alphanum", "NTLM/MD5"),
        ]
        try:
            int(h, 16)
            is_hex = True
        except ValueError:
            is_hex = False

        results = []
        for length, kind, name in patterns:
            if len(h) == length:
                if kind == "hex" and is_hex:
                    results.append(name)

        if h.startswith("$2"):
            results.append("bcrypt")
        if h.startswith("$1$"):
            results.append("MD5 crypt")
        if h.startswith("$6$"):
            results.append("SHA-512 crypt")

        return f"Possible hash types: {', '.join(results) if results else 'Unknown'}\nLength: {len(h)}\nHex: {is_hex}"
