# -*- coding: utf-8 -*-

{
    'name': "Eurocomp",

    'summary': "Conector para consumir productos de EurocompCR",

    'description': """
Este módulo importa todos los productos de Eurocomp y a su vez actualiza sus respectivos stocks.
    """,

    'author': "Singulary",
    'website': "https://singulary.online",
    'license': "OPL-1",
    'category': 'Inventory',
    'version': '17.0.0.2',

    #Dependencias Python
    'external_dependencies': {
        'python': ['zeep','Pillow'],
    },

    # Modulos necesarios para que este funcione correctamente
    'depends': ['base', 'stock', 'purchase'],

    # Siempre cargados
    'data': [
        'views/res_config_settings_views.xml',
        'views/eurocomp_products_treeview.xml',
        'views/eurocomp_menus.xml',
        'views/product_supplierinfo_view.xml',
        'views/product_category_view.xml',
        'data/cron.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,  # Esto indica que es una aplicación
    'icon': 'eurocomp/static/images/odoo_icon.png',  # Ruta a tu icono
}
