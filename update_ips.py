name: Update Dynamic EDLs for Palo Alto

on:
  schedule:
    - cron: '0 */6 * * *' # הרצה אוטומטית כל 6 שעות
  workflow_dispatch: # מאפשר הרצה ידנית מתוך ממשק GitHub Actions

# הגדרת הרשאות ממוקדות: הרשאת כתיבה לתוכן המאגר בלבד
permissions:
  contents: write

jobs:
  update-lists:
    runs-on: ubuntu-latest

    steps:
      # 1. טעינת הרפוזיטורי (גרסה מעודכנת המונעת אזהרות Deprecation)
      - name: Checkout repository
        uses: actions/checkout@v4.2.2

      # 2. הגדרת סביבת Python
      - name: Set up Python
        uses: actions/setup-python@v5.3.0
        with:
          python-version: '3.10'

      # 3. הרצת סקריפט התרגום עבור YES / STINGTV
      - name: Run YES / STINGTV script
        run: python yes_script.py

      # 4. הרצת סקריפט התרגום עבור Quickbase
      - name: Run Quickbase script
        run: python quickbase_script.py

      # 5. ביצוע Commit ו-Push אם חלו שינויים בקובצי ה-EDL
      - name: Commit and push changes
        uses: stefanzweifel/git-auto-commit-action@v5.0.1
        with:
          commit_message: "Auto-update EDL IP lists [skip ci]"
          file_pattern: "yes_ips.txt quickbase_ips.txt"
