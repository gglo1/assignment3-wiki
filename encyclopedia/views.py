from django.shortcuts import render
from markdown2 import Markdown
from django import forms
import random
from django.http import HttpResponse, HttpResponseRedirect
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

markdowner = Markdown()

class SearchForm(forms.Form): #create a search form layout
    query = forms.CharField(max_length=100)

class CreateForm(forms.Form): #create a form for new page
    title = forms.CharField(label="Entry Name")
    content = forms.CharField(label="Contents (Include # followed by the title if bolded title desired)", widget=forms.Textarea(attrs={'rows': 10, 'cols': 50}))

class EditForm(forms.Form): #create an edit page
    title = forms.CharField(label="Entry for")
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 50}))
    
def entry(request, title): #switch to show specified page
    f = util.get_entry(title) #check if page exists
    if f is None:
        form = SearchForm()
        content = "No matches were found" #shows the error page
        return render(request, "encyclopedia/error.html", {"form": form, "content": content})
    else:
        form = SearchForm()
        wikicontent = util.get_entry(title) 
        htmlcontent = markdowner.convert(wikicontent) #convert markdown data to html
        return render(request, "encyclopedia/entry.html", {"title": title, "content": htmlcontent, "form": form})


def search(request): #display user's searched page or list of relevant results
    if request.method == "POST": #active page search
        form = SearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.get("query")
            present = False
            for entry in util.list_entries():
                if data.lower() == entry.lower(): #to make case insensitive
                    wikicontent = util.get_entry(data)
                    htmlcontent = markdowner.convert(wikicontent)
                    present = True
                    break
            if present: #display if page is found
                return render(request, "encyclopedia/entry.html", {"content": htmlcontent, "form": form, "title": data})
            else: #otherwise check substrings
                listE = []
                for entry in util.list_entries():
                    index = entry.lower().find(data.lower()) #to make case insensitive for search
                    if index  != -1:
                        listE.append(entry)
                if len(listE) == 0: #display error page if no relevant content is found
                    form = SearchForm()
                    content = "The page you requested was not found"
                    return render(request, "encyclopedia/error.html", {'form': form, "content": content})
                else: #list pages with relevant substrings found
                    return render(request, "encyclopedia/index.html", {"entries": listE, "form": form})
    else: #otherwise display error page
        return render(request, "encyclopedia/error.html", {'form': form, "content": content})


def create(request): #create a new page
    if request.method == "POST":
        createform = CreateForm(request.POST)
        if createform.is_valid():
            title = createform.cleaned_data.get("title")
            body = createform.cleaned_data.get("content")
            present = False
            for entry in util.list_entries():
                if title.lower() == entry.lower(): #case insensitive
                    present = True
                    break
            if present: #check if page exists
                content = "This page already exists."
                form = SearchForm()
                return render(request, "encyclopedia/error.html", {'form': form, "content": content})
            else: #create page if it doesn't exist
                util.save_entry(title, body)
                form = SearchForm()
                wikicontent = util.get_entry(title)
                htmlcontent = markdowner.convert(wikicontent)
                return render(request, "encyclopedia/entry.html", {"title": title, "content": htmlcontent, "form": form})
    else: #GET method 
        form = SearchForm()
        createform = CreateForm()
        return render(request, "encyclopedia/create.html", {"form": form, "createform": createform})


def edit(request, title): #edit a specified page
    if request.method == "POST":
        editform = EditForm(request.POST)
        if editform.is_valid():
            title = editform.cleaned_data.get("title")
            body = editform.cleaned_data.get("content")
            util.save_entry(title, body) #saves new content
            form = SearchForm()
            htmlcontent = markdowner.convert(body)
            return render(request, "encyclopedia/entry.html", {
                "title": title, "content": htmlcontent, "form": form
            })
    else:
        form = SearchForm()
        editform = EditForm({"title": title, "body": util.get_entry(title)})
        return render(request, "encyclopedia/edit.html", {"form": form, "editform": editform})


def rand(request): #displays random page from encylcopedia
    entries = util.list_entries()
    num = len(entries)
    entry = random.randint(0, num-1) #generates a random number for entry selection
    title = entries[entry]
    wikicontent = util.get_entry(title)
    htmlcontent = markdowner.convert(wikicontent)
    form = SearchForm()
    return render(request, "encyclopedia/rand.html", {"form": form, "title": title, "content": htmlcontent})