# regulatory documents to test the pipeline on.
#
# most of these are REAL excerpts from published Irish/EU regulatory
# sources, kept short and cited to where they came from. one document
# (the internal ICT policy) is invented, because a real internal bank
# policy obviously isn't published anywhere - it's clearly marked as
# such below. this mix (some real, one illustrative) is more honest than
# either an all-fake corpus or pretending to have a real internal
# document I don't actually have access to.

docs = [
    {
        "id": "CBI-OUT-2021",
        "title": "Cross-Industry Guidance on Outsourcing",
        "source": "Central Bank of Ireland, December 2021 - centralbank.ie/docs/default-source/publications/consultation-papers/cp138/cross-industry-guidance-on-outsourcing.pdf",
        "date": "2021-12-17",
        "current": True,
        "public": True,
        "sections": {
            "P13": (
                "Notify the Central Bank of planned critical or important outsourcing "
                "arrangements and of material changes to existing critical or important "
                "outsourcing arrangements. The Central Bank has clarified that notification "
                "of such proposed arrangements does not constitute a pre-approval process "
                "and specific timings in respect of the submission of notifications are not "
                "prescribed unless required by existing regulation."
            ),
            "P14": (
                "Develop and maintain an outsourcing register to include prescribed "
                "information for all existing and future outsourcing arrangements."
            ),
        }
    },
    {
        # this is the CONSULTATION PAPER that came before the guidance above -
        # a real, genuinely-superseded document, used to test the "exclude
        # non-current documents" filter
        "id": "CBI-CP138-2021",
        "title": "CP138 - Consultation on Cross-Industry Guidance on Outsourcing",
        "source": "Central Bank of Ireland - centralbank.ie/publication/consultation-papers/cp138",
        "date": "2021-01-01",
        "current": False,   # superseded by the finalised Guidance (CBI-OUT-2021) above
        "public": True,
        "sections": {
            "1.1": (
                "The Cross-Industry Guidance on Outsourcing outlines the Central Bank of "
                "Ireland's expectations regarding the management of outsourcing risk, with "
                "a view to promoting higher standards of operational resilience in "
                "regulated financial service providers."
            ),
        }
    },
    {
        "id": "EU-DORA-2022",
        "title": "Regulation (EU) 2022/2554 (DORA), Article 19 - reporting of major ICT-related incidents",
        "source": "EUR-Lex, OJ L 333, 27.12.2022; timings per Commission Delegated Regulation (EU) 2025/301, Art. 5",
        "date": "2025-01-17",   # date DORA became directly applicable across the EU
        "current": True,
        "public": True,
        "sections": {
            "Art19": (
                "Financial entities shall report major ICT-related incidents to the "
                "relevant competent authority. The initial notification shall be "
                "submitted as early as possible, in any case within four hours from "
                "classification of the incident as major, and no later than 24 hours "
                "from the moment the financial entity became aware of the incident. "
                "The intermediate report shall be submitted at the latest within 72 "
                "hours from the submission of the initial notification. The final "
                "report shall be submitted no later than one month after the "
                "intermediate report."
            ),
        }
    },
    {
        # NOT a real document - there is no public version of any bank's
        # internal ICT policy, so this one is invented to represent what
        # such a policy might contain. kept clearly separate from the real
        # documents above, and marked internal/non-public so the access
        # control filter has something real to test.
        "id": "INT-POL-ICT-07",
        "title": "[ILLUSTRATIVE, NOT A REAL DOCUMENT] Internal Policy: ICT Third-Party Risk",
        "source": "invented for this project - represents a fictional bank's internal policy",
        "date": "2024-06-01",
        "current": True,
        "public": False,     # internal only - used to test access control
        "sections": {
            "5.2": (
                "Any outsourcing arrangement with an annual contract value exceeding "
                "EUR 250,000 must be escalated to the Group Outsourcing Committee "
                "before contract signature."
            ),
            "6.1": (
                "An ICT incident is classified as major if it affects more than 10 "
                "percent of active retail customers or causes an outage exceeding 2 hours."
            ),
        }
    },
    {
        "id": "CBI-FP-S21",
        "title": "Fitness and Probity - Central Bank Reform Act 2010, s.21(1) and CBI Guidance",
        "source": "Central Bank Reform Act 2010, s.21(1); Guidance on the Standards of Fitness and Probity, centralbank.ie",
        "date": "2025-11-20",
        "current": True,
        "public": True,
        "sections": {
            "s21": (
                "A regulated financial service provider shall not permit a person to "
                "perform a controlled function unless the regulated financial service "
                "provider is satisfied on reasonable grounds that the person complies "
                "with any standard of fitness and probity in a code issued under "
                "section 50, and the person has agreed to comply with any such standard."
            ),
            "monitoring": (
                "Firms are required to monitor on an ongoing basis the fitness and "
                "probity of persons performing controlled functions, and are expected "
                "to carry out this review on at least an annual basis."
            ),
        }
    }
]
