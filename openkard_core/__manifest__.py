# -*- coding: utf-8 -*-
{
    'name': 'OpenKard Core',
    'version': '10.0.0.0.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 1,
    'summary': 'open kard',
    'complexity': "easy",
    'author': 'kafkalen',
    'website': 'aws.kard.or.kr',
    'data':[
        'security/kd_core_security.xml',
        'security/ir.model.access.csv',
        'views/worker_view.xml',
        'menu/openkard_core_menu.xml',
    ],
    'depends': ['base','board', 'document', 'hr', 'web', 'website'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
