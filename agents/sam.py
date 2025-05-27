import pandas as pd
def run(input_data):
    df = pd.read_csv("data.csv")
    record = df[df["Project_ID"] == input_data["project_id"]].iloc[0]
    return {
        "project_id": record["Project_ID"],
        "po_amount": record["PO_Requested"],
        "cost_center": record["Cost_Center"],
        "supplier": record["Supplier"],
        "budget_remaining": record["Budget_Remaining"]
    }