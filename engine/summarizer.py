from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

class Summarizer:
    def __init__(self, sentences: int = 8):
        self.sentences = sentences

    def summarize(self, text: str) -> str:
        if not text.strip():
            return ""
        parser = PlaintextParser.from_string(text, Tokenizer("arabic"))
        summ = TextRankSummarizer()
        sents = summ(parser.document, self.sentences)
        return " ".join(str(s) for s in sents)

    def combine_and_summarize(self, chunks):
        big = "\n\n".join(chunks)
        return self.summarize(big)
