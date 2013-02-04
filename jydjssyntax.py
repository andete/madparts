# based on the pyside C++ syntax highlighting example
# that in itself is based on the C++ example
# see http://qt.gitorious.org/pyside/pyside-examples/blobs/9edeedb37163e71a0040417169ca9aae9e7e6e83/examples/richtext/syntaxhighlighter.py

from PySide import QtGui, QtCore

class JSHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(JSHighlighter, self).__init__(parent)
        # keywords
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.darkCyan)
        keywordPatterns = [
            "TODO", 
            "FIXME", 
            "XXX",
            "TBD",
            "if", 
            "else",
            "switch",
            "while", 
            "for", 
            "do", 
            "in",
            "break",
            "continue", 
            "new",
            "delete",
            "instanceof", 
            "typeof",
            "return",
            "with",
            "true",
            "false",
            "null", 
            "undefined",
            "arguments",
            "case",
            "default",
            "try",
            "finally",
            "throw",
            "alert",
            "confirm",
            "prompt",
            "status",
            "document",
            "event",
            "location",
            "[",
            "]",
            "{",
            "}",
            "function",
            "var",
            "let",
            "this",
            ]
        self.highlightingRules = [(QtCore.QRegExp("\\b"+pattern+"\\b"), keywordFormat) for pattern in keywordPatterns]
        # statements
        statementFormat = QtGui.QTextCharFormat()
        statementFormat.setForeground(QtCore.Qt.darkRed)
        statementFormat.setFontWeight(QtGui.QFont.Bold)
        statementPatterns = [
               "return",
               "with",
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
