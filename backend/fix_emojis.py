"""
Fix Unicode emoji characters in all backend app.py files for Windows compatibility
"""
import os
import re

# Service directories to fix
SERVICES = [
    'portfolio_optimizer',
    'advanced_backtest',
    'simulation_engine',
    'fractional_diff',
    'meta_labeling',
    'stock_screener'
]

def remove_emojis(text):
    """Replace common emojis with ASCII equivalents"""
    replacements = {
        '🚀': '[START]',
        '📊': '[INFO]',
        '✅': '[OK]',
        '📖': '[INFO]',
        '🤖': '[START]',
        '⚠': '[WARN]',
        '❌': '[FAIL]',
        '✓': '[OK]',
        '🔬': '[INFO]',
        '🧠': '[INFO]',
        '📈': '[INFO]',
        '🎯': '[INFO]',
        '📉': '[INFO]',
    }

    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)

    # Remove any remaining emoji characters (Unicode range)
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)

    return text

def fix_file(filepath):
    """Fix a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        content = remove_emojis(content)

        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Fixed {filepath}")
            return True
        else:
            print(f"[SKIP] No emojis found in {filepath}")
            return False
    except Exception as e:
        print(f"[FAIL] Error fixing {filepath}: {e}")
        return False

def main():
    backend_dir = os.path.dirname(__file__)
    fixed_count = 0

    for service in SERVICES:
        app_file = os.path.join(backend_dir, service, 'app.py')
        if os.path.exists(app_file):
            if fix_file(app_file):
                fixed_count += 1
        else:
            print(f"[WARN] {app_file} not found")

    print(f"\n[DONE] Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
