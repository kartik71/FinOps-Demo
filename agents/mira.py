def run(po_data):
    print("[Mira] Budget check...")
    return {"budget_ok": po_data["po_amount"] <= po_data["budget_remaining"]}