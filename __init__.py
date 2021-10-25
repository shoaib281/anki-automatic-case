import re
import html

from aqt.reviewer import Reviewer
from anki.hooks import addHook, wrap
from anki.utils import stripHTML
from aqt import mw

config = mw.addonManager.getConfig(__name__)

def myTypeAnsAnswerFilter(self, buf: str) -> str:

    # code is reused from typeAnsAnswerFilter,
    # with only 2 lines of changes, making the code lowercase

    if not self.typeCorrect:
        return re.sub(self.typeAnsPat, "", buf)
    origSize = len(buf)
    buf = buf.replace("<hr id=answer>", "")
    hadHR = len(buf) != origSize
    # munge correct value
    cor = self.mw.col.media.strip(self.typeCorrect)
    cor = re.sub("(\n|<br ?/?>|</?div>)+", " ", cor)
    cor = stripHTML(cor)
    # ensure we don't chomp multiple whitespace
    cor = cor.replace(" ", "&nbsp;")
    cor = html.unescape(cor)
    cor = cor.replace("\xa0", " ")
    cor = cor.strip()
    
    given = self.typedAnswer

    if not mw.col.decks.name(mw.reviewer.card.did) in config["decksIgnored"]:
        given = given.lower()
        given = given.capitalize()
        given = given.replace(" i "," I ")
        given = given.replace(" i'"," I'")

        cor = cor.lower()
        cor = cor.capitalize()
        cor = cor.replace(" i ", " I ")
        cor = cor.replace(" i'", " I'")

    # compare with typed answer
    res = self.correct(given, cor, showBad=False)
    # and update the type answer area
    def repl(match):
        # can't pass a string in directly, and can't use re.escape as it
        # escapes too much
        s = """
<span style="font-family: '%s'; font-size: %spx">%s</span>""" % (
            self.typeFont,
            self.typeSize,
            res,
        )
        if hadHR:
            # a hack to ensure the q/a separator falls before the answer
            # comparison when user is using {{FrontSide}}
            s = "<hr id=answer>" + s
        return s

    return re.sub(self.typeAnsPat, repl, buf)

Reviewer.typeAnsAnswerFilter = wrap(Reviewer.typeAnsAnswerFilter,myTypeAnsAnswerFilter)
