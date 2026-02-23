#!/usr/bin/env python3
"""Launch the Pressberg Kitchen Recipe Assistant web interface"""

from src.web import app

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Pressberg Kitchen Recipe Assistant")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50 + "\n")
    app.run(debug=True, port=5000)
