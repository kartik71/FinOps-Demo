def run(po_data):
    print("[Jordan] Compliance check...")
    return {"compliance_ok": po_data["supplier"] != "VendorY"}