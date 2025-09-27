# Copyright (c) 2025, Your Company
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": "Description", "fieldname": "description", "fieldtype": "Data", "width": 200},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 120},
        {"label": "Balance Qty", "fieldname": "balance_qty", "fieldtype": "Float", "width": 120, "convertible": "qty"},
        {"label": "Reserved Stock", "fieldname": "reserved_stock", "fieldtype": "Float", "width": 120, "convertible": "qty"},
        {"label": "Net Stock", "fieldname": "net_stock", "fieldtype": "Float", "width": 120, "convertible": "qty"},
        {"label": "Selling Rate", "fieldname": "selling_rate", "fieldtype": "Currency", "width": 120},
        {"label": "Brand", "fieldname": "brand", "fieldtype": "Data", "width": 100},
    ]


def get_data(filters):
    # build where clause using optional filters (item_code, warehouse)
    conditions = ["i.disabled = 0"]
    params = {}
    if filters:
        if filters.get("item_code"):
            conditions.append("i.name = %(item)s")
            params["item"] = filters.get("item_code")
        if filters.get("warehouse"):
            conditions.append("bin.warehouse = %(warehouse)s")
            params["warehouse"] = filters.get("warehouse")

    where_clause = " AND ".join(conditions)

    data = frappe.db.sql(
        f"""
        SELECT
            i.name as item_code,
            i.description,
            i.brand,
            IFNULL(bin.actual_qty, 0) as balance_qty,
            ip.price_list_rate as selling_rate,
            bin.warehouse
        FROM `tabItem` i
        LEFT JOIN `tabBin` bin ON bin.item_code = i.name
        LEFT JOIN `tabItem Price` ip ON ip.item_code = i.name
        WHERE {where_clause}
    """,
        params,
        as_dict=True,
    )

    if not data:
        return []

    # Prepare lists for reserved qty lookup
    item_list = list({d.get("item_code") for d in data if d.get("item_code")})
    warehouse_list = list({d.get("warehouse") for d in data if d.get("warehouse")})

    reserved_map = {}
    if item_list and warehouse_list:
        try:
            from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import (
                get_sre_reserved_qty_for_items_and_warehouses,
            )

            reserved_map = get_sre_reserved_qty_for_items_and_warehouses(item_list, warehouse_list) or {}
        except Exception:
            # fallback: empty reserved map if helper not available
            reserved_map = {}

    # Fill reserved_stock and net_stock
    for d in data:
        key = (d.get("item_code"), d.get("warehouse"))
        reserved_qty = flt(reserved_map.get(key, 0.0))
        d["reserved_stock"] = reserved_qty
        d["net_stock"] = flt((d.get("balance_qty") or 0.0) - reserved_qty)

    return data
