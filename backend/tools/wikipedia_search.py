import wikipedia
from langchain.tools import tool

@tool
def wikipedia_search(query : str)-> str:
    '''Search wikipedia and return summary of the topic'''
    print(f"[Tool Called Wikipedia] for {query}")
    
    try:
        summary = wikipedia.summary(query, sentences=5)
        return summary
    
    except wikipedia.DisambiguationError as e:
        try:
            summary = wikipedia.summary(e.options[0], sentences=5)
            return summary
        except:
            return f"Disambiguation error. Options: {', '.join(e.options[:5])}"
    
    except wikipedia.PageError:
        return f"No Wikipedia page found for: {query}"
    except Exception as e:
        return f"Wikipedia error: {str(e)}"