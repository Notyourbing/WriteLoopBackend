# app/data/writing_corpus.py
"""
Mock corpus of IELTS / CET-6 high-scoring sentence continuations.
Each entry is a natural phrase that commonly follows certain contexts.
"""

WRITING_CORPUS = [
    # Technology
    "has revolutionized the way we communicate and work",
    "brings both unprecedented opportunities and significant challenges",
    "can lead to social isolation if not used responsibly",
    "enhances learning efficiency through personalized content",

    # Environment
    "requires immediate action from governments and individuals alike",
    "is a pressing global issue that demands collective efforts",
    "can be mitigated through sustainable practices and innovation",
    "poses a serious threat to biodiversity and ecosystem stability",

    # Education
    "fosters critical thinking and independent learning skills",
    "should emphasize practical application over rote memorization",
    "plays a pivotal role in shaping future societal leaders",
    "must be accessible to all regardless of socioeconomic background",

    # Society / Policy
    "calls for comprehensive legislation and public awareness campaigns",
    "is instrumental in promoting social equity and justice",
    "can significantly reduce inequality if properly implemented",
    "demands a balanced approach between freedom and regulation",

    # General Academic
    "is supported by a growing body of empirical evidence",
    "remains a subject of intense debate among scholars",
    "can be attributed to a confluence of historical and economic factors",
    "warrants further investigation to fully understand its implications",
    "is widely regarded as a cornerstone of modern society"
]


def get_writing_corpus():
    return WRITING_CORPUS