# core/coder.py — توليد أكواد محلّي بالاعتماد على قواعد بسيطة
from textwrap import dedent

def generate_code(prompt: str) -> str:
    """مولّد أكواد بسيط بدون LLM خارجي"""
    prompt = prompt.lower()
    if "موقع" in prompt or "html" in prompt:
        return dedent("""
        <!DOCTYPE html>
        <html lang="ar">
        <head><meta charset="UTF-8"><title>موقعي</title></head>
        <body>
          <h1>مرحباً بك في موقعي!</h1>
        </body>
        </html>
        """).strip()
    elif "بايثون" in prompt or "python" in prompt:
        return dedent("""
        def hello():
            print("مرحباً من نواة بسام!")
        hello()
        """).strip()
    elif "جافا" in prompt or "java" in prompt:
        return dedent("""
        public class Hello {
            public static void main(String[] args) {
                System.out.println("مرحباً من نواة بسام!");
            }
        }
        """).strip()
    else:
        return "⚙️ لم أتعرف بعد على نوع الكود المطلوب، وضّح لي اللغة أو المجال."
