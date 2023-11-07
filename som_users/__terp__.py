# -*- coding: utf-8 -*-
{
    "name": "Representa Business layer",
    "description": """
        Module for Representa Virtual Office integration
    """,
    "version": "0-dev",
    "author": "Som Energia",
    "category": "www",
    "depends":[
        "base_extended",
        "partner_representante",
        "som_signed_documents",
        "poweremail",
    ],
    "init_xml": [],
    "demo_xml": [
        "demo/res_partner_demo.xml",
    ],
    "update_xml":[
        "wizard/wizard_create_change_password_view.xml",
        "data/email_template_data.xml",
        "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True
}
