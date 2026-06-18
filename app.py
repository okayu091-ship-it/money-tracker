from flask import Flask, render_template, request, redirect, url_for
import json
import os
import datetime

app = Flask(__name__)
DATA_FILE = "transactions.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"person_a": "Aさん", "person_b": "Bさん", "transactions": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def calc_balance(data):
    a = data["person_a"]
    net = 0
    for t in data["transactions"]:
        if t["payer"] == a:
            net += t["amount"]
        else:
            net -= t["amount"]
    return net


@app.route("/")
def index():
    data = load_data()
    a = data["person_a"]
    b = data["person_b"]
    net = calc_balance(data)
    today = datetime.date.today().strftime("%Y-%m-%d")

    sorted_transactions = [
        (actual_index, t, t.get("receiver", b if t["payer"] == a else a))
        for actual_index, t in sorted(
            enumerate(data["transactions"]), key=lambda x: x[1]["date"]
        )
    ]

    return render_template(
        "index.html",
        data=data,
        net=net,
        sorted_transactions=sorted_transactions,
        today=today,
    )


@app.route("/add", methods=["POST"])
def add():
    data = load_data()
    a = data["person_a"]
    b = data["person_b"]
    payer = request.form["payer"]
    receiver = b if payer == a else a
    raw_amount = int(request.form["amount"])
    amount = raw_amount // 2 if request.form.get("amount_type") == "total" else raw_amount
    note = request.form.get("note", "").strip()
    date = request.form["date"]
    data["transactions"].append({
        "payer": payer, "receiver": receiver,
        "amount": amount, "note": note, "date": date,
    })
    save_data(data)
    return redirect(url_for("index"))


@app.route("/delete/<int:index>", methods=["POST"])
def delete(index):
    data = load_data()
    data["transactions"].pop(index)
    save_data(data)
    return redirect(url_for("index"))


@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):
    data = load_data()
    if request.method == "POST":
        a = data["person_a"]
        b = data["person_b"]
        payer = request.form["payer"]
        receiver = b if payer == a else a
        data["transactions"][index].update({
            "payer": payer,
            "receiver": receiver,
            "amount": int(request.form["amount"]),
            "note": request.form.get("note", "").strip(),
            "date": request.form["date"],
        })
        save_data(data)
        return redirect(url_for("index"))
    return render_template("edit.html", data=data, index=index, t=data["transactions"][index])


@app.route("/settings", methods=["POST"])
def settings():
    data = load_data()
    new_a = request.form["person_a"].strip()
    new_b = request.form["person_b"].strip()
    old_a = data["person_a"]
    old_b = data["person_b"]
    for t in data["transactions"]:
        if t["payer"] == old_a:
            t["payer"] = new_a
        elif t["payer"] == old_b:
            t["payer"] = new_b
        if t.get("receiver") == old_a:
            t["receiver"] = new_a
        elif t.get("receiver") == old_b:
            t["receiver"] = new_b
    data["person_a"] = new_a
    data["person_b"] = new_b
    save_data(data)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
