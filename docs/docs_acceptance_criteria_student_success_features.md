# Critères d'acceptation — Epic Transformation & Qualité des données

## Livrable : `marts.student_success_features`

**Statut : ACCEPTÉ avec conditions** (Product Owner : Aymen — 09/07/2026)

### Décision 1 — Définition de `label_pass`

**Contexte :** Marouane (dbt) a signalé que traiter `Withdrawn` comme `Fail` (0)
dans `label_pass` est une décision produit à valider, pas un fait technique.

**Décision :**
- `label_pass` reste tel quel : `Withdrawn` = 0 (même traitement que `Fail`).
  Justification : un décrochage constitue un échec du parcours au regard de
  l'objectif "réussite universitaire" — le système doit pouvoir alerter tôt
  sur ce risque, peu importe la cause finale (échec académique ou abandon).
- **Action complémentaire demandée à Marouane :** ajouter une colonne
  `label_pass_excl_withdrawn` (exclut les Withdrawn), afin qu'Abderahman
  (ML) puisse comparer empiriquement les deux formulations de la cible
  avant de figer le choix définitif pour l'entraînement.

**Critère d'acceptation :**
- [ ] La table `marts.student_success_features` contient les deux colonnes :
  `label_pass` et `label_pass_excl_withdrawn`
- [ ] Les deux colonnes sont documentées dans le data dictionary
- [ ] Abderahman confirme avoir testé les deux variantes avant sélection du modèle final

---

### Décision 2 — Traitement des valeurs manquantes dans `weighted_avg_score`

**Contexte :** `weighted_avg_score` est NULL pour ~28% des étudiants
(aucune évaluation notée soumise). Marouane a explicitement demandé une
stratégie d'imputation documentée plutôt qu'un remplissage silencieux.

**Décision :**
- Pas de zero-fill silencieux (fausserait le signal : "n'a rien soumis"
  ≠ "a eu un 0").
- Ajouter une colonne indicateur binaire `has_scored_assessment` (0/1).
- Imputer `weighted_avg_score` avec une valeur neutre documentée
  (médiane du dataset, ou repli sur `avg_score`) **en complément** de
  l'indicateur, jamais à sa place.

**Critère d'acceptation :**
- [ ] La colonne `has_scored_assessment` est présente dans la table finale
- [ ] La méthode d'imputation choisie est documentée dans le data dictionary
  (valeur utilisée + justification)
- [ ] Aucun zero-fill silencieux n'est appliqué sans l'indicateur associé

---

### Décision 3 — Gestion des `'?'` dans les données brutes OULAD

**Statut : déjà traité, validé sans réserve.**

Confirmé par Marouane : tous les `'?'` du raw OULAD (dans `assessments.date`,
`student_registration.date_registration`/`date_unregistration`,
`student_assessment.score`, `vle.week_from`/`week_to`,
`student_info.imd_band`) sont convertis en `NULL` réels dès l'étape staging.
Le formatage de `imd_band` est également standardisé (toujours avec `%`).

**Critère d'acceptation :**
- [x] Aucune valeur `'?'` littérale ne subsiste dans les colonnes en aval de staging
- [x] `imd_band` a un format cohérent sur toute la table

---

## Prochaine étape
Sprint Review : valider avec Marouane et Abderahman que les colonnes
`label_pass_excl_withdrawn` et `has_scored_assessment` sont bien ajoutées
avant le passage à l'entraînement du modèle (Epic MLOps / Machine Learning).
