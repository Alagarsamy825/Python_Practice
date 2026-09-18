import requests
import pandas as pd
import time
from datetime import datetime

top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"

# 5 categories
categories = {
    "AI": ["ai", "artificial intelligence", "machine learning", "gpt", "llm"],
    "Technology": ["technology", "tech", "software", "programming", "computer"],
    "Business": ["business", "startup", "company", "market", "finance"],
    "Science": ["science", "research", "space", "physics", "biology"],
    "Other": []
}

category_stories = {
    category: []
    for category in categories
}

def get_category(title):
    title = title.lower()

    for category, keywords in categories.items():
        if category == "Other":
            continue

        for keyword in keywords:
            if keyword in title:
                return category

    return "Other"


# Step 1: Get top story IDs
try:
    response = requests.get(top_stories_url, timeout=10)
    response.raise_for_status()
    story_ids = response.json()

except requests.RequestException as e:
    print(f"Failed to fetch top story IDs: {e}")
    story_ids = []

# Step 2: Fetch story details

for story_id in story_ids:

    # Stop once all 5 categories have 25 stories
    if all(len(category_stories[category]) >= 25 for category in categories):
        break

    story_url = (f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")

    try:
        story_response = requests.get(story_url, timeout=10)
        story_response.raise_for_status()
        story = story_response.json()

        # Skip deleted/dead/invalid stories
        if not story or story.get("type") != "story":
            continue

        title = story.get("title", "")
        category = get_category(title)

        # Don't add more than 25 stories
        if len(category_stories[category]) >= 25:
            continue

        story_data = {
            "post_id": story.get("id"),
            "title": story.get("title"),
            "category": category,
            "score": story.get("score", 0),
            "num_comments": story.get("descendants", 0),
            "author": story.get("by"),
            "collected_at": datetime.now().isoformat()
        }

        category_stories[category].append(story_data)

        print(
            f"{category}: "
            f"{len(category_stories[category])}/25 - "
            f"{title}"
        )

    except requests.RequestException as e:
        print(f"Failed to fetch story {story_id}: {e}")
        continue


# Step 3: Wait 2 seconds per category

stories = []

for category in categories:

    print(
        f"\n{category}: "
        f"{len(category_stories[category])} stories collected"
    )

    stories.extend(category_stories[category])

    # One sleep per category
    time.sleep(2)

# Step 4: Create DataFrame

df = pd.DataFrame(stories, columns=[
        "post_id",
        "title",
        "category",
        "score",
        "num_comments",
        "author",
        "collected_at"
    ]
)

print("\nTotal stories:", len(df))

print("\nStories by category:")
print(df["category"].value_counts())


# Step 5: Save CSV

df.to_csv(f"trends_{datetime.now().strftime('%Y-%m-%d')}.csv", index=False)

print("\nSuccessfully saved Trends.csv")