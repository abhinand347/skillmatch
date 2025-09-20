# api.py
from flask import Flask, request, jsonify
import jober  # your job logic
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# sessions per mode
sessions = {
    "chatty": {},
    "compact": {}
}

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    text = data.get("skills", "")
    mode = data.get("mode", "chatty")
    session_id = data.get("session_id")

    # if no session_id, make new
    if not session_id or session_id not in sessions[mode]:
        session_id = str(uuid.uuid4())
        sessions[mode][session_id] = {"step": "skills", "last_recs": []}

    state = sessions[mode][session_id]
    responses = []

    # --- STEP 1: handle skills input ---
    if state["step"] == "skills":
        extracted = jober.extract_skills_with_phrases(text)
        recs = jober.recommend_jobs(extracted)
        state["last_recs"] = recs

        if recs:
            bot_reply = jober.generate_human_like_recommendations(recs, mode)
            responses.append(bot_reply)
            responses.append("Did this job match your interest? (yes/no)")
            state["step"] = "feedback"
        else:
            responses.append("Sorry, I couldn't find any matching jobs. Try listing more skills or being more specific.")
            responses.append("Did this job match your interest? (yes/no)")
            state["step"] = "feedback"

    # --- STEP 2: handle feedback yes/no ---
    elif state["step"] == "feedback":
        if text.lower() == "yes":
            responses.append("Great! 🎉 Glad I could help you find a match.")
            state["step"] = "skills"
        elif text.lower() == "no":
            if len(state["last_recs"]) > 1:
                responses.append("Would you like to see another job suggestion? (yes/no)")
                state["step"] = "another"
            else:
                responses.append("Would you like to add more skills to improve matches? (yes/no)")
                state["step"] = "improve"
        else:
            responses.append("Please answer with 'yes' or 'no'.")

    # --- STEP 3: handle another suggestion ---
    elif state["step"] == "another":
        if text.lower() == "yes":
            recs = state["last_recs"]
            if len(recs) > 1:
                next_rec = recs[1]
                responses.append(
                    f"You might also want to check out the {next_rec['title']} role at {next_rec['company']}, "
                    f"which values skills like {', '.join(next_rec['matched_skills'])}."
                )
            state["step"] = "skills"
        elif text.lower() == "no":
            responses.append("Would you like to add more skills to improve matches? (yes/no)")
            state["step"] = "improve"
        else:
            responses.append("Please answer with 'yes' or 'no'.")

    # --- STEP 4: handle improve skills ---
    elif state["step"] == "improve":
        if text.lower() == "yes":
            responses.append("Sure! Please enter the additional skills you'd like to add.")
            state["step"] = "skills"
        elif text.lower() == "no":
            responses.append("Okay, thanks for your feedback. We’ll keep improving! 🙏")
            state["step"] = "skills"
        else:
            responses.append("Please answer with 'yes' or 'no'.")

    # save session
    sessions[mode][session_id] = state

    return jsonify({
        "session_id": session_id,
        "responses": responses
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)

