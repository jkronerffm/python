#!/usr/bin/python3
import difflib, sys, re,os

class Fore:
    Black = '30'
    Red = '31'
    Green = '32'
    White = '37'

class Back:
    Black = '40'
    Red = '41'
    Green = '42'
    White = '48'

class Style:
    Normal = '0'
    Bold = '1'
    
class Color:
    Pattern='\x1B[{style};{fore};{back}m'

    Default = '\x1B[0m'

    def __init__(self, style, background, foreground):
        self.color = Color.Pattern.format(style=style, fore=foreground, back=background)

    def get(self):
        return self.color

    def __str__(self):
        return self.color
    
class Diff:
    
    rePattern = "@@\s+-((\d+),(\d+))\s+\+((\d+),(\d+))\s+@@(.*)$"
    prog = re.compile(rePattern)
    def __init__(self, leftFile = None, rightFile = None):
        self.leftFile = leftFile
        self.rightFile = rightFile
        self.colors = {
            " ": Color(style=Style.Normal, background=Back.White, foreground=Fore.Black),
            "+": Color(style=Style.Bold, background = Back.Green, foreground=Fore.White),
            "-": Color(style=Style.Bold, background = Back.Red, foreground=Fore.White)
        }
        self.leftLines = None
        self.rightLines = None
        self.diff = None
        self.result = []

    def addColor(self):
        return self.colors["+"]

    def removeColor(self):
        return self.colors["-"]

    def normalColor(self):
        return self.colors[" "]
    
    def setColor(self, name, color):
        self.colors[name] = color

    def setAddColor(self, color):
        self.setColor("+", color)
        
    def setRemoveColor(self, color):
        self.setColor("-", color)

    def setNormalColor(self, color):
        self.setColor(" ", color)

    def __getChangedLines(self,matching):
        m = self.prog.match(matching)
        if m == None:
            return None, None,None
        groups = m.groups()
        fromLine = int(groups[1])
        lineCount = int(groups[2])
        appending = groups[6]
        return fromLine, lineCount, appending

    def __getLinesFromFile(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        return lines

    def __pushToResult(self, fromIndex, toIndex, lines):
        index = fromIndex
        while index < toIndex:
            self.result.append(' ' + lines[index - 1])
            index = index + 1

    def __pushDiffToResult(self, fromIndex):
        i = fromIndex+1
        while  (i < len(self.diff)):
            currentDiff = self.diff[i]
            if currentDiff.startswith('@@'):
                break
            self.result.append(currentDiff)
            i = i + 1
        return i
        
    def __initLists(self):
        if self.leftFile != None:
            leftLines = self.__getLinesFromFile(self.leftFile)
            self.setLeftLines(leftLines)

        if (self.rightFile != None):
            rightLines = self.__getLinesFromFile(self.rightFile)
            self.setRightLines(rightLines)

        if (self.diff == None) and (self.leftLines != None and self.rightLines != None):
            diff = list(difflib.unified_diff(self.leftLines,self.rightLines,self.leftFile, self.rightFile))
            self.setDiff(diff)

    def setLeftLines(self, lines):
        self.leftLines = lines

    def setRightLines(self, lines):
        self.rightLines = lines

    def setDiff(self, diff):
        self.diff = diff
        
    def get(self):
        done = False
        i = 2
        leftIndex = 1
        self.__initLists()
        while i < len(self.diff):
            matching = self.diff[i]
            leftFrom, leftCount,appending = self.__getChangedLines(matching)
            if (leftFrom == None):
                break
            self.__pushToResult(leftIndex, leftFrom, self.leftLines)
            leftIndex = leftFrom + leftCount
            i = self.__pushDiffToResult(i)

        self.__pushToResult(leftIndex, len(self.leftLines), self.leftLines)

        done = len(self.result) > 0
        return done

    def __colorPrint(self, color, line):
        print(str(color) + line + Color.Default)

    def __showItem(self, line):
        self.__colorPrint(self.colors[line[0]], line.rstrip())

    def show(self, showFunc = None):
        if not self.get():
            return

        
        if (showFunc == None):
            os.system("")
            func = self.__showItem
        else:
            func=showFunc

        for line in self.result:
            func(line)
        
    
if __name__ == "__main__":     
    args = sys.argv[1:]
    print(args)
    diffs = Diff(args[0], args[1])
    diffs.show()
    
