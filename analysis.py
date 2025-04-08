import requests
import re
from collections import Counter
import json

NEGATION_WORDS = {
    "no", "not", "never", "none", "neither", "nor",
    "without", "absent", "except", "deny", "denied", "refuse", "refused",
    "exclude", "excluded", "excludes", "exclusion", "ineligible", "invalid",
    "prohibit", "prohibited", "prohibition",
    "ban", "banned", "bar", "bars", "barred",
    "unlawful", "unauthorized", "unauthorised",
    "forbidden", "disallowed", "void",
    "cannot", "can't", "won't"
}

PERMISSIVE_TERMS = {
    "may", "can", "allowed", "permitted", "authorized", "entitled"
}

NEGATED_MODAL_PATTERNS = [
    r"\bmay not\b",
    r"\bshall not\b",
    r"\bmust not\b",
    r"\bcan not\b",
    r"\bis not allowed\b",
    r"\bis not authorized\b",
    r"\bis prohibited\b"
]

def fetch_latest_titles_info():
    """Fetch title numbers, names, and their most recent issue dates."""
    titles_info_url = "https://www.ecfr.gov/api/versioner/v1/titles"
    response = requests.get(titles_info_url)
    response.raise_for_status()
    titles_data = response.json()
    
    titles_info = {
        str(title['number']): {
            'date': title['latest_issue_date'],
            'name': title['name']
        }
        for title in titles_data['titles']
        if not title['reserved'] and title['latest_issue_date']
    }
    return titles_info

def count_words(text):
    text = text.lower().replace("cannot", "can not")

    words = re.findall(r"\b\w+'\w+|\w+\b", text)
    no_counter = Counter(word for word in words if word in NEGATION_WORDS)
    yes_counter = Counter(word for word in words if word in PERMISSIVE_TERMS)

    negated_permission_count = 0
    for pattern in NEGATED_MODAL_PATTERNS:
        negated_permission_count += len(re.findall(pattern, text))

    total_yes = max(sum(yes_counter.values()) - negated_permission_count, 0)
    total_no = sum(no_counter.values())

    return no_counter, yes_counter, total_no, total_yes

def fetch_and_process_title(title_num, date):
    url = f"https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title_num}.xml"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return count_words(response.text)
    except Exception as e:
        print(f"Error on Title {title_num}: {e}")
        return Counter(), Counter(), 0, 0

def aggregate_titles_with_metadata():
    titles_info = fetch_latest_titles_info()
    results = []
    total_no = Counter()
    total_yes = Counter()
    sum_total_no = 0
    sum_total_yes = 0

    for title_num, meta in titles_info.items():
        print(f"Processing Title {title_num} - {meta['name']} ({meta['date']})...")
        no_count, yes_count, no_total, yes_total = fetch_and_process_title(title_num, meta['date'])

        results.append({
            "title": int(title_num),
            "name": meta['name'],
            "no_word_counts": dict(no_count),
            "yes_word_counts": dict(yes_count),
            "total_no": no_total,
            "total_yes": yes_total
        })

        total_no.update(no_count)
        total_yes.update(yes_count)
        sum_total_no += no_total
        sum_total_yes += yes_total

    # Add aggregate record
    results.append({
        "title": "0",
        "name": "All Federal Regulation",
        "no_word_counts": dict(total_no),
        "yes_word_counts": dict(total_yes),
        "total_no": sum_total_no,
        "total_yes": sum_total_yes
    })

    return results

# Run the aggregation
final_json_result = aggregate_titles_with_metadata()
final_json_result[:2]  # Preview first few entries
with open("output.json", "w") as f:
    json.dump(final_json_result, f, indent=2)

print("\n✅ Results written to output.json")
