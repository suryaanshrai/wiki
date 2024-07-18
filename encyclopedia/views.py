from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms

from . import util
from random import randint

class searchForm(forms.Form):
    q = forms.CharField(label="",widget=forms.TextInput(attrs={
        'autocomplete':'off', 'placeholder':'Search Encyclopedia'}))

class newPageForm(forms.Form):
    title = forms.CharField(label="Title")
    entry = forms.CharField(label="Entry",widget=forms.Textarea(attrs={
        "placeholder":"Enter page entry here"
        }))

class newEditForm(forms.Form):
    content = forms.CharField(label="Edit Page", widget=forms.Textarea(attrs={
    }))


defaultData = {
    "searchForm":searchForm()
}

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    }|defaultData)

def entry(request, title):
    entryhtml = util.parse(title)
    if (entryhtml == None):
        return error(request, "Entry not found")
    else:
        return render(request, "encyclopedia/entry.html", {
            "content": entryhtml,
            "title":title
        }|defaultData)

def search(request):
    if request.method == "POST":
        form = searchForm(request.POST)
        if form.is_valid():
            q = form.cleaned_data["q"]
            entries = util.list_entries()
            results=set()
            for entry in entries:
                if q.lower() == entry.lower():
                    return HttpResponseRedirect(reverse("entry", args=[entry]))
                elif q.lower() in entry.lower():
                    results.add(entry)
            if len(results) == 0:
                return error(request, "No results for this query")
            else:
                return render(request, "encyclopedia/search.html", {
                    "results":results
                }|defaultData)

    return HttpResponseRedirect(revere("index"))

def newPage(request):
    if request.method == "POST":
        form = newPageForm(request.POST)
        if form.is_valid():
            title=form.cleaned_data["title"]
            entry=form.cleaned_data["entry"]
            entries=util.list_entries()
            if title in entries:
                return error(request,"An entry with same title already exists")
            else:
                util.save_entry(title, entry)
                return HttpResponseRedirect(reverse("entry", args=[title]))
    else:
        return render(request, "encyclopedia/newPage.html", {
            "form":newPageForm()
        }|defaultData)

def edit(request, title):
    if request.method == "POST":
        form=newEditForm(request.POST)
        if form.is_valid():
            content=form.cleaned_data["content"]
            if title in util.list_entries():
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse("entry", args=[title]))
            else:
                return error(request, "Entry does not exist")
    return render(request, 'encyclopedia/editPage.html', {
        "content" : util.get_entry(title),
        "form" : newEditForm(initial={"content":util.get_entry(title)}),
        "title" : title
    })


def random(request):
    entries=util.list_entries()
    return HttpResponseRedirect(reverse("entry", args=[entries[randint(0,len(entries)-1)]]))

def error(request, message):
    return render(request, "encyclopedia/error.html", {
            "message": message,
        }|defaultData)