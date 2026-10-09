<<<<<<< HEAD
from flask import Flask, request, redirect, url_for
=======
from flask import Flask, request, render_template_string
>>>>>>> fa4293cf337affacd74154b0855ecae187abb407

app = Flask(__name__)

FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CentrAlign Invoice Portal</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        form { background: #f4f4f4; padding: 20px; border-radius: 8px; }
        label { display: block; margin-top: 10px; font-weight: bold; }
        input { width: 100%; padding: 8px; margin-top: 5px; box-sizing: border-box; }
        button { margin-top: 15px; padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        .success { display: none; background: #d4edda; color: #155724; padding: 15px; margin-top: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Log New Invoice</h1>
    <div id="success-banner" class="success">✅ Invoice logged successfully!</div>
    <form action="/log" method="POST">
        <label for="vendor">Vendor Name:</label>
        <input type="text" id="vendor" name="vendor" placeholder="e.g. Acme Corp" required>
        
        <label for="amount">Amount ($):</label>
        <input type="number" step="0.01" id="amount" name="amount" placeholder="e.g. 1500.00" required>
        
        <label for="due_date">Due Date:</label>
        <input type="date" id="due_date" name="due_date" required>
        
        <button type="submit">Submit Invoice</button>
    </form>
    <script>
<<<<<<< HEAD
=======
        // Check URL for success param on load
>>>>>>> fa4293cf337affacd74154b0855ecae187abb407
        const params = new URLSearchParams(window.location.search);
        if (params.get('status') === 'success') {
            document.getElementById('success-banner').style.display = 'block';
            history.replaceState({}, '', window.location.pathname);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(FORM_TEMPLATE)

@app.route('/log', methods=['POST'])
def log_invoice():
    vendor = request.form.get('vendor')
    amount = request.form.get('amount')
    due_date = request.form.get('due_date')
<<<<<<< HEAD
    return redirect(f"/?status=success&vendor={vendor}&amount={amount}&date={due_date}")

=======
    
    # In a real app, this would save to DB. Here we just confirm receipt.
    return redirect(f"/?status=success&vendor={vendor}&amount={amount}&date={due_date}")

from flask import redirect, url_for

>>>>>>> fa4293cf337affacd74154b0855ecae187abb407
if __name__ == '__main__':
    app.run(debug=True, port=5000)
