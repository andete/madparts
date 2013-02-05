# based on the pyside C++ syntax highlighting example
# that in itself is based on the C++ example
# see http://qt.gitorious.org/pyside/pyside-examples/blobs/9edeedb37163e71a0040417169ca9aae9e7e6e83/examples/richtext/syntaxhighlighter.py
# inspiration gotten from coffee.vim 
# http://www.vim.org/scripts/script.php?script_id=3590

from PySide import QtGui, QtCore

class CoffeeHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(CoffeeHighlighter, self).__init__(parent)
        # keywords
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.darkCyan)
        keywordPatterns = [

            # repeat
            "for",
            "while", 
            "until",
            "loop",

            # conditional
            "if", 
            "else",
            "switch",
            "unless"
            "when",
            "then",

            # exception
            "try",
            "catch",
            "finally",

            # keyword
            "new",
            "in",
            "of",
            "by",
            "and",
            "or",
            "not",
            "is",
            "isnt",
            "class",
            "extends",
            "super",
            "do", 
  
            # own; special case: TODO
            "own",

            # operator
            "instanceof",
            "typeof",
            "delete",
 
            # boolean
            "true",
            "on",
            "yes",
            "false",
            "off",
            "no",

            # global
            "null",
            "undefined",

            # special vars
            "this",
            "prototype",
            "arguments",

            # TODO
            "TODO", 
            "FIXME", 
            "XXX",
            "TBD",
            ]
        self.highlightingRules = [(QtCore.QRegExp("\\b"+pattern+"\\b"), keywordFormat) for pattern in keywordPatterns]
        opFormat = QtGui.QTextCharFormat()
        opFormat.setForeground(QtCore.Qt.blue)
        self.highlightingRules = self.highlightingRules + [(QtCore.QRegExp(pattern), opFormat) for pattern in ['\(', '\)', '\[', '\]', '\{', '\}']]

        # statements
        statementFormat = QtGui.QTextCharFormat()
        statementFormat.setForeground(QtCore.Qt.darkRed)
        statementFormat.setFontWeight(QtGui.QFont.Bold)
        statementPatterns = [
               "return",
               "break",
               "continue",
               "throw",
            ] 
        self.highlightingRules = self.highlightingRules +  [(QtCore.QRegExp("\\b"+pattern+"\\b"), statementFormat) for pattern in statementPatterns]
        # types
        typeFormat = QtGui.QTextCharFormat()
        typeFormat.setForeground(QtCore.Qt.darkGreen)
        typeFormat.setFontWeight(QtGui.QFont.Bold)
        typePatterns = [
               "Array",
               "Boolean",
               "Date",
               "Function",
               "Number",
               "Object",
               "String",
               "RegExp",
            ] 
        self.highlightingRules = self.highlightingRules +  [(QtCore.QRegExp("\\b"+pattern+"\\b"), typeFormat) for pattern in typePatterns]
        # class
        classFormat = QtGui.QTextCharFormat()
        classFormat.setFontWeight(QtGui.QFont.Bold)
        classFormat.setForeground(QtCore.Qt.darkGreen)
        self.highlightingRules.append((QtCore.QRegExp("\\bQ[A-Za-z]+\\b"),
                classFormat))
        # // comment
        singleLineCommentFormat = QtGui.QTextCharFormat()
        singleLineCommentFormat.setForeground(QtCore.Qt.red)
        self.highlightingRules.append((QtCore.QRegExp("//[^\n]*"),
                singleLineCommentFormat))

        # quotation
        quotationFormat = QtGui.QTextCharFormat()
        quotationFormat.setForeground(QtCore.Qt.magenta)
        m1 = QtCore.QRegExp("\"[^\"]*\"")
        self.highlightingRules.append((m1, quotationFormat))
        m2 = QtCore.QRegExp("\'[^\']*\'")
        self.highlightingRules.append((m2, quotationFormat))
        # function
        # functionFormat = QtGui.QTextCharFormat()
        # functionFormat.setFontItalic(True)
        # functionFormat.setForeground(QtCore.Qt.blue)
        # self.highlightingRules.append((QtCore.QRegExp("\\b[A-Za-z0-9_]+(?=\\()"),
        #         functionFormat))
        # /* comment */
        self.multiLineCommentFormat = QtGui.QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QtCore.Qt.red)
        self.commentStartExpression = QtCore.QRegExp("/\\*")
        self.commentEndExpression = QtCore.QRegExp("\\*/")

    def highlightBlock(self, text):
        # first apply basic rules
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        # then do special stuff for multiline
        self.setCurrentBlockState(0)
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)
        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = text.length() - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()
            self.setFormat(startIndex, commentLength,
                    self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text,
                    startIndex + commentLength);
