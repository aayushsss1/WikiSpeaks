import wikipedia

def get_wikipedia_content(search):
    wikipedia.set_lang("en")
    page_titles = wikipedia.search(search, results = 4) 
    summaries = []
    for page_title in page_titles[:4]:
        if wiki_page := wikipedia.page(title=page_title, auto_suggest=False):
            if summary := wiki_page.summary:
                summaries.append(summary)
    if not summaries:
        return "Sorry, nothing found on Wikipedia!"
    return "\n\n".join(summaries)