// Copyright (c) 2025, seemab and contributors
// For license information, please see license.txt

frappe.query_reports["Item Check with Reserve Balance"] = {
	"filters": [
		{
            "fieldname": "item_code",
            "label": __("Item Code"),
            "fieldtype": "Link",
            "options": "Item",
            "reqd": 0
        },
        {
            "fieldname": "warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "reqd": 0
        }

	]
};
