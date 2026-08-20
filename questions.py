# test questions with the correct chunk id(s) they should be answered from.
# "gold" empty = question can't be answered from the corpus (tests that
# the system abstains instead of making something up)

test_questions = [
    {"q": "What must a regulated firm notify the Central Bank about regarding outsourcing arrangements?",
     "gold": ["CBI-OUT-2021::P13"]},
    {"q": "Does the Central Bank of Ireland's outsourcing guidance prescribe a fixed number of days' notice for notifying an outsourcing arrangement?",
     "gold": ["CBI-OUT-2021::P13"]},   # real answer: no, timing is not prescribed - good test of NOT inventing a number
    {"q": "What is the deadline for the initial notification of a major ICT incident under DORA?",
     "gold": ["EU-DORA-2022::Art19"]},
    {"q": "What annual contract value triggers escalation to the Group Outsourcing Committee?",
     "gold": ["INT-POL-ICT-07::5.2"]},
    {"q": "Under what condition may a regulated firm permit someone to perform a controlled function?",
     "gold": ["CBI-FP-S21::s21"]},
    {"q": "How often should firms review the fitness and probity of controlled function holders?",
     "gold": ["CBI-FP-S21::monitoring"]},

    # these can't be answered - not in the corpus
    {"q": "What is the minimum capital conservation buffer under CRD IV?", "gold": []},
    {"q": "How many branches must the firm keep open in each county?", "gold": []},
]
