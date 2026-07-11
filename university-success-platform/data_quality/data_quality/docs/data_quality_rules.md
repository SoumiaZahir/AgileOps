# Règles de qualité des données — Dataset OULAD

**Projet :** Smart Platform for University Success — Prédiction Pass/Fail
**Responsable :** Imane Alouani — Data Quality Specialist
**Outil :** Great Expectations 1.18 (moteur de validation : pandas)
**Sources :**
- Couche **Raw** : `university.duckdb` (livrable d'Aymen — schéma `raw`)
- Couche **Marts** : `data/marts/*.csv` (livrable de Marouane — sortie dbt)

**Date de dernière validation :** 10/07/2026

---

## 1. Méthodologie

Avant de définir les règles, chaque table a été profilée (comptage de
valeurs, plages min/max, valeurs distinctes, taux de valeurs manquantes)
afin de baser les règles sur la réalité des données. Le dataset OULAD
utilise le caractère `"?"` comme marqueur de valeur manquante dans les CSV
bruts — ce qui explique pourquoi plusieurs colonnes numériques (`date`,
`score`, `week_from`...) apparaissent en `VARCHAR` dans DuckDB.

Chaque règle est traduite en une *Expectation* Great Expectations, regroupée
en une **Expectation Suite par table**, puis validée via un **Checkpoint**.

La validation couvre les **trois couches du pipeline** ainsi que la
**cohérence inter-tables** :
- **Raw** (7 tables, section 2) — données brutes telles qu'ingérées ;
- **Staging** (7 tables, section 3) — données nettoyées par dbt (`"?"` → NULL,
  cast des types, harmonisation `imd_band`) ;
- **Marts** (2 tables, section 4) — données finales prêtes pour la
  modélisation (Abderahman) et les dashboards (Brahim) ;
- **Cross-table** (section 5) — contrôles d'intégrité référentielle entre tables.

---

## 2. Couche RAW — règles par table

### 2.1 `raw.courses` (22 lignes)

| Règle | Justification |
|---|---|
| `code_module`, `code_presentation` non nuls | Clés d'identification du cours |
| `code_presentation` au format `AAAA[B\|J]` (ex : `2013J`) | B = présentation de février, J = octobre |
| `module_presentation_length` entre 1 et 365 | Durée en jours, réaliste |
| Unicité de `(code_module, code_presentation)` | Un cours-présentation unique |

### 2.2 `raw.assessments` (206 lignes)

| Règle | Justification |
|---|---|
| `id_assessment` non nul et unique | Clé primaire |
| `code_module`, `code_presentation` non nuls | Rattachement obligatoire |
| `assessment_type` ∈ {TMA, CMA, Exam} | Seuls types valides |
| `weight` entre 0 et 100 | Pourcentage |
| `date` au format `?` ou entier | Tolère le marqueur de manquant |
| **`date` : < 2% de `"?"` tolérés** | ⚠️ **Anomalie** : 11/206 (5,3%) manquantes → dépasse le seuil |

### 2.3 `raw.student_info` (32 593 lignes)

| Règle | Justification |
|---|---|
| `id_student`, `code_module`, `code_presentation` non nuls | Champs obligatoires |
| Unicité de `(code_module, code_presentation, id_student)` | Un étudiant unique par présentation |
| `gender` ∈ {M, F} | Valeurs valides |
| `disability` ∈ {Y, N} | Valeurs valides |
| `final_result` ∈ {Pass, Fail, Withdrawn, Distinction} | Variable cible brute |
| `imd_band` ∈ valeurs observées (incl. `"?"`) | ⚠️ Format incohérent : `"10-20"` sans `%`. À standardiser en staging |
| `num_of_prev_attempts` entre 0 et 10 | Plage réaliste |
| `studied_credits` entre 0 et 1000 | Plage réaliste (30-655) |

### 2.4 `raw.student_registration` (32 593 lignes)

| Règle | Justification |
|---|---|
| `id_student` non nul | Obligatoire |
| Unicité de `(code_module, code_presentation, id_student)` | Une inscription unique |
| `date_registration`, `date_unregistration` au format `?` ou entier | Tolère le manquant |

> **Non-anomalie :** `date_unregistration` = 69% de `"?"` — **normal**, la
> majorité des étudiants ne se désinscrivent jamais. Aucun seuil appliqué.

### 2.5 `raw.student_assessment` (173 912 lignes)

| Règle | Justification |
|---|---|
| `id_assessment`, `id_student` non nuls | Clés obligatoires |
| `is_banked` ∈ {0, 1} | Booléen |
| `score` au format `?` ou entier 0-100 | 0,1% manquants — négligeable |

### 2.6 `raw.vle` (6 364 lignes)

| Règle | Justification |
|---|---|
| `id_site` non nul et unique | Clé primaire |
| `activity_type` non nul | Obligatoire |
| `week_from`, `week_to` au format `?` ou entier | Tolère le manquant |
| **`week_from`/`week_to` : < 50% de `"?"` tolérés** | 🔴 **Anomalie majeure** : 82,4% manquants |

### 2.7 `raw.student_vle` (10 655 280 lignes)

| Règle | Justification |
|---|---|
| `id_student`, `id_site` non nuls | Clés obligatoires |
| `sum_click` entre 1 et 20 000 | Plage réaliste (max observé 6977) |

---

## 3. Couche STAGING — règles par table

> La couche Staging est produite par les modèles dbt de Marouane. Elle
> convertit les marqueurs `"?"` en `NULL`, caste les colonnes numériques
> (`assessment_day`, `score`, `week_from`... en INTEGER) et harmonise
> `imd_band` (toujours avec `%`). Les règles ci-dessous **vérifient que ce
> nettoyage a bien eu lieu** ; elles passent toutes (34 règles), ce qui valide
> l'étape de transformation.

| Table (34 règles) | Règles clés |
|---|---|
| `stg_courses` (22) | clés non nulles, format `code_presentation`, `course_length_days` 1-365, unicité |
| `stg_assessments` (206) | `id_assessment` unique, `assessment_type` ∈ {TMA,CMA,Exam}, `assessment_day` 0-400, `assessment_weight` 0-100 |
| `stg_student_info` (32 593) | clé unique, `gender`/`disability`/`final_result` valides, **`imd_band` standardisé avec `%`** (vérifie le nettoyage), plages numériques |
| `stg_student_registration` (32 593) | clé unique, `date_registration` -400 à 400 (négatif valide) |
| `stg_student_assessment` (173 912) | clés non nulles, `is_banked` ∈ {0,1}, **`score` désormais INTEGER 0-100** |
| `stg_vle` (6 364) | `id_site` unique, `week_from`/`week_to` INTEGER 0-52 |
| `stg_student_vle` (10,6 M) | clés non nulles, `sum_click` 1-20 000 |

> **Résultat clé :** en couche staging, `imd_band` ne contient plus la valeur
> incohérente `"10-20"` (sans `%`) détectée en raw — le nettoyage dbt l'a
> corrigée. De même, les `"?"` sont devenus des `NULL` propres. Le contrôle
> qualité **confirme que la transformation fait bien son travail**.

---

## 4. Couche MARTS — règles par table

> La couche Marts est la sortie dbt finale de Marouane. Toutes les règles
> ci-dessous **passent**, ce qui confirme que la table est prête pour la
> modélisation.

### 4.1 `marts.student_success_features` (32 593 lignes, 27 règles)

| Catégorie | Règles |
|---|---|
| **Clé & identifiants** | `student_presentation_id` non nul et unique ; `id_student`, `code_module`, `code_presentation` non nuls ; `code_presentation` au format `AAAA[B\|J]` |
| **Variable cible** | `label_pass` non nul et ∈ {0, 1} ; `final_result` ∈ {Pass, Fail, Withdrawn, Distinction} |
| **Catégorielles** | `gender` ∈ {M,F} ; `disability` ∈ {Y,N} ; `age_band` ∈ {0-35, 35-55, 55<=} ; `imd_band` au format standardisé avec `%` ; `highest_education` ∈ 5 niveaux valides |
| **Flags binaires** | `registered_before_course_start`, `is_unregistered` ∈ {0, 1} |
| **Plages numériques** | scores (`weighted_avg_score`, `avg_score`) entre 0 et 100 ; compteurs (`n_assessments_submitted`, `n_late_submissions`, `n_active_days`, `total_clicks`, `n_distinct_materials_accessed`) dans des plages réalistes ; `studied_credits`, `course_length_days`, `num_of_prev_attempts` bornés |
| **Complétude** | `weighted_avg_score` : au moins 65% non nul (≈28% de NULL attendus pour les étudiants sans évaluation notée — **surveillé** pour détecter toute dérive future) |

> **Point d'attention transmis à Abderahman (modèle) :** `weighted_avg_score`
> est NULL pour ~28% des étudiants (ceux qui n'ont soumis aucune évaluation
> notée). Ce n'est pas une erreur mais une caractéristique des données — une
> stratégie d'imputation ou un indicateur de valeur manquante est nécessaire,
> ne pas remplir naïvement par 0 ni supprimer les lignes.

> **Décision métier à confirmer :** `label_pass` traite actuellement
> `Withdrawn` comme `Fail` (→ 0). À valider avec Aymen (PO) et Abderahman
> avant l'entraînement (cf. data dictionary de Marouane).

### 4.2 `marts.dim_courses` (22 lignes, 5 règles)

| Règle | Justification |
|---|---|
| `course_presentation_id` non nul et unique | Clé de dimension |
| `code_module` non nul | Obligatoire |
| `code_presentation` au format `AAAA[B\|J]` | Format standard |
| `course_length_days` entre 1 et 365 | Durée réaliste (234-269) |

---

## 5. Contrôles de cohérence CROSS-TABLE

Au-delà de la validation table par table, quatre contrôles d'intégrité
référentielle vérifient la cohérence entre tables (couche staging) :

| Contrôle | Résultat |
|---|---|
| Chaque `id_assessment` de `student_assessment` existe dans `assessments` | ✅ 0 orphelin |
| Chaque étudiant de `student_info` a une inscription dans `student_registration` | ✅ 0 orphelin |
| Chaque `(code_module, code_presentation)` d'`assessments` existe dans `courses` | ✅ 0 orphelin |
| Chaque `(code_module, code_presentation)` de `vle` existe dans `courses` | ✅ 0 orphelin |

Aucune violation d'intégrité référentielle détectée : les clés étrangères sont cohérentes entre toutes les tables.

---

## 6. Synthèse des anomalies (dernier run)

| # | Couche | Table | Colonne | Sévérité | Description | Statut |
|---|---|---|---|---|---|---|
| 1 | Raw | `assessments` | `date` | 🟠 Moyenne | 5,3% de manquants, seuil = 2% | **pending** |
| 2 | Raw | `vle` | `week_from` | 🔴 Élevée | 82,4% de manquants | **pending** |
| 3 | Raw | `vle` | `week_to` | 🔴 Élevée | 82,4% de manquants | **pending** |

**Bilan global : 111 règles évaluées (41 raw + 34 staging + 4 cross-table + 32 marts), 108 réussies, 3 anomalies (toutes en couche raw, neutralisées ensuite en staging/marts).**

Détail complet horodaté dans [`quality_issues_log.csv`](../quality_issues_log.csv)
et rapports HTML dans [`docs/data_quality_reports/index.html`](data_quality_reports/index.html).

**Bonne nouvelle :** aucune anomalie ne subsiste en couche Marts. Les problèmes
détectés en Raw (`?` sur `assessments.date`, `vle.week_*`) ont bien été
neutralisés par le nettoyage dbt de Marouane (conversion en `NULL`), ce qui
valide la chaîne Raw → Staging → Marts.

## 7. Recommandations à l'équipe

- **Aymen (Ingestion)** : investiguer pourquoi `week_from`/`week_to` sont
  absents pour 82% des lignes de `vle` — probablement lié à la source OULAD
  elle-même, à confirmer.
- **Marouane (Transformation)** : nettoyage déjà bien fait ✅. Confirmer que
  la colonne `week_*` très incomplète est volontairement écartée des marts.
- **Abderahman (Modèle)** : gérer explicitement les ~28% de NULL sur
  `weighted_avg_score` (imputation ou indicateur), et valider la règle
  `label_pass` pour `Withdrawn`.

---

*Document mis à jour à chaque exécution du pipeline de validation
(`scripts/03_run_validation.py` pour la couche Raw,
`scripts/05_run_marts_validation.py` pour la couche Marts). Voir aussi le
journal `quality_issues_log.csv` pour l'historique horodaté.*
