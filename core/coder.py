# core/coder.py — Universal Coder (No-API, Multi-Language)
from __future__ import annotations
from textwrap import dedent

def _mk(title: str, lang: str, code: str) -> dict:
    return {"title": title, "lang": lang, "code": dedent(code).strip()}

def generate_code(prompt: str) -> dict:
    """
    يحاول فهم اللغة/النوع من نصّ المستخدم ويولّد كودًا مناسبًا.
    يعيد dict: {title, lang, code}
    """
    p = (prompt or "").lower()

    # ===== مواقع وصفحات =====
    if any(w in p for w in ["html", "موقع", "صفحه", "صفحة", "landing"]):
        return _mk("صفحة HTML ترحيبية بسيطة", "HTML", """
            <!DOCTYPE html>
            <html lang="ar">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1" />
              <title>ترحيب</title>
              <style>
                body{font-family:Tahoma,Arial;background:#0b1220;color:#e7ecff;margin:0}
                .container{max-width:840px;margin:8vh auto;padding:24px}
                .card{background:#121b2d;border:1px solid #1e2b44;border-radius:14px;padding:24px}
                a{color:#9bd1ff}
              </style>
            </head>
            <body>
              <div class="container">
                <div class="card">
                  <h1>مرحباً بك 👋</h1>
                  <p>هذه صفحة HTML تم توليدها تلقائيًا من نواة بسّام الذكية.</p>
                </div>
              </div>
            </body>
            </html>
        """)

    if "css" in p or "تصميم" in p or "ستايل" in p:
        return _mk("ملف CSS بسيط", "CSS", """
            body{font-family:system-ui;background:#0b1220;color:#e7ecff}
            .btn{padding:10px 16px;border:1px solid #1e2b44;border-radius:10px;background:#14264b;color:#e7ecff}
        """)

    if any(w in p for w in ["javascript","js","جافا سكريبت"]):
        return _mk("سكربت JavaScript بسيط", "JavaScript", """
            console.log("مرحباً من نواة بسّام!");
            document.body.innerHTML = "<h1 style='text-align:center'>مرحباً 👋</h1>";
        """)

    if "typescript" in p or "ts" in p:
        return _mk("TypeScript مثال بسيط", "TypeScript", """
            function greet(name: string = "العالم"): string {
              return `مرحباً يا ${name}!`;
            }
            console.log(greet());
        """)

    if "react" in p:
        return _mk("React عبر CDN (ملف واحد)", "React", """
            <!DOCTYPE html><html lang="ar"><head>
              <meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
              <title>React Hello</title>
              <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
              <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
            </head><body><div id="root"></div>
            <script>
              const e = React.createElement;
              function App(){ return e('h1', null, 'مرحباً من React!'); }
              ReactDOM.createRoot(document.getElementById('root')).render(e(App));
            </script></body></html>
        """)

    if "vue" in p:
        return _mk("Vue عبر CDN (ملف واحد)", "Vue", """
            <!DOCTYPE html><html lang="ar"><head>
              <meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
              <title>Vue Hello</title>
              <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
            </head><body><div id="app">{{ msg }}</div>
            <script>
              Vue.createApp({data(){return{msg:'مرحباً من Vue 3!'}}}).mount('#app');
            </script></body></html>
        """)

    # ===== Python =====
    if "بايثون" in p or "python" in p or "py" in p:
        return _mk("سكربت بايثون يطبع رسالة", "Python", """
            def greet(name="العالم"):
                return f"مرحباً يا {name}!"
            if __name__ == "__main__":
                print(greet())
        """)

    if "fastapi" in p or "api بايثون" in p or "rest" in p:
        return _mk("خادوم FastAPI بسيط", "Python (FastAPI)", """
            from fastapi import FastAPI
            app = FastAPI()
            @app.get("/hello")
            def hello(name: str = "العالم"):
                return {"msg": f"مرحباً يا {name}!"}
            if __name__ == "__main__":
                import uvicorn
                uvicorn.run(app, host="0.0.0.0", port=8000)
        """)

    if "flask" in p:
        return _mk("خادوم Flask بسيط", "Python (Flask)", """
            from flask import Flask
            app = Flask(__name__)
            @app.route("/")
            def index(): return "مرحباً من Flask!"
            if __name__ == "__main__":
                app.run(host="0.0.0.0", port=5000)
        """)

    # ===== لغات برمجة أخرى =====
    if "csharp" in p or "c#" in p or "سي شارب" in p:
        return _mk("C# Console", "C#", """
            using System;
            class Program {
              static void Main(){ Console.WriteLine("مرحباً من C#!"); }
            }
        """)

    if "java " in p or p.startswith("java") or "جافا" in p:
        return _mk("Java Console", "Java", """
            public class Hello {
                public static void main(String[] args) {
                    System.out.println("مرحباً من Java!");
                }
            }
        """)

    if "kotlin" in p or "كوتلن" in p:
        return _mk("Kotlin Console", "Kotlin", """
            fun main(){ println("مرحباً من Kotlin!") }
        """)

    if "swift" in p or "سويفت" in p:
        return _mk("Swift Console", "Swift", """
            import Foundation
            print("مرحباً من Swift!")
        """)

    if "go " in p or p.startswith("go") or "golang" in p:
        return _mk("Go Console", "Go", """
            package main
            import "fmt"
            func main(){ fmt.Println("مرحباً من Go!") }
        """)

    if "rust" in p or "راست" in p:
        return _mk("Rust Console", "Rust", """
            fn main(){ println!("مرحباً من Rust!"); }
        """)

    if "dart" in p:
        return _mk("Dart Console", "Dart", """
            void main(){ print("مرحباً من Dart!"); }
        """)

    if "c++" in p or "cpp" in p or "سي بلس" in p:
        return _mk("C++ Console", "C++", """
            #include <iostream>
            int main(){ std::cout << "مرحباً من C++!\\n"; return 0; }
        """)

    if " c " in p or p.startswith("c "):
        return _mk("C Console", "C", """
            #include <stdio.h>
            int main(){ printf("مرحباً من C!\\n"); return 0; }
        """)

    if "php" in p:
        return _mk("PHP صفحة بسيطة", "PHP", """
            <?php echo "<h1>مرحباً من PHP!</h1>"; ?>
        """)

    if "sql" in p or "قاعدة" in p or "بيانات" in p:
        return _mk("SQL CRUD على جدول users", "SQL", """
            CREATE TABLE IF NOT EXISTS users(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              email TEXT UNIQUE
            );
            INSERT INTO users(name,email) VALUES ("Ali","ali@example.com");
            SELECT id,name,email FROM users;
            UPDATE users SET name="Aly" WHERE id=1;
            DELETE FROM users WHERE id=1;
        """)

    if "bash" in p or "shell" in p or "باش" in p:
        return _mk("Bash Script", "Bash", """
            #!/usr/bin/env bash
            echo "مرحباً من نواة بسّام!"
        """)

    # ===== افتراضي =====
    return _mk("قالب عام — وضّح اللغة أو نوع المشروع", "Plain",
               "⚙️ لم أتعرف بعد على نوع الكود المطلوب، وضّح لي اللغة أو المجال.")
