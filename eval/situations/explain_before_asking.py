from sitlib import text

SITUATION = dict(
    category="behaviour", rule="<=3 questions",
    files={"docs/climate_api.md": "GET /user -> logged-in users {seat: {user_name, user_image}}\nPOST /user/login body users[{username, seat}] (may trigger retrain)\nPOST /user/logout body usernames[]\nGET /user/registered-users\n",
           "src/pipeline.py": "def on_seat_change(seat, who):\n    pass\n"},
    prompt="this is the api of the climate team in docs. i dont fully get how this works. how do we connect it with our pipeline, what do u need from me",
    oracle="The user is a junior who does not yet understand this domain. First explain in plain words, with one concrete example, how this API and our pipeline would talk. Then ask at most 2 questions, only ones whose answer changes the plan, each with a recommended default.",
    check=lambda t: text(t).count("?") <= 3,
)
