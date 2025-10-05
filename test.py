from duckduckgo_search import DDGS

query = input("What internships are you looking for?")

with DDGS() as ddgs:
    results = ddgs.text(query+" Internships opportunities", max_results=5)
    print("Extracted URLs:")
    for result in results:
        print(result['href'])

