# these strings are removed the titles of pages when they show up in lists
removed_title_strings = [
    "BA in ",
    "BS in ",
    "BSEd in ",
    "AA in ",
    "AS in ",
    "Minor in ",
    " Certificate",
    " Concentration",
    " License",
    " Endorsement",
    " Specialization"
]

# loops the Title strings list and removes any found word from the sentence
def _clean_title(sentence_string):
    output = sentence_string
    for word in removed_title_strings:
        output = sentence_string.replace(word,"")
        if output != sentence_string:
            return output
    return output