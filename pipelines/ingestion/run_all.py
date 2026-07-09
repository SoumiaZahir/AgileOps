"""
Lance tous les scripts d'ingestion en une seule commande.
Usage : python run_all.py
"""

import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = [
    "ingest_courses.py",
    "ingest_assessments.py",
    "ingest_student_info.py",
    "ingest_student_registration.py",
    "ingest_student_assessment.py",
    "ingest_vle.py",
    "ingest_student_vle.py",   # le plus volumineux, lancé en dernier
]

if __name__ == "__main__":
    print("=== Lancement de toutes les ingestions ===\n")
    for script in SCRIPTS:
        print(f"--- {script} ---")
        script_path = os.path.join(SCRIPT_DIR, script)
        result = subprocess.run([sys.executable, script_path])
        if result.returncode != 0:
            print(f"⚠️  {script} a échoué (voir data/raw/ingestion_log.jsonl)")
    print("\n=== Terminé ===")
