# -*- coding: utf-8 -*-
{
    "name": "Production data",
    "description": """
        Module to interact with production data
    """,
    "version": "0-dev",
    "author": "Som Energia",
    "category": "www",
    "depends":[
        "giscere_mhcil",
        "giscere_polissa",
        "som_ov_users",
        "som_ov_installations",
    ],
    "init_xml": [],
    "demo_xml": [
        'demo/giscere_mhcil_demo.xml',
    ],
    "update_xml":[
        "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True
}
