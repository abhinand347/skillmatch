# jober.py
import spacy
import pandas as pd
import random

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Prompts
chatty_skill_prompts = [
    "Let's see what you're made of! 🚀 Drop your skills below.",
    "Brag a little 😊 — what skills do you have?",
    "Go ahead — tell me your awesome skills! I'll find the right job for you. 😎",
    "Tech wizard? Team player? Fast typer? Tell me everything! ✨",
    "Give me your skills — I'll give you your future. 🔮",
    "You can write your skills however you want — a sentence, list, or even a paragraph.",
    "What kind of skills do you have? Type however you like!",
    "Tell me your skills — I'm all ears. 🎧",
    "Just describe your skills in your own words — I'll do the rest!"
]

compact_skill_prompts = [
    "Input your skill set to initiate recommendation protocols...",
    "Job matching engine engaged. Awaiting input of your skillset...",
    "Processing unit is active. Kindly enter the skills you possess..."
]

# === Load skills from CSV ===
def load_known_skills_from_csv(jobs_csv="jobs.csv"):
    try:
        jobs = pd.read_csv(jobs_csv)
        known_skills = set()
        for skills_str in jobs["skills"]:
            skills = [skill.strip().lower() for skill in skills_str.split(",")]
            known_skills.update(skills)
        return known_skills
    except Exception:
        return {"python", "sql", "excel", "javascript", "html", "css"}

known_skills_set = load_known_skills_from_csv()

# === Extract skills ===
def extract_skills_with_phrases(text):
    doc = nlp(text)
    skills = set()

    for chunk in doc.noun_chunks:
        phrase = chunk.text.lower().strip()
        if phrase in known_skills_set:
            skills.add(phrase)

    for token in doc:
        word = token.text.lower().strip()
        if word in known_skills_set:
            skills.add(word)

    return list(skills)

# === Recommend jobs ===
def recommend_jobs(extracted_skills, jobs_csv="jobs.csv"):
    try:
        jobs = pd.read_csv(jobs_csv)
    except Exception:
        jobs = pd.DataFrame({
            "title": ["Data Analyst", "Web Developer", "ML Engineer"],
            "company": ["ABC Corp", "TechSoft", "AI Labs"],
            "skills": ["python, sql, excel", "html, css, javascript", "python, machine learning"]
        })

    recommendations = []
    for _, job in jobs.iterrows():
        job_skills = [skill.strip().lower() for skill in job["skills"].split(",")]
        matched = set(extracted_skills).intersection(job_skills)
        if matched:
            recommendations.append({
                "title": job["title"],
                "company": job["company"],
                "matched_skills": list(matched),
                "match_count": len(matched)
            })

    recommendations.sort(key=lambda x: x["match_count"], reverse=True)
    return recommendations

# === Generate chatbot response ===
def generate_human_like_recommendations(recommendations, mode="chatty"):
    if not recommendations:
        return "Sorry, I couldn't find any matching jobs. Try listing more skills."

    if mode == "chatty":
        top = recommendations[0]
        skills_str = ", ".join(top["matched_skills"])
        response = f"Based on your skills in {skills_str}, you'd be a great fit for the {top['title']} role at {top['company']}."

        if len(recommendations) > 1:
            second = recommendations[1]
            response += f" You might also check out the {second['title']} role at {second['company']}."

        return response

    else:  # compact
        jobs_list = [f"{rec['title']} at {rec['company']} ({len(rec['matched_skills'])} skills matched)"
                     for rec in recommendations[:5]]
        return "Top matches:\n" + "\n".join(jobs_list)

# ✅ Only runs if you type: python jober.py (not when Flask imports it)
if __name__ == "__main__":
    print("Standalone test mode.\n")
    user_input = input("Enter your skills: ")
    extracted = extract_skills_with_phrases(user_input)
    recs = recommend_jobs(extracted)
    print(generate_human_like_recommendations(recs, "chatty"))
