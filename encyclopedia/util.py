import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def parse(title):
    try:
        # return Markdown().convert(get_entry(title))
        f = open(f"entries/{title}.md")
        html = ""
        for line in f:
            thisline=line
            # Parsing Markdown to html
            # checking for list
            if (thisline[0] == "-" or thisline[0] == "+" or thisline[0] == "*")\
            and thisline[1] == " ":
                mylist = ""
                while (thisline[0] == "-" or thisline[0] == "+" or thisline[0] == "*")\
                and thisline[1] == " ":
                    mylist += f"<li>{thisline[2:]}</li>"
                    thisline = next(f,None)
                html += f"\n<ul>{mylist}</ul>\n"
            thisline = parsePara(thisline)
            thisline = parseBold(thisline)
            thisline = parseHeadings(thisline)
            thisline = parseLinks(thisline)
            html += thisline
        f.close()
        return html
    except:
        return None

def parseHeadings(line):
    if line[0] == "#" and line[1] == " ":
        return f"<h1>{line[2:-1]}</h1>\n"
    elif line[0] == "#" and line[1] == "#" and line[2] == " ":
        return f"<h3>{line[3:-1]}</h3>\n"
    elif line[0] == "#" and line[1] == "#" and line[2] == "#" and line[3] == " ":
        return f"<h5>{line[4:-1]}</h5>\n"
    else: return line

def parseBold(line):
    i=0
    tempa=0
    tempb=0
    starta=True
    startb=True
    while i < len(line)-1:
        if (line[i] == "*" and line[i+1] == "*"):
            if starta:
                tempa=i
                starta = False
            else:
                part1=line[:tempa]
                part2=line[tempa+2:i]
                part3=line[i+2:]
                line = f"{part1}<b>{part2}</b>{part3}"
                starta = True
        elif (line[i] == "_" and line[i+1] == "_"):
            if startb:
                tempb=i
                startb = False
            else:
                part1=line[:tempb]
                part2=line[tempb+2:i]
                part3=line[i+2:]
                line = f"{part1}<b>{part2}</b>{part3}"
                startb = True
        i += 1
    return line

def parseLinks(line):
    while True:
        x=re.search("\]\(", line)
        if x == None:
            return line
        i=x.span()[0]-1
        j=x.span()[1]
        name=""
        href=""
        while line[i] != "[":
            name = line[i]+name
            i-=1
        while line[j] != ")":
            href += line[j]
            j+=1
        link = f"<a href=\"{href}\">{name}</a>"
        line = f"{line[:i]}{link}{line[j+1:]}"

def parsePara(line):
    if line[0].isalpha():
        return f"<p>{line}</p>"
    else:
        return line