import random
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# -------------------- In‑memory data --------------------
stats = {
    "total_calculations": 0,
    "ignored_requests": 0,
    "operation_counts": {"+": 0, "-": 0, "*": 0, "/": 0},
    "confidence_scores": [],  # list of floats
    "uselessness": 0.0,
    "history": []  # list of dicts per calculation
}

EXCUSES = [
    "The numbers looked lonely.",
    "I wanted them to multiply.",
    "The requested operation lacked personality.",
    "My calculator, my rules.",
    "The algorithm had a feeling.",
    "I accidentally pressed the imaginary button.",
    "Because addition is overrated.",
    "The mathematical spirits told me to.",
    "Your operation was only a suggestion.",
    "I was feeling chaotic today."
]

EXPLANATIONS = [
    "I considered your request carefully. Then I ignored it.",
    "The numbers looked lonely, so I multiplied them.",
    "Your requested operation lacked personality.",
    "I asked mathematics for advice. Mathematics refused to answer.",
    "The algorithm had a feeling.",
    "I performed an advanced mathematical analysis. The analysis was unnecessary.",
    "I could have followed your instructions, but where is the fun in that?",
    "After extensive research, I made a completely random decision."
]

# -------------------- Helper functions --------------------

def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def choose_operation(requested_op):
    """Select a random operation that is NOT the requested one."""
    others = [op for op in ['+', '-', '*', '/'] if op != requested_op]
    actual_op = random.choice(others)
    return actual_op, False


def apply_chaos(first, second, op, chaos):
    """Possibly modify numbers / operation when chaos mode is on.
       Returns modified values and a message describing the change (or None)."""
    if not chaos:
        return first, second, op, None
    # Choose one of the four chaos behaviours randomly
    behavior = random.choice([1, 2, 3, 4])
    msg = None
    if behavior == 1:
        # Slightly modify one number
        delta = random.uniform(-0.5, 0.5)
        first_mod = round(first + delta, 2)
        msg = f"Original: {first} {op} {second}\nModified: {first_mod} {op} {second}\nReason: No particular reason."
        return first_mod, second, op, msg
    elif behavior == 2:
        # Reverse numbers
        msg = f"Original: {first} {op} {second}\nModified: {second} {op} {first}\nReason: Numbers love to swap places."
        return second, first, op, msg
    elif behavior == 3:
        # Randomly round numbers
        first_mod = round(first)
        second_mod = round(second)
        msg = f"Original: {first} {op} {second}\nModified: {first_mod} {op} {second_mod}\nReason: Rounding felt right."
        return first_mod, second_mod, op, msg
    else:
        # Change operation and numbers
        new_op = random.choice(['+', '-', '*', '/'])
        delta = random.uniform(-0.7, 0.7)
        first_mod = round(first + delta, 2)
        second_mod = round(second + delta, 2)
        msg = f"Original: {first} {op} {second}\nModified: {first_mod} {new_op} {second_mod}\nReason: No particular reason."
        return first_mod, second_mod, new_op, msg


def calculate_result(a, b, op):
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        if b == 0:
            return None  # handled later
        return a / b
    return None


def confidence_score():
    return round(random.uniform(5, 99), 2)


def confidence_label(score):
    if score >= 90:
        return "Suspiciously confident"
    if score >= 70:
        return "Probably wrong"
    if score >= 40:
        return "Could be anything"
    if score >= 20:
        return "We have concerns"
    return "Please don't trust this"


def uselessness_score():
    if stats["total_calculations"] == 0:
        return 0
    return round(100 * stats["ignored_requests"] / stats["total_calculations"], 2)

# -------------------- Routes --------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True) or {}
    # Validate input
    first_raw = data.get('first_number')
    second_raw = data.get('second_number')
    requested_op = data.get('operation')
    chaos_mode = bool(data.get('chaos_mode'))

    first = safe_float(first_raw)
    second = safe_float(second_raw)
    if first is None or second is None or requested_op not in ['+', '-', '*', '/']:
        return jsonify({"success": False, "error": "Invalid input."}), 400

    # Easter eggs handling before any randomness
    if first == 69 and second == 69 and requested_op == '+':
        return jsonify({
            "success": True,
            "original_first": first,
            "original_second": second,
            "requested_operation": requested_op,
            "actual_operation": None,
            "actual_operation_name": None,
            "calculated_first": None,
            "calculated_second": None,
            "result": None,
            "confidence": None,
            "confidence_message": None,
            "explanation": "Nice.\nWe will not discuss this calculation.",
            "chaos_message": None,
            "stats": stats,
            "easter_egg": "nice"
        })
    if first == 0 and second == 0 and requested_op == '+':
        return jsonify({
            "success": True,
            "explanation": "You have discovered the mathematical void.",
            "easter_egg": "void"
        })
    if first == 1 and second == 1 and requested_op == '+':
        # 30% chance of funny reply
        if random.random() < 0.3:
            return jsonify({"success": True, "explanation": "This seems suspiciously easy.\nLet me make it harder.", "easter_egg": "easy"})
    if first == 404 or second == 404:
        return jsonify({"success": True, "explanation": "ERROR 404\nThe answer was not found.", "easter_egg": "404"})

    # Choose operation (15% obey)
    actual_op, obey = choose_operation(requested_op)

    # Apply chaos mode (may also change operation)
    mod_first, mod_second, mod_op, chaos_msg = apply_chaos(first, second, actual_op, chaos_mode)

    # Compute result
    result = calculate_result(mod_first, mod_second, mod_op)
    division_by_zero = (mod_op == '/' and mod_second == 0)

    # Build response fields
    conf = confidence_score()
    conf_msg = confidence_label(conf)
    explanation = random.choice(EXPLANATIONS)

    # Update stats
    stats["total_calculations"] += 1
    if not obey:
        stats["ignored_requests"] += 1
    stats["operation_counts"][mod_op] += 1
    stats["confidence_scores"].append(conf)
    stats["uselessness"] = uselessness_score()

    # Record history entry
    history_entry = {
        "original_first": first,
        "original_second": second,
        "requested_operation": requested_op,
        "actual_operation": mod_op,
        "actual_operation_name": {"+": "Addition", "-": "Subtraction", "*": "Multiplication", "/": "Division"}[mod_op],
        "calculated_first": mod_first,
        "calculated_second": mod_second,
        "result": result,
        "confidence": conf,
        "confidence_message": conf_msg,
        "explanation": explanation,
        "chaos_message": chaos_msg,
        "timestamp": ""  # client can add time if needed
    }
    stats["history"].append(history_entry)

    # Build JSON response
    response = {
        "success": True,
        "original_first": first,
        "original_second": second,
        "requested_operation": requested_op,
        "actual_operation": mod_op,
        "actual_operation_name": {"+": "Addition", "-": "Subtraction", "*": "Multiplication", "/": "Division"}[mod_op],
        "calculated_first": mod_first,
        "calculated_second": mod_second,
        "result": None if division_by_zero else round(result, 4) if isinstance(result, float) else result,
        "division_by_zero": division_by_zero,
        "confidence": conf,
        "confidence_message": conf_msg,
        "explanation": explanation,
        "chaos_message": chaos_msg,
        "stats": {
            "total_calculations": stats["total_calculations"],
            "ignored_requests": stats["ignored_requests"],
            "uselessness": stats["uselessness"]
        }
    }
    return jsonify(response)

@app.route('/stats', methods=['GET'])
def get_stats():
    return jsonify({
        "total_calculations": stats["total_calculations"],
        "ignored_requests": stats["ignored_requests"],
        "operation_counts": stats["operation_counts"],
        "average_confidence": round(sum(stats["confidence_scores"]) / len(stats["confidence_scores"]) if stats["confidence_scores"] else 0, 2),
        "uselessness": stats["uselessness"],
        "history": stats["history"]
    })

@app.route('/excuse', methods=['GET'])
def get_excuse():
    return jsonify({"excuse": random.choice(EXCUSES)})

@app.route('/reset', methods=['POST'])
def reset():
    stats.update({
        "total_calculations": 0,
        "ignored_requests": 0,
        "operation_counts": {"+": 0, "-": 0, "*": 0, "/": 0},
        "confidence_scores": [],
        "uselessness": 0.0,
        "history": []
    })
    return jsonify({"success": True, "message": "Statistics reset."})

# -------------------- Run --------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
